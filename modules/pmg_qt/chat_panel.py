"""The Chat tab of the command area (31c): a provider conversation whose tool
calls run through pymol.agent.Executor on the GUI thread."""

import asyncio
import json
import threading
import uuid
import webbrowser

from pymol import CmdException, agent, assistant, signin, snapshots
from pymol.Qt import QtCore, QtWidgets

from .icons import menu_icon

# a sign-in in the browser; that of "OpenAI" is the ChatGPT plan, next to its key
SIGN_IN = ("ChatGPT", "OpenRouter")
CLAUDE = "Claude Code"  # signs in by itself; nothing of it is kept here


class ChatPanel(QtWidgets.QWidget):
    message = QtCore.Signal(str, str)
    finished = QtCore.Signal()
    signed = QtCore.Signal(str, object, object)  # provider, credential, models

    def __init__(self, cmd, window):
        super().__init__(window)
        self.cmd = cmd
        self.window_ = window
        self.executor = agent.Executor(cmd, self._confirm, self._log)
        # the agent connector (pymol.agent_server): turns of its own
        self.connector = agent.Executor(cmd, self._confirm, self._log)
        self.conversation = None
        self.worker = None
        self.settings = QtCore.QSettings("pymolish", "pymolish-studio")
        self.credentials = {}  # provider: the tokens of its sign-in
        self.listed = {CLAUDE: signin.CLAUDE_MODELS}  # provider: (model ID, name)
        self.claude = None  # the account Claude Code is signed in to
        self.cancel = None  # an Event while a sign-in waits for the browser
        self.waiting = ""  # what that wait is for
        self.restored = False  # kept sign-ins are read when Chat is first shown

        self.history = QtWidgets.QPlainTextEdit()
        self.history.setReadOnly(True)
        self.provider = QtWidgets.QComboBox()
        self.provider.addItems([p for p in assistant.ROUTES if p != "ChatGPT"])
        chosen = self.settings.value("chat/provider", "Anthropic")
        # an entry of its own before 4.80.0
        self.provider.setCurrentText("OpenAI" if chosen == "ChatGPT" else chosen)
        self.provider.setToolTip("Provider that receives the conversation")
        self.model = QtWidgets.QComboBox(editable=True)
        self.model.lineEdit().setPlaceholderText("model ID")
        self.model.setToolTip(
            "A tool-capable model of your provider; listed after a sign-in"
        )
        self.model.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.model.setSizeAdjustPolicy(
            QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.model.setMinimumContentsLength(16)
        self.model.completer().setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        self.model.completer().setCompletionMode(
            QtWidgets.QCompleter.CompletionMode.PopupCompletion
        )
        self.key = QtWidgets.QLineEdit(placeholderText="API key (this run only)")
        self.key.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.key.setToolTip(
            "Kept in memory for this run only; empty uses"
            " ANTHROPIC_API_KEY or OPENAI_API_KEY"
        )
        self.login = QtWidgets.QPushButton()
        self.stay = QtWidgets.QCheckBox("Stay signed in")
        self.stay.setToolTip(
            "Keep the sign-in in the keychain of this computer;"
            " off: it ends with this run"
        )
        self.stay.setChecked(self.settings.value("chat/stay", False, bool))
        self.account = QtWidgets.QLabel()
        self.account.setOpenExternalLinks(True)
        self.account.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextBrowserInteraction
        )
        self.images = QtWidgets.QCheckBox("Share viewport")
        self.images.setToolTip("Let the model request a 640x480 image of the view")
        self.trusted = QtWidgets.QCheckBox("Trusted Python")
        self.trusted.setToolTip(
            "Allow proposed Python after your confirmation; it is not sandboxed"
        )
        self.unasked = QtWidgets.QCheckBox("Run without asking")
        self.unasked.setToolTip(
            "Let the model and connected agents delete, change the structure,"
            " read and write files, download and, with Trusted Python, run"
            " Python without a question; off again at the next start"
        )
        self.prompt = QtWidgets.QLineEdit(
            placeholderText="Ask about or change the session"
        )
        self.send = QtWidgets.QPushButton("Send")
        self.stop = QtWidgets.QPushButton("Stop")
        self.undo = QtWidgets.QPushButton("Undo")
        self.stop.setEnabled(False)
        self.undo.setEnabled(False)
        self.undo.setToolTip("Restore the session from before this turn's changes")

        options = QtWidgets.QHBoxLayout()
        for widget in (self.provider, self.model, self.key, self.images, self.trusted):
            options.addWidget(widget)
        access = QtWidgets.QHBoxLayout()
        for widget in (self.login, self.stay):
            access.addWidget(widget)
        access.addWidget(self.account, 1)
        access.addWidget(self.unasked)
        entry = QtWidgets.QHBoxLayout()
        for widget in (self.prompt, self.send, self.stop, self.undo):
            entry.addWidget(widget)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(options)
        layout.addLayout(access)
        layout.addWidget(self.history)
        layout.addLayout(entry)

        self.images.toggled.connect(lambda on: setattr(self.connector, "images", on))
        self.trusted.toggled.connect(lambda on: setattr(self.connector, "trusted", on))
        self.unasked.toggled.connect(lambda on: setattr(self.connector, "unasked", on))
        self.send.clicked.connect(self.start)
        self.prompt.returnPressed.connect(self.start)
        self.stop.clicked.connect(self.executor.cancel.set)
        self.undo.clicked.connect(self._undo)
        self.provider.currentTextChanged.connect(self._provider_changed)
        self.model.lineEdit().editingFinished.connect(self._reset)
        self.model.activated.connect(self._reset)
        self.login.clicked.connect(self._login_clicked)
        self.stay.toggled.connect(self._keep)
        self.message.connect(self.append)
        self.finished.connect(self._done)
        self.signed.connect(self._signed)
        self._show_access()

    def showEvent(self, event):
        if not self.restored:  # no keychain and no network before Chat is opened
            self.restored = True
            self._provider_changed(self.provider.currentText())
        super().showEvent(event)

    def changeEvent(self, event):
        # hasattr: a palette change can come before the row is built
        if event.type() == QtCore.QEvent.Type.PaletteChange and hasattr(
            self, "account"
        ):
            self._show_access()  # the icon is tinted
        super().changeEvent(event)

    def _model(self):
        """The model ID: of the listed name that is shown, else what was typed."""
        text = self.model.currentText().strip()
        index = self.model.findText(text)
        return self.model.itemData(index) or text if index >= 0 else text

    def _plan(self):
        """The sign-in the chosen provider has: for OpenAI the ChatGPT plan."""
        provider = self.provider.currentText()
        return "ChatGPT" if provider == "OpenAI" else provider

    def _route(self):
        """Who gets the conversation: the ChatGPT plan while signed in to it."""
        plan = self._plan()
        return plan if plan in self.credentials else self.provider.currentText()

    def _show_access(self):
        provider = self._plan()
        credential = self.credentials.get(provider)
        self.provider.setEnabled(not self.cancel)
        # a key only where one is taken, and not next to a sign-in that is used
        self.key.setVisible(provider not in ("OpenRouter", CLAUDE) and not credential)
        self.stay.setVisible(provider in SIGN_IN)
        self.account.setVisible(provider in (*SIGN_IN, CLAUDE))
        # no sign-out here: it would sign the user's Claude Code out everywhere
        self.login.setVisible(
            provider in SIGN_IN
            or (provider == CLAUDE and bool(self.cancel or not self.claude))
        )
        self.login.setEnabled(provider != CLAUDE or bool(signin.claude()))
        if self.cancel:
            icon, text, note = "sign in", "Cancel sign-in", self.waiting
        elif provider == CLAUDE:
            icon, text, note = "sign in", f"Continue with {provider}", ""
            if self.claude:
                who = self.claude.get("email") or "your account"
                plan = self.claude.get("subscriptionType") or self.claude.get(
                    "authMethod", ""
                )
                note = f"Using Claude Code of {who}" + (f" ({plan})" if plan else "")
            elif not signin.claude():
                note = f'<a href="{signin.CLAUDE_SETUP}">Install Claude Code</a> first'
        elif not credential:
            icon, text, note = "sign in", f"Continue with {provider}", ""
        elif provider == "ChatGPT":
            who = credential.get("email") or "your account"
            icon, text = "sign out", "Sign out"
            note = f'Using ChatGPT plan of {who} · <a href="{signin.USAGE}">Manage usage</a>'
        else:
            url = signin.manage_url(provider, credential)
            icon, text = "sign out", "Sign out"
            note = f'Using your OpenRouter credits · <a href="{url}">Manage key</a>'
        self.login.setIcon(menu_icon(icon, self.palette().buttonText().color()))
        self.login.setText(text)
        self.login.setToolTip(
            "Forget this sign-in"
            if credential
            else "Sign in to your own account in the browser; no API key"
        )
        self.account.setText(note)

    def _fill_models(self, provider):
        wanted = self.settings.value("chat/model/" + provider, "")
        self.model.clear()
        for model, name in self.listed.get(provider, ()):
            self.model.addItem(name, model)
        index = self.model.findData(wanted)
        if index >= 0:
            self.model.setCurrentIndex(index)
        elif wanted:
            self.model.setEditText(wanted)

    def _provider_changed(self, provider):
        self._reset()
        self.settings.setValue("chat/provider", provider)
        self._fill_models(self._route())
        plan = self._plan()
        if plan in SIGN_IN and plan not in self.credentials and self.stay.isChecked():
            try:
                secret = signin.kept(plan)
            except CmdException:
                secret = ""  # said when the box is ticked, not at every start
            if secret:
                self._sign_in(plan, secret)
        if provider == CLAUDE and not self.claude and signin.claude():
            self._sign_in(provider, "status")  # is Claude Code signed in already?
        self._show_access()

    def _login_clicked(self):
        provider = self._plan()
        if self.cancel:
            self.cancel.set()
        elif provider in self.credentials:
            self._sign_out(provider)
        else:
            self._sign_in(provider)

    def _open(self, url):
        self.message.emit("sign-in", "If the browser did not open, go to:\n" + url)
        webbrowser.open(url)

    def _sign_in(self, provider, secret=""):
        """In the browser, or silently from the secret the keychain kept."""
        self.cancel = cancel = threading.Event()
        self.waiting = "Checking the sign-in" if secret else "Waiting for the browser"
        stay = self.stay.isChecked()
        client = self.settings.value("chat/chatgpt_client", "")
        email = self.settings.value("chat/chatgpt_email", "")
        host = self.settings.value("chat/host_id", "")
        if not host:  # names this installation to ChatGPT; not a secret
            host = "urn:uuid:" + str(uuid.uuid4())
            self.settings.setValue("chat/host_id", host)

        def run():
            credential, found = None, []
            try:
                if provider == CLAUDE:
                    found = signin.CLAUDE_MODELS  # the same without a sign-in
                    credential = (
                        signin.claude_status()
                        if secret
                        else signin.claude_login(
                            cancel, lambda line: self.message.emit("sign-in", line)
                        )
                    )
                elif provider == "OpenRouter":
                    credential = (
                        {"access_token": secret}
                        if secret
                        else signin.openrouter(cancel, not stay, self._open)
                    )
                elif secret:
                    credential = signin.fresh(
                        {"refresh_token": secret, "client_id": client, "email": email}
                    )
                else:
                    credential = signin.chatgpt(host, client, email, cancel, self._open)
                if provider != CLAUDE:
                    found = signin.models(provider, credential["access_token"])
            except (CmdException, KeyError) as error:
                detail = getattr(error, "message", f"the answer lacked {error}")
                self.message.emit("error", f"Sign-in to {provider}: {detail}")
            self.signed.emit(provider, credential, found)

        threading.Thread(target=run, daemon=True).start()
        self._show_access()

    def _signed(self, provider, credential, found):
        """A sign-in ended with the models to choose from (credential None: it
        failed), or a token was renewed (found None)."""
        if found is not None:
            self.cancel = None
            self.listed[provider] = found
        if provider == CLAUDE:
            self.claude, credential = credential, None
        if credential:
            first = provider not in self.credentials
            self.credentials[provider] = credential
            if provider == "ChatGPT":
                self.settings.setValue("chat/chatgpt_client", credential["client_id"])
                self.settings.setValue("chat/chatgpt_email", credential["email"])
                if first and not self.settings.value("chat/welcomed", False, bool):
                    self.settings.setValue("chat/welcomed", True)
                    QtWidgets.QMessageBox.information(
                        self,
                        "You're using your ChatGPT plan",
                        "Chat requests to ChatGPT are paid from your ChatGPT plan."
                        f" Review and limit that use at {signin.USAGE}",
                    )
            if self.stay.isChecked():
                self._keep(True)
        # not after a failed sign-in: a model ID typed for the key would be lost
        if found and provider == self._plan():
            self._fill_models(self._route())
        self._show_access()

    def _keep(self, stay):
        """Write the sign-ins to the keychain, or take them out of it."""
        self.settings.setValue("chat/stay", stay)
        try:
            if stay and not self.credentials:
                signin.kept(self._plan())  # is there a keychain?
            for provider in self.credentials if stay else SIGN_IN:
                credential = self.credentials.get(provider, {})
                secret = credential.get("refresh_token") or credential.get(
                    "access_token"
                )
                signin.keep(provider, secret if stay else "")
        except CmdException as error:
            if stay:
                self.append(
                    "error", f"{error.message}\nThe sign-in lasts for this run."
                )
                self.stay.setChecked(False)

    def _sign_out(self, provider):
        credential = self.credentials.pop(provider)
        if self.stay.isChecked():
            try:
                signin.keep(provider, "")
            except CmdException as error:
                self.append("error", error.message)
        if provider == "OpenRouter":
            self.append(
                "sign-in",
                "Signed out here. The key still exists at OpenRouter; delete it"
                " at " + signin.manage_url(provider, credential),
            )
        else:

            def run():
                if not signin.revoke(credential):
                    self.message.emit(
                        "sign-in",
                        "ChatGPT did not confirm the sign-out; disconnect"
                        " pymolish in the ChatGPT settings.",
                    )

            threading.Thread(target=run, daemon=True).start()
        self._fill_models(self._route())  # of the key again, not of the plan
        self._show_access()

    def append(self, kind, text):
        self.history.appendPlainText(f"[{kind}] {text}\n")
        bar = self.history.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _log(self, text):
        # runs on the GUI thread inside Executor.call; also into the main log
        self.append("tool", text[:2000])
        print(" Chat:", text[:300])

    def _confirm(self, proposal):
        answer = QtWidgets.QMessageBox.question(
            self,
            "Allow this action?",
            json.dumps(proposal, indent=1, default=str)[:4000],
        )
        return answer == QtWidgets.QMessageBox.StandardButton.Yes

    def _reset(self):
        if self.conversation and (
            self.conversation.provider,
            self.conversation.model,
        ) != (self._route(), self._model()):
            self.conversation = None

    def _undo(self):
        self.undo.setEnabled(False)
        self.cmd.undo()

    def start(self):
        text = self.prompt.text().strip()
        if not text or self.worker is not None:
            return
        provider = self._route()
        self._reset()  # a model picked from the list without leaving the field
        try:
            if self.conversation is None:
                self.conversation = assistant.Conversation(
                    provider,
                    self._model(),
                    self.executor,
                    # mutations are serialized on the GUI thread
                    lambda *a: self.cmd._call_in_gui_thread(
                        lambda: self.executor.call(*a)
                    ),
                    self.message.emit,
                )
        except CmdException as error:
            self.append("error", str(error))
            return
        self.executor.images = self.images.isChecked()
        self.executor.trusted = self.trusted.isChecked()
        self.executor.unasked = self.unasked.isChecked()
        self.executor.begin_turn()
        self.append("you", text)
        self.prompt.clear()
        self.send.setEnabled(False)
        self.stop.setEnabled(True)
        self.undo.setEnabled(False)
        self.settings.setValue("chat/model/" + provider, self._model())
        key, conversation = self.key.text(), self.conversation
        credential = self.credentials.get(provider)

        def run():
            try:
                token = "" if provider in (*SIGN_IN, CLAUDE) else key
                if credential:
                    renewed = signin.fresh(credential)
                    if renewed is not credential:  # rotating: store the new one
                        self.signed.emit(provider, renewed, None)
                    token = renewed["access_token"]
                asyncio.run(conversation.run(text, token))
            except Exception as error:
                self.message.emit("error", str(error))
            self.finished.emit()

        self.worker = threading.Thread(target=run, daemon=True)
        self.worker.start()

    def _done(self):
        self.worker = None
        self.send.setEnabled(True)
        self.stop.setEnabled(False)
        snapshot = self.executor.snapshot
        self.undo.setEnabled(
            bool(snapshot) and bool(snapshots._undo) and snapshots._undo[-1] is snapshot
        )
