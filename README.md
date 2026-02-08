# winremote-mcp

A Windows Remote MCP Server — control Windows desktops via the [Model Context Protocol](https://modelcontextprotocol.io/).

Built with [FastMCP](https://github.com/jlowin/fastmcp). Runs **on the Windows machine** you want to control.

## Features

- **Desktop Control** — screenshot (JPEG compressed), click, type, scroll, keyboard shortcuts
- **Window Management** — focus, minimize-all, launch/resize apps
- **Remote Management** — PowerShell shell (with `cwd`), clipboard, processes, system info, notifications
- **File Operations** — read, write, list, search files
- **Health Endpoint** — `GET /health` returns `{"status":"ok","version":"0.2.0"}`
- **Hot Reload** — `--reload` flag for development
- **Auto-Start** — `winremote install` / `winremote uninstall` for Windows scheduled tasks

## Installation

```bash
# With uv (recommended)
uv pip install .

# Or with pip
pip install .
```

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

## Requirements

- Windows 10/11
- Python >= 3.10

## Acknowledgments

Inspired by [Windows-MCP](https://github.com/CursorTouch/Windows-MCP) by CursorTouch. Thanks for the pioneering work on Windows desktop automation via MCP.

## License

MIT
