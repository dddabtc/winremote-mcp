"""Unit tests for auth middleware."""

from __future__ import annotations

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from winremote.auth import AuthKeyMiddleware


def _make_app(auth_key: str):
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
    app.add_middleware(AuthKeyMiddleware, auth_key=auth_key)
    return app


class TestAuthMiddleware:
    def test_health_no_auth(self):
        app = _make_app("secret123")
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_unauthorized_without_key(self):
        app = _make_app("secret123")
        client = TestClient(app)
        resp = client.get("/")
        assert resp.status_code == 401

    def test_authorized_with_key(self):
        app = _make_app("secret123")
        client = TestClient(app)
        resp = client.get("/", headers={"Authorization": "Bearer secret123"})
        assert resp.status_code == 200

    def test_wrong_key(self):
        app = _make_app("secret123")
        client = TestClient(app)
        resp = client.get("/", headers={"Authorization": "Bearer wrong"})
        assert resp.status_code == 401
