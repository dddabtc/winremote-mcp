# OpenClaw Integration Guide

## Overview

winremote-mcp can be used with [OpenClaw](https://github.com/openclaw/openclaw) to give your AI agent full control over a Windows machine — screenshots, clicking, typing, file management, and more.

## Setup

### 1. Install on Windows

```bash
pip install winremote-mcp
python -m winremote
```

Server starts on `http://0.0.0.0:8090/mcp` by default.

### 2. Configure OpenClaw

Add to your `~/.openclaw/openclaw.json`:

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

Replace `<windows-ip>` with your Windows machine's IP address.

### 3. With Authentication (Recommended)

Start the server with an auth key:

```bash
python -m winremote --auth-key "your-secret-key"
# or
WINREMOTE_AUTH_KEY=your-secret-key python -m winremote
```

Then in OpenClaw config:

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

### 4. Verify Connection

After restarting OpenClaw, the agent should have access to all winremote tools. Test by asking:

> "Take a screenshot of the Windows desktop"

## Use Cases with OpenClaw

- **Desktop monitoring** — Periodic screenshots via heartbeat/cron jobs
- **Browser automation** — Navigate, click, type in any Windows app
- **File management** — Read/write files remotely
- **System administration** — Check processes, services, event logs
- **Notification relay** — Send Windows toast notifications from your AI

---

# Making winremote-mcp an OpenClaw Skill

## What is a Skill?

An OpenClaw Skill is a packaged capability that any OpenClaw agent can use. It includes a `SKILL.md` with instructions, optional scripts, and configuration.

## Skill Structure

```
skills/
  winremote/
    SKILL.md          # Instructions for the agent
    scripts/
      setup.sh        # Optional: auto-setup script
      test.sh         # Optional: health check
```

## SKILL.md Template

```markdown
# winremote — Windows Remote Control

Control a Windows machine via MCP protocol.

## Prerequisites

- winremote-mcp running on the target Windows machine
- Network access from OpenClaw host to Windows machine

## Setup

1. On Windows: `pip install winremote-mcp && python -m winremote`
2. Add MCP server to OpenClaw config (see docs/openclaw-integration.md)

## Available Tools

After setup, you have these MCP tools:

### Desktop
- `Snapshot` — Screenshot + window list (params: use_vision, quality, max_width, monitor)
- `Click` — Mouse click at coordinates
- `Type` — Type text
- `Scroll` — Scroll at position
- `Move` — Move mouse / drag
- `Shortcut` — Keyboard shortcuts (e.g. "ctrl+c")
- `FocusWindow` — Bring window to front by title
- `MinimizeAll` — Show desktop (Win+D)
- `App` — Launch/switch/resize applications

### System
- `Shell` — Execute PowerShell commands (with cwd support)
- `GetSystemInfo` — CPU, memory, disk, network, uptime
- `ListProcesses` — Process list with CPU/memory
- `KillProcess` — Kill by PID or name

### Files
- `FileRead` / `FileWrite` — Text files
- `FileDownload` / `FileUpload` — Binary files (base64)
- `FileList` — Directory listing
- `FileSearch` — Glob pattern search

### Other
- `GetClipboard` / `SetClipboard`
- `Notification` — Windows toast notifications
- `Scrape` — Fetch URL content
- `Ping` / `PortCheck` / `NetConnections`
- `ServiceList` / `ServiceStart` / `ServiceStop`
- `RegRead` / `RegWrite`
- `EventLog` — Windows event logs

## Tips

- Use `Snapshot` with `quality=50, max_width=1280` for faster transfers
- Use `FocusWindow` before `Click`/`Type` to target the right window
- `Shell` supports `cwd` parameter for working directory
- Chain `Snapshot` → identify target → `Click` for UI automation
```

## Publishing as a Skill

### Option 1: Local Skill

Place the skill folder in your OpenClaw workspace:

```
~/clawd/skills/winremote/SKILL.md
```

OpenClaw will auto-discover it.

### Option 2: Publish to ClawHub

1. Package your skill following the [skill-creator guide](https://docs.openclaw.ai/skills)
2. Submit to [ClawHub](https://clawhub.com) for community use

## Auto-Start on Boot

Use the built-in install command on Windows:

```bash
python -m winremote install
```

This creates a Windows scheduled task that starts winremote-mcp on boot.

To remove:

```bash
python -m winremote uninstall
```
