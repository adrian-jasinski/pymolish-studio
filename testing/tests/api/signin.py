"""Browser sign-in of the Chat tab (31d) with a stand-in browser and stand-in
providers: no network, no keychain, no saved settings of the user."""

import base64
import hashlib
import json
import os
import sys
import threading
import time
import types
import urllib.parse
import urllib.request

import pytest

from pymol import CmdException, cmd, signin


def browser(**answer):
    """An open_url that plays the user: it calls the redirect URI with the
    state of the request and `answer`. `.seen` is the query it was sent."""
    seen = {}

    def open_url(url):
        seen.update(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
        back = seen.get("callback_url") or seen["redirect_uri"]
        query = urllib.parse.urlencode({"state": seen["state"], **answer})
        threading.Thread(
            target=urllib.request.urlopen, args=(back + "?" + query,), daemon=True
        ).start()

    open_url.seen = seen
    return open_url


def provider(monkeypatch, answer):
    """Replace the HTTP calls; returns the list of (url, fields) sent."""
    sent = []

    def send(url, fields=None, form=False, token=""):
        sent.append((url, fields))
        return answer() if callable(answer) else answer

    monkeypatch.setattr(signin, "_send", send)
    return sent


def id_token(**claims):
    body = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode()
    return "header." + body.rstrip("=") + ".signature"


def test_openrouter_exchanges_the_code_with_its_verifier(monkeypatch):
    sent = provider(monkeypatch, {"key": "sk-or-1"})
    opened = browser(code="abc")
    assert signin.openrouter(open_url=opened) == {"access_token": "sk-or-1"}
    url, fields = sent[0]
    assert url == "https://openrouter.ai/api/v1/auth/keys" and fields["code"] == "abc"
    digest = hashlib.sha256(fields["code_verifier"].encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    assert opened.seen["code_challenge"] == challenge
    assert opened.seen["callback_url"].startswith("http://localhost:")
    assert opened.seen["expiration"] == "1-day"
    signin.openrouter(expiring=False, open_url=browser(code="abc"))


def test_openrouter_rejects_a_foreign_answer_and_can_be_cancelled(monkeypatch):
    sent = provider(monkeypatch, {"key": "sk-or-1"})
    with pytest.raises(CmdException, match="did not authorize"):
        signin.openrouter(open_url=browser(code="abc", state="of someone else"))
    cancel = threading.Event()
    cancel.set()
    with pytest.raises(CmdException, match="cancelled"):
        signin.openrouter(cancel, open_url=lambda url: None)
    assert not sent


def chatgpt_answer(opened, client="oaiapp_1", scope=signin.SCOPE, **claims):
    return lambda: {
        "access_token": "access",
        "refresh_token": "refresh",
        "expires_in": 3600,
        "scope": scope,
        "id_token": id_token(
            **{
                "nonce": opened.seen["nonce"],
                "iss": signin.AUTH,
                "aud": client,
                "email": "a@example.org",
                **claims,
            }
        ),
    }


def test_chatgpt_registers_on_the_first_sign_in(monkeypatch):
    opened = browser(code="abc", client_id="oaiapp_1")
    sent = provider(monkeypatch, chatgpt_answer(opened))
    credential = signin.chatgpt("urn:uuid:host", open_url=opened)
    assert credential["client_id"] == "oaiapp_1"
    assert credential["email"] == "a@example.org"
    assert credential["refresh_token"] == "refresh"
    assert credential["expires_at"] > time.time() + 3000
    seen = opened.seen
    assert seen["client_id"] == "dynamic_agent_client"
    assert seen["agent_name_hint"] == "pymolish"
    assert seen["ext_agent_host_id"] == "urn:uuid:host"
    assert seen["redirect_uri"].startswith("http://127.0.0.1:")
    assert seen["redirect_uri"].endswith("/auth/callback")
    assert signin.PLAN in seen["scope"]
    fields = sent[0][1]
    assert fields["client_id"] == "oaiapp_1"
    assert fields["redirect_uri"] == seen["redirect_uri"]


def test_chatgpt_returning_sign_in_reuses_the_registration(monkeypatch):
    opened = browser(code="abc")
    provider(monkeypatch, chatgpt_answer(opened))
    credential = signin.chatgpt(
        "urn:uuid:host", "oaiapp_1", "a@example.org", open_url=opened
    )
    assert credential["client_id"] == opened.seen["client_id"] == "oaiapp_1"
    assert opened.seen["login_hint"] == "a@example.org"
    assert "agent_name_hint" not in opened.seen


@pytest.mark.parametrize(
    "back, answer, message",
    [
        ({"error": "access_denied"}, {}, "did not authorize"),
        ({"code": "abc"}, {}, "no usable registration"),
        ({"code": "abc", "client_id": "oaiapp_2"}, {"client": "oaiapp_2"}, None),
        ({"code": "abc", "client_id": "oaiapp_1"}, {"nonce": "old"}, "identity"),
        ({"code": "abc", "client_id": "oaiapp_1"}, {"scope": "openid"}, "plan"),
    ],
)
def test_chatgpt_refusals(monkeypatch, back, answer, message):
    opened = browser(**back)
    provider(monkeypatch, chatgpt_answer(opened, **answer))
    if message:
        with pytest.raises(CmdException, match=message):
            signin.chatgpt("urn:uuid:host", open_url=opened)
    else:  # another registration than the one this account was signed in with
        with pytest.raises(CmdException, match="no usable registration"):
            signin.chatgpt("urn:uuid:host", "oaiapp_1", open_url=opened)


def test_fresh_renews_only_an_expiring_token(monkeypatch):
    sent = provider(monkeypatch, {"access_token": "a2", "refresh_token": "r2"})
    valid = {
        "access_token": "a1",
        "refresh_token": "r1",
        "client_id": "oaiapp_1",
        "expires_at": time.time() + 600,
    }
    key = {"access_token": "sk-or-1"}
    assert signin.fresh(valid) is valid and signin.fresh(key) is key and not sent
    renewed = signin.fresh({**valid, "expires_at": time.time() + 30})
    assert (renewed["access_token"], renewed["refresh_token"]) == ("a2", "r2")
    assert renewed["expires_at"] > time.time() + 3000
    fields = sent[0][1]
    assert fields["grant_type"] == "refresh_token" and fields["client_id"] == "oaiapp_1"


def test_models_keep_what_the_provider_lists(monkeypatch):
    listed = [
        {"slug": "m1", "display_name": "Model one", "visibility": "list"},
        {"slug": "m2", "display_name": "Hidden", "visibility": "hide"},
    ]
    provider(monkeypatch, {"models": listed, "data": [{"id": "b/x"}, {"id": "a/y"}]})
    assert signin.models("ChatGPT", "token") == [("m1", "Model one")]
    assert signin.models("OpenRouter") == [("a/y", "a/y"), ("b/x", "b/x")]


def test_keychain_round_trip_and_refusal(monkeypatch):
    store = {}
    fake = types.SimpleNamespace(
        get_password=lambda service, name: store.get((service, name)),
        set_password=lambda service, name, secret: store.update(
            {(service, name): secret}
        ),
        delete_password=lambda service, name: store.pop((service, name)),
    )
    monkeypatch.setitem(sys.modules, "keyring", fake)
    assert signin.kept("ChatGPT") == ""
    signin.keep("ChatGPT", "refresh")
    assert signin.kept("ChatGPT") == "refresh"
    signin.keep("ChatGPT", "")
    signin.keep("ChatGPT", "")  # nothing left to delete
    assert not store
    fake.get_password = lambda service, name: 1 / 0
    with pytest.raises(CmdException, match="keychain"):
        signin.kept("ChatGPT")


@pytest.fixture
def panel(monkeypatch, tmp_path):
    """A Chat panel with its own settings file and a keychain in a dict."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from pymol.Qt import QtCore, QtWidgets

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    ini = str(tmp_path / "settings.ini")
    Settings = QtCore.QSettings
    monkeypatch.setattr(
        QtCore, "QSettings", lambda *a: Settings(ini, Settings.Format.IniFormat)
    )
    keychain = {}
    monkeypatch.setattr(signin, "kept", lambda name: keychain.get(name, ""))
    monkeypatch.setattr(signin, "keep", keychain.__setitem__)
    monkeypatch.setattr(
        signin, "models", lambda name, token: [("a/one", "One"), ("b/two", "Two")]
    )
    monkeypatch.setattr(
        signin,
        "openrouter",
        lambda cancel, expiring, open_url: {"access_token": "sk-or-1"},
    )
    from pmg_qt.chat_panel import ChatPanel

    def make():
        made = ChatPanel(cmd, None)
        made.show()
        made.keychain = keychain
        made.until = lambda done: until(app, done)
        return made

    return make


def until(app, done):
    deadline = time.monotonic() + 5
    while not done():
        assert time.monotonic() < deadline
        app.processEvents()
        time.sleep(0.01)


def test_panel_signs_in_lists_models_and_stays_signed_in(panel):
    chat = panel()
    assert chat.login.isHidden() and not chat.key.isHidden()  # Anthropic: a key
    chat.provider.setCurrentText("OpenRouter")
    assert chat.key.isHidden() and not chat.login.isHidden()
    assert chat.login.text() == "Continue with OpenRouter"
    chat.stay.setChecked(True)
    chat.login.click()
    chat.until(lambda: "OpenRouter" in chat.credentials)
    assert chat.login.text() == "Sign out" and "Manage key" in chat.account.text()
    assert chat.model.currentText() == "One" and chat._model() == "a/one"
    assert chat.keychain == {"OpenRouter": "sk-or-1"}
    chat.model.setCurrentIndex(1)
    chat.settings.setValue("chat/model/OpenRouter", chat._model())  # as Send does

    again = panel()  # the next run: provider, sign-in and model come back
    again.until(lambda: "OpenRouter" in again.credentials)
    assert again.provider.currentText() == "OpenRouter" and again._model() == "b/two"

    again.login.click()
    assert again.login.text() == "Continue with OpenRouter"
    assert again.keychain == {"OpenRouter": ""} and not again.credentials


def test_panel_without_a_keychain_keeps_the_sign_in_for_this_run(panel, monkeypatch):
    def refuse(name, secret):
        raise CmdException("no keychain")

    monkeypatch.setattr(signin, "keep", refuse)
    monkeypatch.setattr(signin, "kept", lambda name: refuse(name, ""))
    chat = panel()
    chat.provider.setCurrentText("OpenRouter")
    chat.stay.setChecked(True)
    assert not chat.stay.isChecked()  # refused at once: nothing to keep yet
    chat.login.click()
    chat.until(lambda: "OpenRouter" in chat.credentials)
    assert chat.login.text() == "Sign out" and chat._model() == "a/one"


def test_panel_failed_sign_in_can_be_tried_again(panel, monkeypatch):
    def fail(cancel, expiring, open_url):
        raise CmdException("declined")

    monkeypatch.setattr(signin, "openrouter", fail)
    chat = panel()
    chat.provider.setCurrentText("OpenRouter")
    chat.login.click()
    assert chat.login.text() == "Cancel sign-in" and not chat.provider.isEnabled()
    chat.until(lambda: chat.cancel is None)
    assert chat.login.text() == "Continue with OpenRouter" and chat.provider.isEnabled()
    assert "declined" in chat.history.toPlainText()


def test_panel_chatgpt_keeps_the_refresh_token_and_welcomes_once(panel, monkeypatch):
    from pymol.Qt import QtWidgets

    welcomed, asked, renewed = [], [], []
    monkeypatch.setattr(
        QtWidgets.QMessageBox, "information", lambda *a: welcomed.append(a[1])
    )
    tokens = {
        "access_token": "a1",
        "refresh_token": "r1",
        "expires_at": time.time() + 3600,
        "client_id": "oaiapp_1",
        "email": "a@example.org",
    }

    def chatgpt(host, client, email, cancel, open_url):
        asked.append((host, client))
        return tokens

    def fresh(credential):
        renewed.append(credential)
        return {**tokens, "access_token": "a2", "refresh_token": "r2"}

    monkeypatch.setattr(signin, "chatgpt", chatgpt)
    chat = panel()
    chat.provider.setCurrentText("ChatGPT")
    chat.stay.setChecked(True)
    chat.login.click()
    chat.until(lambda: "ChatGPT" in chat.credentials)
    assert welcomed == ["You're using your ChatGPT plan"]
    assert (
        "a@example.org" in chat.account.text() and "Manage usage" in chat.account.text()
    )
    assert asked[0][0].startswith("urn:uuid:") and asked[0][1] == ""  # a first sign-in
    assert chat.keychain == {"ChatGPT": "r1"}

    monkeypatch.setattr(signin, "fresh", fresh)
    again = panel()  # the next run renews from the kept token, without the browser
    again.until(lambda: "ChatGPT" in again.credentials)
    assert renewed[0]["refresh_token"] == "r1" and renewed[0]["client_id"] == "oaiapp_1"
    assert again.keychain == {"ChatGPT": "r2"}  # the rotated token replaces the old
    assert len(asked) == 1 and len(welcomed) == 1
