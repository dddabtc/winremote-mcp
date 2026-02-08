# winremote — Windows Remote Control

Control a Windows machine remotely via MCP protocol. 40 tools for desktop automation, system management, file operations, and more.

## Prerequisites

- winremote-mcp running on the target Windows machine
- Network access from OpenClaw host to the Windows machine

## Quick Setup

**On Windows:**
```bash
pip install winremote-mcp
python -m winremote
# Server starts on http://127.0.0.1:8090/mcp (local only)

# For remote access:
python -m winremote --host 0.0.0.0
```

**With authentication (recommended):**
```bash
python -m winremote --auth-key "your-secret-key"
```

**Auto-start on boot:**
```bash
python -m winremote install
```

## OpenClaw Config

Add to `~/.openclaw/openclaw.json`:

```json
{
  "mcp": {
    "servers": {
      "winremote": {
        "type": "streamable-http",
        "url": "http://<windows-ip>:8090/mcp"
      }
    }
  }
}
```

With auth:
```json
{
  "mcp": {
    "servers": {
      "winremote": {
        "type": "streamable-http",
        "url": "http://<windows-ip>:8090/mcp",
        "headers": {
          "Authorization": "Bearer your-secret-key"
        }
      }
    }
  }
}
```

## Available Tools (40)

### Desktop Control
- `Snapshot` — Screenshot + window list (JPEG compressed, multi-monitor support)
- `AnnotatedSnapshot` — Screenshot with numbered labels on clickable elements
- `OCR` — Extract text from screen (pytesseract or Windows built-in)
- `ScreenRecord` — Record screen as GIF (2-10 seconds)
- `Click` — Mouse click at coordinates (left/right/middle, single/double)
- `Type` — Type text at coordinates
- `Scroll` — Scroll at position
- `Move` — Move mouse or drag
- `Shortcut` — Keyboard shortcuts (e.g. "ctrl+c", "alt+tab")
- `FocusWindow` — Bring window to front (fuzzy title match)
- `MinimizeAll` — Show desktop (Win+D)
- `App` — Launch, switch, or resize applications

### System Management
- `Shell` — Execute PowerShell commands (with working directory support)
- `GetSystemInfo` — CPU, memory, disk, network, uptime
- `ListProcesses` — Process list with CPU/memory usage
- `KillProcess` — Kill process by PID or name
- `ServiceList` / `ServiceStart` / `ServiceStop` — Windows service management
- `TaskList` / `TaskCreate` / `TaskDelete` — Scheduled task management
- `EventLog` — Windows event log viewer with level filtering

### File Operations
- `FileRead` / `FileWrite` — Text file read/write
- `FileDownload` / `FileUpload` — Binary file transfer (base64)
- `FileList` — Directory listing with sizes
- `FileSearch` — Glob pattern file search

### Registry
- `RegRead` — Read registry values
- `RegWrite` — Write registry values

### Network
- `Ping` — Ping a host
- `PortCheck` — Check if a port is open
- `NetConnections` — List network connections

### Other
- `GetClipboard` / `SetClipboard` — Clipboard access
- `Notification` — Windows toast notifications
- `LockScreen` — Lock workstation
- `Scrape` — Fetch URL content as markdown
- `Wait` — Pause execution

## Tips

- Use `Snapshot` with `quality=50, max_width=1280` for faster transfers
- Use `AnnotatedSnapshot` to identify UI elements visually — each element gets a red numbered label
- Use `FocusWindow` before `Click`/`Type` to ensure the right window is active
- Chain: `AnnotatedSnapshot` → identify target number → `Click` at its coordinates
- `Shell` supports `cwd` parameter — no need to `cd` first
- `ScreenRecord` with `duration=3, fps=5, max_width=640` for lightweight GIFs
- `OCR` works best with `pip install winremote-mcp[ocr]` (pytesseract)

## Health Check

```bash
curl http://<windows-ip>:8090/health
# {"status":"ok","version":"0.3.0"}
```

## Links

- GitHub: https://github.com/dddabtc/winremote-mcp
- PyPI: https://pypi.org/project/winremote-mcp/
