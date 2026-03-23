"""Authentication middleware for FastMCP — API key and OAuth Bearer tokens."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Paths that never require authentication
_PUBLIC_PATHS = frozenset(
    {
        "/health",
        "/.well-known/oauth-authorization-server",
        "/oauth/register",
        "/oauth/authorize",
        "/oauth/token",
    }
)


class AuthKeyMiddleware(BaseHTTPMiddleware):
    """Require Bearer token on all endpoints except public ones.

    Supports two modes:
    - API key: ``Authorization: Bearer <auth_key>``
    - OAuth:   ``Authorization: Bearer <oauth_access_token>``

    When *oauth_validator* is provided it is called for tokens that do not
    match *auth_key*, giving OAuth tokens a chance to authenticate.
    """

    def __init__(self, app, auth_key: str, oauth_validator=None):
        super().__init__(app)
        self.auth_key = auth_key
        self.oauth_validator = oauth_validator

    async def dispatch(self, request: Request, call_next):
        if request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")

        # Check API key first
        if auth_header == f"Bearer {self.auth_key}":
            return await call_next(request)

        # Fallback to OAuth token validation
        if self.oauth_validator and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if self.oauth_validator(token):
                return await call_next(request)

        return JSONResponse({"error": "Unauthorized"}, status_code=401)


class OAuthOnlyMiddleware(BaseHTTPMiddleware):
    """Authenticate via OAuth Bearer tokens only (no API key configured)."""

    def __init__(self, app, oauth_validator):
        super().__init__(app)
        self.oauth_validator = oauth_validator

    async def dispatch(self, request: Request, call_next):
        if request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if self.oauth_validator(token):
                return await call_next(request)

        return JSONResponse({"error": "Unauthorized"}, status_code=401)
