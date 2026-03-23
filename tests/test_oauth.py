"""Tests for OAuth 2.0 Authorization Server and updated auth middleware."""

from __future__ import annotations

import base64
import hashlib
import secrets
import time

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from winremote.auth import AuthKeyMiddleware, OAuthOnlyMiddleware
from winremote.oauth import OAuthStore, build_oauth_routes, validate_oauth_token

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_pkce():
    """Generate a PKCE code_verifier and code_challenge (S256)."""
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def _oauth_app(store: OAuthStore, issuer: str = "http://localhost:8090", **kwargs):
    """Build a Starlette app with OAuth routes for testing."""

    async def homepage(request):
        return JSONResponse({"ok": True})

    routes_map = build_oauth_routes(store, issuer, **kwargs)
    starlette_routes = [Route("/", homepage)]
    for path, (handler, methods) in routes_map.items():
        starlette_routes.append(Route(path, handler, methods=methods))

    return Starlette(routes=starlette_routes)


# ---------------------------------------------------------------------------
# Metadata endpoint
# ---------------------------------------------------------------------------


class TestOAuthMetadata:
    def test_metadata_returns_endpoints(self):
        store = OAuthStore()
        app = _oauth_app(store)
        client = TestClient(app)
        resp = client.get("/.well-known/oauth-authorization-server")
        assert resp.status_code == 200
        data = resp.json()
        assert data["issuer"] == "http://localhost:8090"
        assert "authorization_endpoint" in data
        assert "token_endpoint" in data
        assert "registration_endpoint" in data
        assert "S256" in data["code_challenge_methods_supported"]


# ---------------------------------------------------------------------------
# Dynamic client registration
# ---------------------------------------------------------------------------


class TestOAuthRegister:
    def test_register_client(self):
        store = OAuthStore()
        app = _oauth_app(store)
        client = TestClient(app)
        resp = client.post(
            "/oauth/register",
            json={
                "redirect_uris": ["http://localhost/callback"],
                "client_name": "test-client",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "client_id" in data
        assert "client_secret" in data
        assert data["client_name"] == "test-client"

    def test_register_missing_redirect_uris(self):
        store = OAuthStore()
        app = _oauth_app(store)
        client = TestClient(app)
        resp = client.post("/oauth/register", json={})
        assert resp.status_code == 400

    def test_register_with_configured_client_id(self):
        store = OAuthStore()
        app = _oauth_app(store, configured_client_id="my-id", configured_client_secret="my-secret")
        client = TestClient(app)
        resp = client.post(
            "/oauth/register",
            json={
                "redirect_uris": ["http://localhost/callback"],
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["client_id"] == "my-id"
        assert data["client_secret"] == "my-secret"


# ---------------------------------------------------------------------------
# Full authorization code + PKCE flow
# ---------------------------------------------------------------------------


class TestOAuthFlow:
    def test_full_auth_code_flow(self):
        store = OAuthStore()
        app = _oauth_app(store)
        client = TestClient(app, follow_redirects=False)

        # 1) Register
        reg = client.post(
            "/oauth/register",
            json={
                "redirect_uris": ["http://localhost/callback"],
            },
        )
        assert reg.status_code == 201
        client_id = reg.json()["client_id"]

        # 2) Authorize with PKCE
        verifier, challenge = _make_pkce()
        auth_resp = client.get(
            "/oauth/authorize",
            params={
                "client_id": client_id,
                "redirect_uri": "http://localhost/callback",
                "response_type": "code",
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "state": "xyz",
            },
        )
        assert auth_resp.status_code == 302
        location = auth_resp.headers["location"]
        assert "code=" in location
        assert "state=xyz" in location

        # Extract code from redirect
        from urllib.parse import parse_qs, urlparse

        parsed = urlparse(location)
        code = parse_qs(parsed.query)["code"][0]

        # 3) Token exchange
        token_resp = client.post(
            "/oauth/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": verifier,
                "client_id": client_id,
                "redirect_uri": "http://localhost/callback",
            },
        )
        assert token_resp.status_code == 200
        token_data = token_resp.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "Bearer"

        # 4) Validate token
        assert validate_oauth_token(store, token_data["access_token"]) is True

    def test_authorize_requires_pkce(self):
        store = OAuthStore()
        app = _oauth_app(store)
        client = TestClient(app)
        resp = client.get(
            "/oauth/authorize",
            params={
                "client_id": "test",
                "redirect_uri": "http://localhost/callback",
                "response_type": "code",
            },
        )
        assert resp.status_code == 400

    def test_authorize_rejects_wrong_response_type(self):
        store = OAuthStore()
        app = _oauth_app(store)
        client = TestClient(app)
        resp = client.get(
            "/oauth/authorize",
            params={
                "client_id": "test",
                "redirect_uri": "http://localhost/callback",
                "response_type": "token",
                "code_challenge": "abc",
            },
        )
        assert resp.status_code == 400

    def test_token_rejects_wrong_verifier(self):
        store = OAuthStore()
        app = _oauth_app(store)
        client = TestClient(app, follow_redirects=False)

        # Register + authorize
        reg = client.post("/oauth/register", json={"redirect_uris": ["http://localhost/cb"]})
        client_id = reg.json()["client_id"]
        verifier, challenge = _make_pkce()
        auth_resp = client.get(
            "/oauth/authorize",
            params={
                "client_id": client_id,
                "redirect_uri": "http://localhost/cb",
                "response_type": "code",
                "code_challenge": challenge,
                "code_challenge_method": "S256",
            },
        )
        from urllib.parse import parse_qs, urlparse

        code = parse_qs(urlparse(auth_resp.headers["location"]).query)["code"][0]

        # Use wrong verifier
        token_resp = client.post(
            "/oauth/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": "wrong-verifier",
                "client_id": client_id,
                "redirect_uri": "http://localhost/cb",
            },
        )
        assert token_resp.status_code == 400
        assert token_resp.json()["error"] == "invalid_grant"

    def test_code_single_use(self):
        store = OAuthStore()
        app = _oauth_app(store)
        client = TestClient(app, follow_redirects=False)

        reg = client.post("/oauth/register", json={"redirect_uris": ["http://localhost/cb"]})
        client_id = reg.json()["client_id"]
        verifier, challenge = _make_pkce()
        auth_resp = client.get(
            "/oauth/authorize",
            params={
                "client_id": client_id,
                "redirect_uri": "http://localhost/cb",
                "response_type": "code",
                "code_challenge": challenge,
                "code_challenge_method": "S256",
            },
        )
        from urllib.parse import parse_qs, urlparse

        code = parse_qs(urlparse(auth_resp.headers["location"]).query)["code"][0]

        # First exchange succeeds
        resp1 = client.post(
            "/oauth/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": verifier,
                "client_id": client_id,
                "redirect_uri": "http://localhost/cb",
            },
        )
        assert resp1.status_code == 200

        # Second exchange fails (code consumed)
        resp2 = client.post(
            "/oauth/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": verifier,
                "client_id": client_id,
                "redirect_uri": "http://localhost/cb",
            },
        )
        assert resp2.status_code == 400


# ---------------------------------------------------------------------------
# Token validation
# ---------------------------------------------------------------------------


class TestTokenValidation:
    def test_invalid_token(self):
        store = OAuthStore()
        assert validate_oauth_token(store, "nonexistent") is False

    def test_expired_token(self):
        from winremote.oauth import AccessToken

        store = OAuthStore()
        store.tokens["expired"] = AccessToken(token="expired", client_id="c", expires_at=time.time() - 10)
        assert validate_oauth_token(store, "expired") is False
        assert "expired" not in store.tokens


# ---------------------------------------------------------------------------
# Auth middleware with OAuth fallback
# ---------------------------------------------------------------------------


class TestAuthMiddlewareWithOAuth:
    def _make_app(self, auth_key, oauth_validator=None):
        async def homepage(request):
            return JSONResponse({"ok": True})

        async def health(request):
            return JSONResponse({"status": "ok"})

        app = Starlette(
            routes=[
                Route("/", homepage),
                Route("/health", health),
            ]
        )
        app.add_middleware(AuthKeyMiddleware, auth_key=auth_key, oauth_validator=oauth_validator)
        return app

    def test_health_still_public(self):
        app = self._make_app("secret")
        client = TestClient(app)
        assert client.get("/health").status_code == 200

    def test_api_key_still_works(self):
        app = self._make_app("secret")
        client = TestClient(app)
        resp = client.get("/", headers={"Authorization": "Bearer secret"})
        assert resp.status_code == 200

    def test_oauth_token_accepted(self):
        app = self._make_app("secret", oauth_validator=lambda t: t == "oauth-tok")
        client = TestClient(app)
        resp = client.get("/", headers={"Authorization": "Bearer oauth-tok"})
        assert resp.status_code == 200

    def test_invalid_token_rejected(self):
        app = self._make_app("secret", oauth_validator=lambda t: False)
        client = TestClient(app)
        resp = client.get("/", headers={"Authorization": "Bearer wrong"})
        assert resp.status_code == 401


class TestOAuthOnlyMiddleware:
    def _make_app(self, oauth_validator):
        async def homepage(request):
            return JSONResponse({"ok": True})

        app = Starlette(routes=[Route("/", homepage)])
        app.add_middleware(OAuthOnlyMiddleware, oauth_validator=oauth_validator)
        return app

    def test_valid_token(self):
        app = self._make_app(lambda t: t == "good")
        client = TestClient(app)
        resp = client.get("/", headers={"Authorization": "Bearer good"})
        assert resp.status_code == 200

    def test_invalid_token(self):
        app = self._make_app(lambda t: False)
        client = TestClient(app)
        resp = client.get("/", headers={"Authorization": "Bearer bad"})
        assert resp.status_code == 401

    def test_no_token(self):
        app = self._make_app(lambda t: True)
        client = TestClient(app)
        resp = client.get("/")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Config fields
# ---------------------------------------------------------------------------


class TestConfigSSLOAuth:
    def test_ssl_fields_in_config(self):
        from winremote.config import ServerConfig

        cfg = ServerConfig()
        assert cfg.ssl_certfile is None
        assert cfg.ssl_keyfile is None

    def test_oauth_fields_in_config(self):
        from winremote.config import SecurityConfig

        cfg = SecurityConfig()
        assert cfg.oauth_client_id is None
        assert cfg.oauth_client_secret is None

    def test_load_config_with_ssl_oauth(self, tmp_path):
        from winremote.config import load_config

        toml_file = tmp_path / "winremote.toml"
        toml_file.write_text("""
[server]
ssl_certfile = "/path/to/cert.pem"
ssl_keyfile = "/path/to/key.pem"

[security]
oauth_client_id = "my-client"
oauth_client_secret = "my-secret"
""")
        cfg = load_config(toml_file)
        assert cfg.server.ssl_certfile == "/path/to/cert.pem"
        assert cfg.server.ssl_keyfile == "/path/to/key.pem"
        assert cfg.security.oauth_client_id == "my-client"
        assert cfg.security.oauth_client_secret == "my-secret"
