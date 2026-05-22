"""Regression tests for security hardening controls."""

from __future__ import annotations

import base64
import hashlib
import secrets
from urllib.parse import parse_qs, urlparse

import pytest
from click.testing import CliRunner
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from winremote.__main__ import _open_validated_fetch_url, cli
from winremote.oauth import OAuthStore, build_oauth_routes
from winremote.security import validate_fetch_url
from winremote.tiers import resolve_enabled_tools


def _make_pkce():
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def _oauth_app(store: OAuthStore, **kwargs):
    async def homepage(request):
        return JSONResponse({"ok": True})

    routes_map = build_oauth_routes(store, "http://localhost:8090", **kwargs)
    routes = [Route("/", homepage)]
    for path, (handler, methods) in routes_map.items():
        routes.append(Route(path, handler, methods=methods))
    return Starlette(routes=routes)


class TestOAuthHardening:
    def test_configured_oauth_registration_does_not_leak_client_secret(self):
        store = OAuthStore()
        app = _oauth_app(store, configured_client_id="my-id", configured_client_secret="my-secret")
        client = TestClient(app)

        resp = client.post("/oauth/register", json={"redirect_uris": ["http://localhost/callback"]})

        assert resp.status_code in {400, 403, 404}
        assert "my-secret" not in resp.text

    def test_dynamic_oauth_without_configured_client_is_disabled(self):
        store = OAuthStore()
        app = _oauth_app(store)
        client = TestClient(app)

        resp = client.post("/oauth/register", json={"redirect_uris": ["http://localhost/callback"]})

        assert resp.status_code in {400, 403, 404}
        assert not store.clients

    def test_oauth_token_requires_configured_client_secret(self):
        store = OAuthStore()
        app = _oauth_app(store, configured_client_id="trusted", configured_client_secret="secret")
        client = TestClient(app, follow_redirects=False)
        verifier, challenge = _make_pkce()

        auth_resp = client.get(
            "/oauth/authorize",
            params={
                "client_id": "trusted",
                "redirect_uri": "http://localhost/callback",
                "response_type": "code",
                "code_challenge": challenge,
                "code_challenge_method": "S256",
            },
        )
        assert auth_resp.status_code == 302
        code = parse_qs(urlparse(auth_resp.headers["location"]).query)["code"][0]

        token_resp = client.post(
            "/oauth/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": verifier,
                "client_id": "trusted",
                "redirect_uri": "http://localhost/callback",
            },
        )

        assert token_resp.status_code == 401
        assert token_resp.json()["error"] == "invalid_client"


class TestNetworkFetchHardening:
    def test_validate_fetch_url_rejects_file_scheme(self):
        allowed, reason = validate_fetch_url("file:///etc/passwd")
        assert allowed is False
        assert "scheme" in reason.lower()

    def test_validate_fetch_url_rejects_loopback_http_by_default(self):
        allowed, reason = validate_fetch_url("http://127.0.0.1:8090/health")
        assert allowed is False
        assert "private" in reason.lower() or "loopback" in reason.lower()

    def test_validate_fetch_url_allows_public_https(self, monkeypatch):
        import socket

        monkeypatch.setattr(
            socket,
            "getaddrinfo",
            lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))],
        )
        allowed, reason = validate_fetch_url("https://example.com/index.html")
        assert allowed is True
        assert reason == ""

    def test_open_validated_fetch_url_blocks_redirect_to_loopback(self, monkeypatch):
        import socket
        import urllib.error
        import urllib.request

        monkeypatch.setattr(
            socket,
            "getaddrinfo",
            lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))],
        )

        class FakeOpener:
            def open(self, req, timeout=15):
                raise urllib.error.HTTPError(
                    "http://127.0.0.1/health",
                    302,
                    "Found",
                    {"Location": "http://127.0.0.1/health"},
                    None,
                )

        monkeypatch.setattr(urllib.request, "build_opener", lambda *args, **kwargs: FakeOpener())

        with pytest.raises(ValueError, match="redirect"):
            _open_validated_fetch_url("https://example.com/redirect")


class TestToolTierHardening:
    def test_app_launch_is_not_enabled_by_default(self):
        enabled = resolve_enabled_tools()
        assert "App" not in enabled
        assert "App" in resolve_enabled_tools(enable_tier3=True)

    def test_play_sound_is_not_enabled_by_default(self):
        enabled = resolve_enabled_tools()
        assert "PlaySound" not in enabled
        assert "PlaySound" in resolve_enabled_tools(enable_tier3=True)


class TestRemoteBindHardening:
    def test_debug_flag_is_accepted_and_enables_debug_logging(self, monkeypatch):
        from winremote import __main__ as main_module

        run_kwargs = {}
        monkeypatch.setattr(main_module.mcp, "run", lambda **kwargs: run_kwargs.update(kwargs))

        runner = CliRunner()
        result = runner.invoke(cli, ["--debug"])

        assert result.exit_code == 0
        assert run_kwargs["uvicorn_args"]["log_level"] == "debug"

    def test_non_loopback_http_requires_auth_or_explicit_override(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--host", "0.0.0.0", "--port", "8090"])

        assert result.exit_code != 0
        assert "--auth-key" in result.output
        assert "--allow-insecure-remote" in result.output

    def test_non_loopback_http_allows_configured_oauth(self, monkeypatch):
        from winremote import __main__ as main_module

        monkeypatch.setattr(main_module.mcp, "run", lambda **kwargs: None)
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--host",
                "0.0.0.0",
                "--port",
                "8090",
                "--oauth-client-id",
                "trusted",
                "--oauth-client-secret",
                "secret",
            ],
        )

        assert result.exit_code == 0


class TestConfigHardening:
    def test_allow_insecure_remote_requires_toml_boolean(self, tmp_path):
        from winremote.config import load_config

        config_path = tmp_path / "winremote.toml"
        config_path.write_text('[server]\nallow_insecure_remote = "false"\n', encoding="utf-8")

        with pytest.raises(ValueError, match="server.allow_insecure_remote"):
            load_config(config_path)
