# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.2.0]: https://github.com/dddabtc/winremote-mcp/releases/tag/v0.2.0
