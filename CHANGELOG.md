# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.4.8]: https://github.com/dddabtc/winremote-mcp/releases/tag/v0.4.8
