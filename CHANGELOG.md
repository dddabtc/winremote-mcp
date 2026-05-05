# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.21] - 2026-05-05

### Docs

- Add a README `What's New in v0.4.20` summary for the security hardening release.
- Keep only the latest three `What's New` sections in README and point older release notes to the full changelog.

## [0.4.20] - 2026-05-04

### Security

- Refuse non-loopback HTTP binds without `--auth-key` unless `--allow-insecure-remote` is explicitly set.
- Disable dynamic OAuth client registration; OAuth now requires pre-provisioned confidential clients with a configured client ID and secret.
- Require OAuth PKCE `S256` and loopback redirect URIs.
- Harden `Scrape` and `PlaySound` URL fetching against SSRF by blocking private, loopback, link-local, multicast, reserved, and unspecified targets and adding response size limits.
- Move `App` and `PlaySound` to Tier 3 because they can start programs or fetch server-side resources.

### CI

- Raise minimum dependency versions for FastMCP, Pillow, Authlib, cryptography, python-multipart, pytest, and Pygments to versions without currently known advisories in CI.
- Add CI security scans for Bandit, pip-audit, and zizmor.
- Restrict GitHub Actions workflow permissions to read-only contents unless PyPI OIDC publishing requires `id-token: write`.

## [0.4.19] - 2026-05-01

### Docs

- Added Hermes integration documentation for native MCP server setup.
- Linked README integration section to the repo's Hermes, OpenClaw, Claude, and Cursor guide directories.

## [0.4.18] - 2026-04-13

### Security

- Fixed command injection vulnerabilities in shell execution paths
- Hardened input handling across desktop and shell tools
- Fixed logic bugs in tool parameter validation

### Docs

- Added AI vision guide for non-standard UI frameworks (Flutter/Electron/Qt)
- Fixed formatting issues in SECURITY.md

## [0.4.17] - 2026-04-11

### Fixed

- Fixed PlaySound tool not working through MCP interface

## [0.4.16] - 2026-04-11

### Added

- Added PlaySound tool (Tier 1) for audio playback on Windows host
- PlaySound supports both local file paths and URLs
- Added unit tests for PlaySound tool

### Fixed

- Fixed syntax errors in PlaySound tool definition
- Fixed ruff lint issues (E701, F541)

## [0.4.15] - 2026-04-03

### Fixed

- Patched FastMCP streamable HTTP session handling so session-less `GET /mcp` probes with `Accept: text/event-stream` return HTTP 405 instead of HTTP 400.

## [0.4.14] - 2026-04-03

### Fixed

- Return HTTP 405 for session-less `GET /mcp` probe requests with SSE accept headers, improving compatibility with MCP inspector/probe clients before initialization.

## [0.4.13] - 2026-04-03

### Fixed

- Suppress FastMCP startup banner by default in inspection/catalog environments via `FASTMCP_SHOW_SERVER_BANNER=false`, avoiding non-protocol stderr noise during Glama inspection.

## [0.4.12] - 2026-04-03

### Fixed

- Added `WINREMOTE_QUIET=1` mode to suppress startup banner/noisy inspection output for catalog and proxy-based inspection environments such as Glama.
- Added minimal Dockerfile for Glama inspection/deploy flows.

## [0.4.11] - 2026-04-03

### Fixed

- Made the CLI import-safe on non-Windows/Linux CI hosts by deferring `pyautogui` failures until desktop tools are actually used. This allows `pip install winremote-mcp` and `winremote-mcp --help` to succeed in headless environments used by package checkers.
- Added a `winremote` console-script alias alongside `winremote-mcp`.
- Corrected README command examples to use the shipped `winremote-mcp` executable.

## [0.4.10] - 2026-03-23

### Fixed

- Restored full OpenClaw integration guide in README (setup, HTTPS, OAuth, config reference).

## [0.4.9] - 2026-03-23

### Added

- **HTTPS/TLS support**: `--ssl-certfile` and `--ssl-keyfile` CLI options (and `server.ssl_certfile` / `server.ssl_keyfile` in `winremote.toml`) to run the server over HTTPS. When both are provided, the startup banner shows `[https ON]`. Generate a self-signed cert with: `openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes`.
- **OAuth 2.0 Authorization Server** (closes #33): Full MCP-compatible OAuth 2.0 AS with:
  - `GET /.well-known/oauth-authorization-server` — RFC 8414 server metadata
  - `POST /oauth/register` — RFC 7591 dynamic client registration
  - `GET /oauth/authorize` — Authorization Code flow with PKCE (RFC 7636)
  - `POST /oauth/token` — token exchange with PKCE verification
  - `--oauth-client-id` and `--oauth-client-secret` CLI options (and `security.oauth_client_id` / `security.oauth_client_secret` in config) to whitelist a specific client
  - Compatible with Claude Desktop and other MCP clients that require OAuth or HTTPS
  - Startup banner shows `[oauth ON]` when OAuth is configured
  - Existing `--auth-key` Bearer token auth continues to work alongside OAuth

## [0.4.8] - 2026-02-21

### Fixed

- Added compatibility for **fastmcp 3.x** tool internals while preserving **2.x** support.
- Reworked tool wrapping/filtering logic to avoid direct dependency on `_tool_manager._tools`.
- Resolved runtime failure reported in issue #29:
  `AttributeError: 'FastMCP' object has no attribute '_tool_manager'`.

## [0.3.0] - 2026-02-08

### Added

- **API Key Authentication**: `--auth-key` CLI option (or `WINREMOTE_AUTH_KEY` env var) to require Bearer token on all MCP requests. `/health` remains public.
- **Multi-Monitor Snapshot**: New `monitor` parameter (0=all, 1/2/3=specific) with `all_screens=True` support.
- **Registry Tools**: `RegRead` and `RegWrite` tools for Windows Registry operations (HKLM, HKCU, HKCR, HKU, HKCC).
- **Service Management**: `ServiceList`, `ServiceStart`, `ServiceStop` tools via PowerShell.
- **Scheduled Task Management**: `TaskList`, `TaskCreate`, `TaskDelete` tools via schtasks/PowerShell.
- **Network Tools**: `Ping` (subprocess), `PortCheck` (socket), `NetConnections` (psutil).
- **Binary File Transfer**: `FileDownload` (returns base64) and `FileUpload` (writes from base64).
- **Windows Event Log**: `EventLog` tool to read System/Application/Security logs with level filtering.
- **OCR Tool**: `OCR(region, lang)` extracts text from screen regions. Uses pytesseract if available, falls back to Windows built-in OCR engine. `pytesseract` is an optional dependency (`pip install winremote-mcp[ocr]`).
- **Screen Recording**: `ScreenRecord(duration, fps, region)` captures screen activity as animated GIF. Default 3s at 5fps, max 10s. Returns base64 GIF in ImageContent.
- **Annotated Snapshot**: `AnnotatedSnapshot(max_elements)` takes a screenshot and overlays numbered red labels on interactive UI elements. Helps AI agents visually identify click targets.

## [0.2.0] - 2025-02-08

### Added

- Desktop control: screenshot (JPEG compressed), click, type, scroll, keyboard shortcuts
- Window management: focus by fuzzy title match, minimize-all (Win+D), launch/resize apps
- Remote management: PowerShell shell with optional `cwd`, clipboard read/write, process list/kill, system info, notifications, lock screen
- File operations: read, write, list, search
- Web scraping: fetch URL content via `Scrape` tool
- Snapshot compression: configurable `quality` (default 75) and `max_width` (default 1920) for JPEG output
- Health endpoint: `GET /health` returns `{"status":"ok","version":"0.2.0"}`
- Hot reload: `--reload` flag for development
- Auto-start: `winremote install` / `winremote uninstall` for Windows scheduled tasks
- Transport options: stdio (default) and streamable-http
- Better pywin32 error reporting with explicit messages

[0.3.0]: https://github.com/dddabtc/winremote-mcp/releases/tag/v0.3.0
[0.2.0]: https://github.com/dddabtc/winremote-mcp/releases/tag/v0.2.0

[0.4.9]: https://github.com/dddabtc/winremote-mcp/releases/tag/v0.4.9
[0.4.8]: https://github.com/dddabtc/winremote-mcp/releases/tag/v0.4.8
