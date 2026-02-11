# winremote-mcp

[![CI](https://github.com/dddabtc/winremote-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/dddabtc/winremote-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/winremote-mcp)](https://pypi.org/project/winremote-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/winremote-mcp)](https://pypi.org/project/winremote-mcp/)

A Windows Remote MCP Server — control Windows desktops via the [Model Context Protocol](https://modelcontextprotocol.io/).

Built with [FastMCP](https://github.com/jlowin/fastmcp). Runs **on the Windows machine** you want to control.

## Features

- **Desktop Control** — screenshot (JPEG compressed, multi-monitor), click, type, scroll, keyboard shortcuts
- **Window Management** — focus, minimize-all, launch/resize apps
- **Remote Management** — PowerShell shell (with `cwd`), clipboard, processes, system info, notifications
- **File Operations** — read, write, list, search, binary transfer (base64)
- **Registry Tools** — read/write Windows Registry values
- **Service Management** — list, start, stop Windows services
- **Scheduled Tasks** — list, create, delete scheduled tasks
- **Network Tools** — ping, port check, network connections
- **Event Log** — read Windows Event Log with level filtering
- **API Key Auth** — optional `--auth-key` / `WINREMOTE_AUTH_KEY` for Bearer token authentication
- **Health Endpoint** — `GET /health` returns `{"status":"ok","version":"0.3.0"}` (always public)
- **OCR** — extract text from screen regions (pytesseract or Windows built-in)
- **Screen Recording** — capture animated GIF of screen activity
- **Annotated Snapshot** — screenshot with numbered labels on interactive elements
- **Hot Reload** — `--reload` flag for development
- **Auto-Start** — `winremote install` / `winremote uninstall` for Windows scheduled tasks

## Installation

```bash
# From PyPI (once published)
pip install winremote-mcp

# From source
pip install .

# With uv
uv pip install .
```

> **PyPI publishing**: This repo uses GitHub Actions with [trusted publishers](https://docs.pypi.org/trusted-publishers/). To enable, configure PyPI trusted publisher for the `dddabtc/winremote-mcp` repo, workflow `publish.yml`, environment `pypi`.

## Usage

### stdio transport
```bash
winremote-mcp
# or
uv run winremote-mcp
```

### Streamable HTTP transport (default)
```bash
# Local only (default: 127.0.0.1)
winremote-mcp

# Remote access — explicitly bind to all interfaces
winremote-mcp --host 0.0.0.0 --port 8090
```

### With hot reload (development)
```bash
winremote-mcp --reload
```

### With authentication
```bash
winremote-mcp --auth-key "my-secret-key"
# or via environment variable
WINREMOTE_AUTH_KEY="my-secret-key" winremote-mcp
```

Clients must include `Authorization: Bearer my-secret-key` header. The `/health` endpoint remains public.

### Health check
```bash
curl http://localhost:8090/health
# {"status":"ok","version":"0.4.1"}
```

### Auto-start (Windows scheduled task)
```bash
# Create scheduled task to start on boot
winremote-mcp install

# Remove scheduled task
winremote-mcp uninstall
```

### MCP Client Config

**stdio:**
```json
{
  "mcpServers": {
    "windows-remote": {
      "command": "uv",
      "args": ["run", "winremote-mcp"]
    }
  }
}
```

**streamable-http:**
```json
{
  "mcpServers": {
    "windows-remote": {
      "type": "streamable-http",
      "url": "http://<windows-ip>:8090/mcp"
    }
  }
}
```

## What's New in v0.4.1

- **ReconnectSession Tool**: New tool to reconnect disconnected Windows desktop sessions to console, enabling screenshot/automation when no RDP client is connected
- **Auto-reconnect Behavior**: `Snapshot` and `AnnotatedSnapshot` now automatically reconnect disconnected sessions if screenshot capture fails, then retry the operation
- **Chinese Windows Support**: Fixed encoding crashes on Chinese Windows systems (GBK terminals)
  - Replaced emoji characters (✅ ❌) in `install`/`uninstall` commands with plain text `[OK]`/`[ERROR]`
  - Added `start_mcp.bat` approach that sets `PYTHONIOENCODING=utf-8` before launching the server
  - Scheduled task now uses the batch file for reliable startup on Chinese Windows

### v0.4.0

- **Error Resilience**: All 40 tools wrapped with try/except — errors return helpful messages instead of crashing the server
- **Concurrency Control**: Tools categorized into 5 groups (desktop/file/query/shell/network). Desktop tools (mouse, keyboard, screenshot) are exclusive — only one at a time. Other categories allow parallel execution.
- **Task Management**: Every tool call returns a `[task:id]` prefix. Three new management tools:
  - `CancelTask(task_id)` — cancel a running or pending task
  - `GetTaskStatus(task_id)` — get task details or list recent tasks
  - `GetRunningTasks()` — list all currently active tasks

### v0.3.0

- **API Key Authentication**: `--auth-key` CLI option or `WINREMOTE_AUTH_KEY` env var, Bearer token on all endpoints (except /health)
- **Multi-monitor Snapshot**: `monitor` param to capture specific screens
- **AnnotatedSnapshot**: Screenshot with red numbered labels on clickable UI elements
- **OCR**: Extract text from screen — pytesseract (recommended) + Windows built-in fallback. See [docs/ocr-setup.md](docs/ocr-setup.md)
- **ScreenRecord**: Capture screen as animated GIF (2-10 seconds)
- **Registry**: RegRead, RegWrite
- **Services**: ServiceList, ServiceStart, ServiceStop
- **Scheduled Tasks**: TaskList, TaskCreate, TaskDelete
- **Network**: Ping, PortCheck, NetConnections (with `limit` param)
- **File Transfer**: FileDownload, FileUpload (binary via base64)
- **Event Log**: Windows Event Log viewer with level filtering
- **Skill Packages**: Ready-to-use configs for [OpenClaw](skill/openclaw/SKILL.md), [Claude](skill/claude/README.md), [Cursor](skill/cursor/README.md)

### v0.2.0

- Snapshot JPEG compression (quality + max_width params)
- Health endpoint, Shell cwd param, hot reload, install/uninstall commands

## Tools

| Tool | Description |
|------|-------------|
| Snapshot | Screenshot (JPEG, configurable quality/max_width) + window list + UI elements |
| Click | Mouse click (left/right/middle, single/double/hover) |
| Type | Type text at coordinates |
| Scroll | Vertical/horizontal scroll |
| Move | Move mouse / drag |
| Shortcut | Keyboard shortcuts |
| Wait | Pause execution |
| FocusWindow | Bring window to front (fuzzy title match) |
| MinimizeAll | Show desktop (Win+D) |
| App | Launch/switch/resize applications |
| Shell | Execute PowerShell commands (with optional cwd) |
| GetClipboard | Read clipboard |
| SetClipboard | Write clipboard |
| ListProcesses | Process list with CPU/memory |
| KillProcess | Kill process by PID or name |
| GetSystemInfo | System information |
| Notification | Windows toast notification |
| LockScreen | Lock workstation |
| Scrape | Fetch URL content |
| FileRead | Read file content |
| FileWrite | Write file content |
| FileList | List directory contents |
| FileSearch | Search files by pattern |
| FileDownload | Download file as base64 (binary) |
| FileUpload | Upload file from base64 (binary) |
| RegRead | Read Windows Registry value |
| RegWrite | Write Windows Registry value |
| ServiceList | List Windows services |
| ServiceStart | Start a Windows service |
| ServiceStop | Stop a Windows service |
| TaskList | List scheduled tasks |
| TaskCreate | Create a scheduled task |
| TaskDelete | Delete a scheduled task |
| Ping | Ping a host |
| PortCheck | Check if a TCP port is open |
| NetConnections | List network connections |
| EventLog | Read Windows Event Log entries |
| OCR | Extract text from screen via OCR (pytesseract or Windows built-in) |
| ScreenRecord | Record screen activity as animated GIF |
| AnnotatedSnapshot | Screenshot with numbered labels on interactive elements |
| ReconnectSession | Reconnect disconnected Windows desktop session to console |
| CancelTask | Cancel a running or pending task by ID |
| GetTaskStatus | Get task details or list recent task history |
| GetRunningTasks | List all currently active (running/pending) tasks |

### OCR (optional dependency)

The OCR tool supports two engines: **pytesseract** (recommended) and **Windows built-in OCR** (fallback).

Quick setup:
```bash
# 1. Install Tesseract-OCR engine
winget install UB-Mannheim.TesseractOCR

# 2. Install Python package
pip install winremote-mcp[ocr]
```

Supports 100+ languages including Chinese (`chi_sim`), Japanese (`jpn`), Korean (`kor`).

📖 **Full guide**: [docs/ocr-setup.md](docs/ocr-setup.md) — installation, language packs, Windows OCR fallback, troubleshooting.

## Requirements

- Windows 10/11
- Python >= 3.10

## Integration & Skills

Ready-to-use skill packages for popular AI platforms:

| Platform | Guide | Transport |
|----------|-------|-----------|
| [OpenClaw](skill/openclaw/SKILL.md) | Full skill with 40 tools | stdio / streamable-http |
| [Claude Desktop / Claude Code](skill/claude/README.md) | MCP config for Claude | stdio / streamable-http |
| [Cursor](skill/cursor/README.md) | `.cursor/mcp.json` config | stdio / streamable-http |

### Quick Config (any MCP client)

**Local (stdio):**
```json
{
  "mcpServers": {
    "winremote": {
      "command": "python",
      "args": ["-m", "winremote", "--transport", "stdio"]
    }
  }
}
```

**Remote (streamable-http):**
```bash
# On Windows: python -m winremote
```
```json
{
  "mcpServers": {
    "winremote": {
      "type": "streamable-http",
      "url": "http://<windows-ip>:8090/mcp"
    }
  }
}
```

See [docs/openclaw-integration.md](docs/openclaw-integration.md) for detailed setup with authentication.

## Security

**Default bind: `127.0.0.1` (localhost only).** Remote access requires explicit `--host 0.0.0.0`.

When exposing to the network:
- **Always use `--auth-key`** — without it, anyone on the network has full access
- **Use a firewall** — restrict port 8090 to trusted IPs only
- **Consider a reverse proxy** — nginx/caddy with TLS for encrypted connections
- **Network segmentation** — run on a private VLAN, not the public internet

### Current security model

| Feature | Status |
|---------|--------|
| Bearer token auth | ✅ `--auth-key` |
| Localhost by default | ✅ `127.0.0.1` |
| Health endpoint public | ✅ No auth needed |
| Per-tool permissions | ❌ Not yet |
| Operation audit log | ❌ Not yet |
| IP allowlist | ❌ Not yet |
| Rate limiting | ❌ Not yet |
| Shell sandboxing | ❌ Not yet |

> ⚠️ **This tool is designed for personal use in trusted networks** (e.g., local development, LAN). Do not expose to the public internet without additional security layers.

## Testing

The project includes a comprehensive test suite with mocked Windows dependencies, so tests run on any platform.

```bash
# Install test dependencies
pip install -e ".[test]"

# Run all tests
pytest

# Run with coverage
pytest --cov=winremote --cov-report=term-missing

# Run specific test module
pytest tests/test_desktop_tools.py
pytest tests/test_taskmanager.py
```

### Test Structure

| File | Covers |
|------|--------|
| `test_desktop_tools.py` | Click, Type, Scroll, Move, Shortcut, Wait, FocusWindow, MinimizeAll |
| `test_shell_tools.py` | Shell, Scrape, App |
| `test_services.py` | ServiceList/Start/Stop, TaskList/Create/Delete, EventLog |
| `test_network.py` | Ping, PortCheck, NetConnections |
| `test_taskmanager.py` | TaskManager concurrency, cancellation, wrapping |
| `test_auth.py` | AuthKeyMiddleware (Bearer token, /health bypass) |
| `test_registry.py` | Registry read/write, key parsing |
| `test_helpers.py` | `_tobool`, `_check_win32`, version |
| `test_integration.py` | MCP tool registration, /health endpoint |

All tests use `unittest.mock` to avoid requiring a real Windows environment.

## Acknowledgments

Inspired by [Windows-MCP](https://github.com/CursorTouch/Windows-MCP) by CursorTouch. Thanks for the pioneering work on Windows desktop automation via MCP.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
