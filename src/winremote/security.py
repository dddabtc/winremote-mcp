"""Security helpers: IP allowlist parsing + middleware."""

from __future__ import annotations

import ipaddress

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


def parse_ip_allowlist(raw_entries: list[str]) -> list[ipaddress._BaseNetwork]:
    """Parse allowlist entries of single IPs and CIDR ranges."""
    parsed: list[ipaddress._BaseNetwork] = []
    errors: list[str] = []

    for entry in raw_entries:
        value = entry.strip()
        if not value:
            continue
        try:
            if "/" in value:
                parsed.append(ipaddress.ip_network(value, strict=False))
            else:
                ip_obj = ipaddress.ip_address(value)
                suffix = "/32" if ip_obj.version == 4 else "/128"
                parsed.append(ipaddress.ip_network(f"{ip_obj}{suffix}", strict=False))
        except ValueError as exc:
            errors.append(f"{entry}: {exc}")

    if errors:
        raise ValueError("Invalid IP allowlist entries: " + "; ".join(errors))

    return parsed


class IPAllowlistMiddleware(BaseHTTPMiddleware):
    """Restrict access to configured client IP networks."""

    def __init__(self, app, allowlist: list[ipaddress._BaseNetwork]):
        super().__init__(app)
        self.allowlist = allowlist

    async def dispatch(self, request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        client = request.client
        if client is None:
            return JSONResponse({"error": "Forbidden: missing client address"}, status_code=403)

        try:
            client_ip = ipaddress.ip_address(client.host)
        except ValueError:
            return JSONResponse({"error": f"Forbidden: invalid client address {client.host}"}, status_code=403)

        if not any(client_ip in net for net in self.allowlist):
            return JSONResponse(
                {
                    "error": f"Forbidden: client IP {client_ip} is not in allowlist",
                },
                status_code=403,
            )

        return await call_next(request)
