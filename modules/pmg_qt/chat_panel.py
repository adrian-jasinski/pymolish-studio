"""The Chat tab of the command area (31c): a provider conversation whose tool
calls run through pymol.agent.Executor on the GUI thread."""

import asyncio
import json
import threading

from pymol import CmdException, agent, assistant, snapshots
from pymol.Qt import QtCore, QtWidgets


class ChatPanel(QtWidgets.QWidget):
    message = QtCore.Signal(str, str)
    finished = QtCore.Signal()

    def __init__(self, cmd, window):
        super().__init__(window)
        self.cmd = cmd
        self.window_ = window
        self.executor = agent.Executor(cmd, self._confirm, self._log)
        # the agent connector (pymol.agent_server): turns of its own
        self.connector = agent.Executor(cmd, self._confirm, self._log)
        self.conversation = None
        self.worker = None

        self.history = QtWidgets.QPlainTextEdit()
        self.history.setReadOnly(True)
        self.provider = QtWidgets.QComboBox()
        self.provider.addItems(["Anthropic", "OpenAI"])
        self.provider.setToolTip("Provider that receives the conversation")
        self.model = QtWidgets.QLineEdit(placeholderText="model ID")
        self.model.setToolTip("A tool-capable model ID from your provider")
        self.key = QtWidgets.QLineEdit(placeholderText="API key (this run only)")
        self.key.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.key.setToolTip(
            "Kept in memory for this run only; empty uses"
            " ANTHROPIC_API_KEY or OPENAI_API_KEY"
        )
        self.images = QtWidgets.QCheckBox("Share viewport")
        self.images.setToolTip("Let the model request a 640x480 image of the view")
        self.trusted = QtWidgets.QCheckBox("Trusted Python")
        self.trusted.setToolTip(
            "Allow proposed Python after your confirmation; it is not sandboxed"
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
        entry = QtWidgets.QHBoxLayout()
        for widget in (self.prompt, self.send, self.stop, self.undo):
            entry.addWidget(widget)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(options)
        layout.addWidget(self.history)
        layout.addLayout(entry)

        self.images.toggled.connect(lambda on: setattr(self.connector, "images", on))
        self.trusted.toggled.connect(lambda on: setattr(self.connector, "trusted", on))
        self.send.clicked.connect(self.start)
        self.prompt.returnPressed.connect(self.start)
        self.stop.clicked.connect(self.executor.cancel.set)
        self.undo.clicked.connect(self._undo)
        self.provider.currentTextChanged.connect(self._reset)
        self.model.editingFinished.connect(self._reset)
        self.message.connect(self.append)
        self.finished.connect(self._done)

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
        ) != (self.provider.currentText(), self.model.text().strip()):
            self.conversation = None

    def _undo(self):
        self.undo.setEnabled(False)
        self.cmd.undo()

    def start(self):
        text = self.prompt.text().strip()
        if not text or self.worker is not None:
            return
        try:
            if self.conversation is None:
                self.conversation = assistant.Conversation(
                    self.provider.currentText(),
                    self.model.text(),
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
        self.executor.begin_turn()
        self.append("you", text)
        self.prompt.clear()
        self.send.setEnabled(False)
        self.stop.setEnabled(True)
        self.undo.setEnabled(False)
        key, conversation = self.key.text(), self.conversation

        def run():
            try:
                asyncio.run(conversation.run(text, key))
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
