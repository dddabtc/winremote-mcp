# winremote-mcp for Claude Desktop / Claude Code

## Setup

### 1. Install on Windows

```bash
pip install winremote-mcp
```

### 2. Configure Claude Desktop

Edit `claude_desktop_config.json`:

**Local (stdio — Claude Desktop on the same Windows machine):**
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

**Remote (streamable-http — Claude Desktop on a different machine):**

First, start the server on Windows:
```bash
python -m winremote --auth-key "your-secret-key"
```

Then configure Claude Desktop:
```json
{
  "mcpServers": {
    "winremote": {
      "type": "streamable-http",
      "url": "http://<windows-ip>:8090/mcp",
      "headers": {
        "Authorization": "Bearer your-secret-key"
      }
    }
  }
}
```

### 3. Configure Claude Code (CLI)

Add to your Claude Code MCP settings:

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

Or for remote:
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

## Config File Locations

| Platform | Path |
|----------|------|
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Claude Desktop (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` |
| Claude Code | Project `.mcp.json` or `~/.claude/mcp.json` |
| Cursor | `.cursor/mcp.json` in project root |

## What Claude Can Do

With winremote-mcp, Claude gets 40 tools to control your Windows machine:

- **See your screen** — `Snapshot`, `AnnotatedSnapshot`, `OCR`
- **Click and type** — `Click`, `Type`, `Shortcut`, `FocusWindow`
- **Run commands** — `Shell` (PowerShell), `App` (launch programs)
- **Manage files** — `FileRead`, `FileWrite`, `FileList`, `FileSearch`
- **Monitor system** — `GetSystemInfo`, `ListProcesses`, `ServiceList`
- **Network tools** — `Ping`, `PortCheck`, `NetConnections`
- **Record screen** — `ScreenRecord` (GIF output)
- **And more** — Clipboard, notifications, registry, event logs, scheduled tasks

## Example Prompts

> "Take a screenshot and tell me what's on my screen"

> "Open Chrome and navigate to github.com"

> "Find all .py files on my Desktop"

> "What processes are using the most memory?"

> "Check if port 3000 is open on localhost"

> "Record my screen for 5 seconds"
