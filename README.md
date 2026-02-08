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

### Streamable HTTP transport (default, for remote access)
```bash
winremote-mcp --transport streamable-http --host 0.0.0.0 --port 8090
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
# {"status":"ok","version":"0.2.0"}
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

## What's New in v0.2.0

- **Snapshot compression**: Returns JPEG instead of PNG. Configurable `quality` (default 75) and `max_width` (default 1920) params. Significantly reduces image size.
- **Health endpoint**: `GET /health` returns JSON status — useful for monitoring and load balancers.
- **Shell cwd parameter**: Optional `cwd` param to run commands in a specific directory.
- **Better pywin32 error reporting**: Explicit error messages when pywin32 is missing instead of silent failures.
- **Hot reload**: `--reload` flag passes through to uvicorn for development.
- **Install/uninstall commands**: `winremote install` creates a Windows scheduled task for auto-start on boot.

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

### OCR (optional dependency)

For the OCR tool, install pytesseract:
```bash
pip install winremote-mcp[ocr]
# Also install Tesseract-OCR: https://github.com/UB-Mannheim/tesseract/wiki
```

If pytesseract is not installed, the OCR tool will attempt to use the Windows built-in OCR engine (Windows 10+).

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

## Acknowledgments

Inspired by [Windows-MCP](https://github.com/CursorTouch/Windows-MCP) by CursorTouch. Thanks for the pioneering work on Windows desktop automation via MCP.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
