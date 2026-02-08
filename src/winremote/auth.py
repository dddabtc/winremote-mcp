"""API key authentication middleware for FastMCP."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class AuthKeyMiddleware(BaseHTTPMiddleware):
    """Require Bearer token on all endpoints except /health."""

    def __init__(self, app, auth_key: str):
        super().__init__(app)
        self.auth_key = auth_key

    async def dispatch(self, request: Request, call_next):
        # /health is always public
        if request.url.path == "/health":
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if auth_header == f"Bearer {self.auth_key}":
            return await call_next(request)

        return JSONResponse({"error": "Unauthorized"}, status_code=401)
