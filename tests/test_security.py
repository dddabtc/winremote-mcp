"""Unit tests for IP allowlist middleware and parsing."""

from __future__ import annotations

import ipaddress

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from winremote.security import IPAllowlistMiddleware, parse_ip_allowlist


def _make_app(allowlist: list[str]):
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
    app.add_middleware(IPAllowlistMiddleware, allowlist=parse_ip_allowlist(allowlist))
    return app


class TestParseIPAllowlist:
    def test_parses_ip_and_cidr(self):
        parsed = parse_ip_allowlist(["127.0.0.1", "10.0.0.0/24"])
        assert ipaddress.ip_address("127.0.0.1") in parsed[0]
        assert ipaddress.ip_address("10.0.0.42") in parsed[1]

    def test_invalid_entries_raise(self):
        try:
            parse_ip_allowlist(["bad-ip"])
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "bad-ip" in str(exc)


class TestIPAllowlistMiddleware:
    def test_health_is_public(self):
        app = _make_app(["127.0.0.1/32"])
        client = TestClient(app, client=("10.1.2.3", 1234))
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_allowed_ip_passes(self):
        app = _make_app(["127.0.0.1/32"])
        client = TestClient(app, client=("127.0.0.1", 1234))
        resp = client.get("/")
        assert resp.status_code == 200

    def test_blocked_ip_returns_403(self):
        app = _make_app(["127.0.0.1/32"])
        client = TestClient(app, client=("10.1.2.3", 1234))
        resp = client.get("/")
        assert resp.status_code == 403
