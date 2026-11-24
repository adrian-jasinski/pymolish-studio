"""Browser sign-in for the Chat tab (31d): OpenRouter, and "Sign in with
ChatGPT" for open-source apps. Both are an authorization code with PKCE that
comes back to a listener on this computer. Standard library only, no Qt.

OpenRouter: https://openrouter.ai/docs/guides/overview/auth/oauth
ChatGPT: https://developers.openai.com/siwc/token-sharing-open-source
"""

import base64
import hashlib
import json
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from pymol import CmdException

OPENROUTER = "https://openrouter.ai"
AUTH = "https://auth.openai.com"
RESOURCE = "https://api.openai.com/v1"
PLAN = "chatgpt.tokens.use.direct"
SCOPE = "openid profile email offline_access resource.invoke " + PLAN
USAGE = "https://chatgpt.com/settings/usage"
PAGE = b"<html><body><h3>pymolish</h3>Signed in. Close this page.</body></html>"


def _send(url, fields=None, form=False, token=""):
    """JSON from a GET, or from a POST of fields as JSON or as a form."""
    host = urllib.parse.urlsplit(url).netloc
    headers = {"User-Agent": "pymolish"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = None
    if fields is not None:
        encode = urllib.parse.urlencode if form else json.dumps
        data = encode(fields).encode()
        headers["Content-Type"] = (
            "application/x-www-form-urlencoded" if form else "application/json"
        )
    try:
        request = urllib.request.Request(url, data, headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read() or b"null")
    except urllib.error.HTTPError as error:
        body = error.read(2000).decode(errors="replace")
        raise CmdException(f"{host} answered {error.code}: {body}") from None
    except (OSError, ValueError) as error:
        raise CmdException(f"No usable answer from {host}: {error}") from None


def _pkce():
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode()).digest()
    return verifier, base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def _callback(url_for, path, host, port, cancel, open_url, wait=300):
    """Open the browser at url_for(redirect URI) and wait for it to come
    back; returns the query of that request and the redirect URI."""
    got = {}

    class Handler(BaseHTTPRequestHandler):
        timeout = 5  # a browser that connects ahead and sends nothing

        def do_GET(self):
            parts = urllib.parse.urlsplit(self.path)
            if parts.path != path:
                return self.send_error(404)
            got.update(urllib.parse.parse_qsl(parts.query))
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(PAGE)

        def log_message(self, format, *args):
            pass  # the code stays out of the terminal

    try:
        server = HTTPServer(("127.0.0.1", port), Handler)
    except OSError:  # the preferred port is taken
        server = HTTPServer(("127.0.0.1", 0), Handler)
    with server:
        server.timeout = 0.2
        uri = f"http://{host}:{server.server_port}{path}"
        open_url(url_for(uri))
        deadline = time.monotonic() + wait
        while not got:
            if (cancel and cancel.is_set()) or time.monotonic() > deadline:
                raise CmdException("Sign-in was cancelled")
            server.handle_request()
    return got, uri


def openrouter(cancel=None, expiring=True, open_url=webbrowser.open):
    """A key of the user's OpenRouter account, made for this sign-in."""
    verifier, challenge = _pkce()
    state = secrets.token_urlsafe(16)
    query = {
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "key_label": "pymolish",
        "state": state,
    }
    if expiring:
        query["expiration"] = "1-day"  # a key nobody keeps should not live on
    got, _ = _callback(
        lambda uri: (
            f"{OPENROUTER}/auth?"
            + urllib.parse.urlencode({"callback_url": uri, **query})
        ),
        "/callback",
        "localhost",
        0,
        cancel,
        open_url,
    )
    if got.get("state") != state or "code" not in got:
        raise CmdException("OpenRouter did not authorize the sign-in")
    answer = _send(
        f"{OPENROUTER}/api/v1/auth/keys",
        {
            "code": got["code"],
            "code_verifier": verifier,
            "code_challenge_method": "S256",
        },
    )
    return {"access_token": answer["key"]}


def _claims(token):
    """The payload of a JWT, unverified."""
    try:
        payload = token.split(".")[1]
        return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    except (IndexError, ValueError):
        return {}


def chatgpt(host_id, client_id="", email="", cancel=None, open_url=webbrowser.open):
    """Tokens that spend the user's ChatGPT plan. Without a client_id from an
    earlier sign-in, the user registers pymolish in the browser first."""
    verifier, challenge = _pkce()
    state, nonce = secrets.token_urlsafe(16), secrets.token_urlsafe(16)
    query = {
        "client_id": client_id or "dynamic_agent_client",
        "ext_agent_host_id": host_id,
        "response_type": "code",
        "scope": SCOPE,
        "resource": RESOURCE,
        "state": state,
        "nonce": nonce,
        "code_challenge_method": "S256",
        "code_challenge": challenge,
    }
    if not client_id:
        query["agent_name_hint"] = "pymolish"
    elif email:
        query["login_hint"] = email
    got, uri = _callback(
        lambda uri: (
            f"{AUTH}/api/accounts/authorize?"
            + urllib.parse.urlencode({**query, "redirect_uri": uri})
        ),
        "/auth/callback",
        "127.0.0.1",
        1455,  # the port of OpenAI's example; any other is allowed later
        cancel,
        open_url,
    )
    if got.get("state") != state:
        raise CmdException("The sign-in answer does not belong to this attempt")
    if "code" not in got:
        raise CmdException("ChatGPT did not authorize: " + got.get("error", "no code"))
    issued = got.get("client_id", client_id)
    if issued in ("", "dynamic_agent_client") or (client_id and issued != client_id):
        raise CmdException("ChatGPT returned no usable registration of pymolish")
    answer = _send(
        f"{AUTH}/api/accounts/oauth/token",
        {
            "grant_type": "authorization_code",
            "client_id": issued,
            "code": got["code"],
            "code_verifier": verifier,
            "redirect_uri": uri,
            "resource": RESOURCE,
        },
        form=True,
    )
    # ponytail: the signature of the ID token is not checked. It came straight
    # from the token endpoint over TLS (OpenID Connect Core 3.1.3.7 allows
    # that) and is used for the e-mail shown only. Check it against the JWKS
    # before anything trusts the identity.
    claims = _claims(answer.get("id_token", ""))
    audience = claims.get("aud")
    if (
        claims.get("nonce") != nonce
        or claims.get("iss") != AUTH
        or issued not in (audience if isinstance(audience, list) else [audience])
    ):
        raise CmdException("The identity ChatGPT returned does not match this sign-in")
    if PLAN not in answer.get("scope", "").split():
        raise CmdException(
            "Use of your ChatGPT plan was not allowed for pymolish. Sign in"
            " again and allow it, or use an API key."
        )
    return {
        "access_token": answer["access_token"],
        "refresh_token": answer["refresh_token"],
        "expires_at": time.time() + answer.get("expires_in", 3600),
        "client_id": issued,
        "email": claims.get("email", email),
    }


def fresh(credential):
    """The credential, renewed when its access token is about to expire."""
    if (
        "refresh_token" not in credential
        or credential.get("expires_at", 0) - 60 > time.time()
    ):
        return credential
    answer = _send(
        f"{AUTH}/api/accounts/oauth/token",
        {
            "grant_type": "refresh_token",
            "client_id": credential["client_id"],
            "refresh_token": credential["refresh_token"],
            "resource": RESOURCE,
        },
        form=True,
    )
    return {
        **credential,
        "access_token": answer["access_token"],
        # rotating: the old one stops working
        "refresh_token": answer.get("refresh_token", credential["refresh_token"]),
        "expires_at": time.time() + answer.get("expires_in", 3600),
    }


def revoke(credential):
    """End the renewable ChatGPT session; False when that was not confirmed."""
    try:
        found = _send(AUTH + "/.well-known/openid-configuration")
        _send(
            found["revocation_endpoint"],
            {
                "token": credential["refresh_token"],
                "token_type_hint": "refresh_token",
                "client_id": credential["client_id"],
            },
            form=True,
        )
        return True
    except (CmdException, KeyError):
        return False


def models(provider, token=""):
    """(model ID, name to show) of the models a signed-in user can choose."""
    if provider == "OpenRouter":
        found = _send(OPENROUTER + "/api/v1/models?supported_parameters=tools")
        return sorted((m["id"], m["id"]) for m in found["data"])
    found = _send(RESOURCE + "/models", token=token)
    return [
        (m["slug"], m.get("display_name") or m["slug"])
        for m in found["models"]
        if m.get("visibility") == "list"
    ]


def manage_url(provider, credential):
    """Where the user reviews what this sign-in spends, or removes it."""
    if provider == "OpenRouter":
        digest = hashlib.sha256(credential["access_token"].encode()).hexdigest()
        return f"{OPENROUTER}/keys/{digest}"
    return USAGE


# ponytail: one keychain entry per provider holds the OpenRouter key or the
# ChatGPT refresh token only (Windows keeps 1280 characters per entry). A
# second running pymolish renews the same token and signs the first one out.
# Keep the access token in an entry of its own if restarts must not renew.
def kept(provider):
    """The secret "Stay signed in" kept for this provider, or ""."""
    return _keychain(lambda k: k.get_password("pymolish", provider) or "")


def keep(provider, secret):
    """Keep the secret in the keychain of this computer; "" removes it."""

    def write(k):
        if secret:
            k.set_password("pymolish", provider, secret)
        elif k.get_password("pymolish", provider):
            k.delete_password("pymolish", provider)

    _keychain(write)


def _keychain(action):
    try:
        import keyring
    except ImportError:
        raise CmdException(
            "Staying signed in needs the keyring package: pip install 'pymolish[ai]'"
        ) from None
    try:
        return action(keyring)
    except Exception as error:  # no keychain service, locked, entry too long
        raise CmdException(f"The keychain of this computer refused: {error}") from None
