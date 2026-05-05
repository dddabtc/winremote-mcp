# WinRemote MCP — Run MCP Servers Remotely on Windows

[![PyPI version](https://img.shields.io/pypi/v/winremote-mcp)](https://pypi.org/project/winremote-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/winremote-mcp)](https://pypi.org/project/winremote-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/dddabtc/winremote-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/dddabtc/winremote-mcp/actions/workflows/ci.yml)
[![Downloads](https://static.pepy.tech/badge/winremote-mcp)](https://pepy.tech/projects/winremote-mcp)
[![win-remote-mcp MCP server](https://glama.ai/mcp/servers/dddabtc/win-remote-mcp/badges/score.svg)](https://glama.ai/mcp/servers/dddabtc/win-remote-mcp)

**The ultimate Windows MCP server for remote desktop control and automation.** Control any Windows machine through the Model Context Protocol — perfect for AI agents, Claude Desktop. Transform your Windows desktop into a powerful, remotely-accessible automation endpoint.

Run **on the Windows machine** you want to control. Built with [FastMCP](https://github.com/jlowin/fastmcp) and the [Model Context Protocol](https://modelcontextprotocol.io/).

## Quickstart (30 seconds)

```bash
# Install from PyPI
pip install winremote-mcp

# Start the Windows MCP server
winremote-mcp
```

That's it! Your Windows MCP server is now running on `http://127.0.0.1:8090` and ready to accept commands from MCP clients like Claude Desktop.

## 🤖 Agent Integrations

winremote-mcp works with MCP-compatible AI agents and clients. Client-specific setup guides live in this repo:

- [Hermes](skill/hermes/) — add winremote as a native streamable HTTP or stdio MCP server.
- [OpenClaw](skill/openclaw/) — use winremote as OpenClaw's Windows control layer.
- [Claude Desktop / Claude Code](skill/claude/) — configure local stdio or remote streamable HTTP.
- [Cursor](skill/cursor/) — add winremote to `.cursor/mcp.json`.

### Hermes Setup

Run winremote-mcp on the Windows machine, then add it to Hermes as an MCP server:

```powershell
pip install winremote-mcp
winremote-mcp --host 0.0.0.0 --port 8090 --auth-key "your-secret-key"
```

```yaml
mcp_servers:
  winremote:
    type: streamable-http
    url: http://<windows-ip>:8090/mcp
    headers:
      Authorization: Bearer your-secret-key
```

See the full [Hermes integration guide](skill/hermes/) for local stdio setup, verification prompts, and available capabilities.

## 🤖 OpenClaw Integration

winremote-mcp is the official Windows control layer for [OpenClaw](https://github.com/openclaw/openclaw). Together they give your AI agent full remote control over any Windows machine — screenshots, PowerShell, file transfer, GUI automation, and more.

---

### The Easiest Way: Just Tell OpenClaw

You don't need to configure anything manually. Just tell your OpenClaw agent:

> "Install winremote-mcp on my Windows machine at `192.168.1.100` and connect it to yourself. Python is installed at `C:\Python311\python.exe`."

OpenClaw will SSH into the Windows machine, install the package, start the server, and wire up the MCP connection — all automatically.

---

### Manual Setup (Step by Step)

#### Step 1 — Install on Windows

```cmd
pip install winremote-mcp
```

#### Step 2 — Start the server

**Local-only quick start (default, safest):**
```cmd
winremote-mcp
```

**Remote access requires authentication:**

Starting with v0.4.20, `winremote-mcp` refuses to bind HTTP transport to a non-loopback address without authentication. Use an API key for LAN or remote access:

```cmd
winremote-mcp --host 0.0.0.0 --port 8090 --auth-key YOUR_SECRET_KEY
```

For lab-only legacy behavior, you can explicitly acknowledge the risk with `--allow-insecure-remote`; do not use this on shared, routed, or internet-exposed networks.

**Auto-start on boot:**
```cmd
winremote-mcp install
```

#### Step 3 — Connect OpenClaw

Add to your `openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "winremote": {
        "type": "mcp",
        "url": "http://192.168.1.100:8090/mcp",
        "headers": {
          "Authorization": "Bearer YOUR_SECRET_KEY"
        }
      }
    }
  }
}
```

Or tell your OpenClaw agent:
> "Add winremote MCP at `http://192.168.1.100:8090/mcp` with auth key `YOUR_SECRET_KEY`."

#### Step 4 — What your agent can do

Once connected, your AI agent has full Windows control:

| Capability | Example |
|------------|---------|
| 🖥️ Screenshots | Capture the full desktop or a specific window |
| ⚡ Shell execution | Run PowerShell, CMD, or batch scripts |
| 📁 File transfer | Upload/download files between Linux and Windows |
| 🖱️ GUI automation | Click, type, drag — control any Windows app |
| 🔧 System info | Process list, services, event logs, registry |
| 📷 OCR | Extract text from any screen region |
| 🎬 Screen recording | Record desktop activity as GIF |

---

### Secure Remote Access (HTTPS)

For access over the internet or untrusted networks, enable HTTPS:

**Step 1 — Generate a certificate:**
```bash
# Self-signed (LAN/homelab)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Trusted cert (no browser warnings) — requires mkcert installed
mkcert -install && mkcert 192.168.1.100
```

**Step 2 — Start with TLS:**
```cmd
winremote-mcp --host 0.0.0.0 --port 8090 ^
  --auth-key YOUR_SECRET_KEY ^
  --ssl-certfile cert.pem ^
  --ssl-keyfile key.pem
```

**OpenClaw config with HTTPS:**
```json
{
  "plugins": {
    "entries": {
      "winremote": {
        "type": "mcp",
        "url": "https://192.168.1.100:8090/mcp",
        "headers": {
          "Authorization": "Bearer YOUR_SECRET_KEY"
        }
      }
    }
  }
}
```

---

### OAuth 2.0 (for Claude Desktop and other MCP clients)

Some MCP clients (like Claude Desktop) use OAuth instead of API keys. OAuth is a pre-provisioned confidential-client flow: configure both client ID and client secret on the server, then copy the same values into the client. Dynamic client registration is disabled, and redirect URIs must be loopback `http(s)` URIs.

```cmd
winremote-mcp --host 0.0.0.0 --port 8090 ^
  --ssl-certfile cert.pem --ssl-keyfile key.pem ^
  --oauth-client-id my-client --oauth-client-secret my-secret
```

**Claude Desktop config (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "winremote": {
      "type": "http",
      "url": "https://192.168.1.100:8090/mcp/",
      "oauth": {
        "clientId": "my-client",
        "clientSecret": "my-secret"
      }
    }
  }
}
```

---

### `winremote.toml` — Full Config Reference

Place in your working directory or `~/.config/winremote/winremote.toml`:

```toml
[server]
host         = "0.0.0.0"
port         = 8090
auth_key     = "your-secret-key"
# Optional break-glass flag for legacy trusted-LAN deployments only.
# Remote HTTP without auth is refused unless this is true.
allow_insecure_remote = false
ssl_certfile = "C:/certs/cert.pem"   # optional — enables HTTPS
ssl_keyfile  = "C:/certs/key.pem"    # optional — enables HTTPS

[security]
ip_allowlist        = ["192.168.1.0/24"]   # restrict to LAN only
oauth_client_id     = ""                    # optional OAuth client ID
oauth_client_secret = ""                    # optional OAuth secret

[tools]
exclude = ["ScreenRecord"]   # disable specific tools
```

---

> **Note:** winremote-mcp is a standard MCP server and works with any MCP-compatible client — Claude Desktop, Cursor, OpenClaw, and others.

## What's New in v0.4.19

### 🤖 Hermes Integration

- Added a Hermes setup guide for connecting winremote-mcp as a native MCP server.
- Added README links to client-specific integration guides in this repository.

## What's New in v0.4.18

### 🔒 Security Hardening & Bug Fixes

Comprehensive security audit and fix pass across the entire codebase:

- **Fixed command injection** in Shell (`cwd`), Services (filter), Desktop (`launch_app`, `show_notification`), and `install`/`uninstall` CLI commands — all user inputs now properly escaped with PowerShell single-quote quoting or subprocess list form.
- **Fixed OAuth token bypass** — `client_secret` is now mandatory when the client has one configured (previously could be omitted to skip validation).
- **Fixed coordinate (0,0) unreachable** — `Type`, `Scroll`, and `Move` tools now correctly handle coordinates where x or y is zero.
- **Fixed AnnotatedSnapshot performance** — no longer takes redundant extra screenshots for scale calculation.
- **Fixed ScreenRecord** — duration clamped to 0.1–10s, fps to 1–10; fixed GIF size calculation.
- **Added FileUpload size limit** — rejects base64 payloads over 100 MB.
- **Removed dead code** — duplicate `_ensure_session_connected()` function removed.
- **Hardened XML escaping** in toast notifications to prevent injection via title/message.
- **Improved temp file cleanup** — PlaySound now cleans up downloaded files in `finally` block.
- **TaskManager** — cancel operations now hold lock during status transition.

## What's New in v0.4.17

### 🔧 PlaySound Fix

Fixed PlaySound tool not working through the MCP interface:

- **Parameters now accept `null`** — MCP clients that pass `null` for omitted params no longer get a `ValidationError`.
- **Audio actually plays** — switched from async `Play()` to `PlaySync()` for WAV; the old implementation caused PowerShell to exit before audio could start.
- **Removed `System.Windows.Forms` dependency** — no longer loads an unnecessary assembly that could fail in non-interactive/service sessions.
- **Real .mp3/.ogg support** — non-WAV formats now route through WPF `MediaPlayer` instead of `SoundPlayer` (which only handles `.wav`).
- **Path sanitisation** — prevents PowerShell injection via crafted file paths.

## What's New in v0.4.16

### 🔊 PlaySound Tool

New Tier 1 tool to play audio files on the Windows host. Supports `.wav`, `.mp3`, `.ogg` from local path or URL.

## What's New in v0.4.9

### 🔒 HTTPS / TLS Support

You can now run WinRemote MCP over HTTPS — required for remote access and for tools like Claude Desktop that need a secure connection.

**Step 1 — Generate a self-signed certificate** (for local/LAN use):
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

**Step 2 — Start the server with TLS:**
```bash
winremote-mcp --ssl-certfile cert.pem --ssl-keyfile key.pem --host 0.0.0.0 --port 8090
```

Or in `winremote.toml`:
```toml
[server]
host         = "0.0.0.0"
port         = 8090
ssl_certfile = "C:/Users/you/cert.pem"
ssl_keyfile  = "C:/Users/you/key.pem"
```

When active, the startup banner shows **`[https ON]`** and the server listens on `https://`.

**Claude Desktop config** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "winremote": {
      "type": "http",
      "url": "https://192.168.1.100:8090/mcp/",
      "headers": { "Authorization": "Bearer YOUR_AUTH_KEY" }
    }
  }
}
```

> **Tip:** For a trusted certificate (no browser warning), use [mkcert](https://github.com/FiloSottile/mkcert): `mkcert -install && mkcert 192.168.1.100`

---

### 🔑 OAuth 2.0 Support (closes #33)

WinRemote now ships a built-in OAuth 2.0 Authorization Server, so clients like Claude Desktop can authenticate via OAuth instead of a static API key.

```bash
winremote-mcp --ssl-certfile cert.pem --ssl-keyfile key.pem \
                --oauth-client-id my-client --oauth-client-secret my-secret
```

The server exposes the standard MCP OAuth endpoints:
- `GET /.well-known/oauth-authorization-server`
- `POST /oauth/register`
- `GET /oauth/authorize`
- `POST /oauth/token`

Startup banner shows **`[oauth ON]`** when enabled. Existing `--auth-key` Bearer token auth still works unchanged.

---

## What's New in v0.4.8

- ✅ Added compatibility with **fastmcp 3.x** internal tool registry changes
- ✅ Kept compatibility with **fastmcp 2.x**
- ✅ Fixed tool wrapping/filtering paths that could raise:
  `AttributeError: 'FastMCP' object has no attribute '_tool_manager'`

## What Problem It Solves

- **Remote Windows Control**: Control Windows desktops from anywhere through standardized MCP protocol
- **AI Agent Integration**: Enable Claude, GPT, and other AI agents to interact with Windows GUI applications  
- **Cross-Platform Automation**: Bridge the gap between Linux/macOS development environments and Windows targets
- **Headless Windows Management**: Manage Windows servers and workstations without RDP or VNC overhead

## Features

- **Desktop Control** — Screenshot capture (JPEG compressed, multi-monitor), click, type, scroll, keyboard shortcuts
- **Window Management** — Focus windows, minimize-all, launch/resize applications, multi-monitor support
- **Remote Shell Access** — PowerShell command execution with working directory support
- **File Operations** — Read, write, list, search files; binary transfer via base64 encoding
- **System Administration** — Windows Registry access, service management, scheduled tasks, process control
- **Network Tools** — Ping hosts, check TCP ports, monitor network connections
- **Advanced Features** — OCR text extraction, screen recording (GIF), annotated screenshots with UI element labels
- **AI Vision Support** — Works with Flutter, Electron, Qt and any UI via AI vision. See [Vision Guide](docs/vision-guide.md)
- **Security & Auth** — Optional API key authentication, localhost-only binding by default

## Installation

### From PyPI (Recommended)
```bash
pip install winremote-mcp
```

### From Source
```bash
git clone https://github.com/dddabtc/winremote-mcp.git
cd winremote-mcp
pip install .
```

### With Optional Dependencies
```bash
# Install with OCR support (includes pytesseract)
pip install winremote-mcp[ocr]

# Install development dependencies
pip install winremote-mcp[test]
```

### OCR Setup (Optional)
For text extraction from screenshots:
```bash
# 1. Install Tesseract OCR engine
winget install UB-Mannheim.TesseractOCR

# 2. Install with OCR dependencies
pip install winremote-mcp[ocr]
```

## Usage

### Basic Usage

### Tier and tool controls
```bash
# Default: tier1 + tier2 enabled, tier3 disabled
winremote-mcp

# Enable destructive tier3 tools
winremote-mcp --enable-tier3

# Disable interactive tier2 (tier1 only)
winremote-mcp --disable-tier2

# Both together: tier1 + tier3 (tier2 disabled)
winremote-mcp --enable-tier3 --disable-tier2

# Backward-compatible: enable everything
winremote-mcp --enable-all

# Explicit tool list (highest precedence over tier flags)
winremote-mcp --tools Snapshot,Click,Type

# Remove specific tools from resolved set
winremote-mcp --enable-tier3 --exclude-tools Shell,FileWrite
```

### Config file (`winremote.toml`)
Search order:
1. `--config /path/to/winremote.toml`
2. `./winremote.toml`
3. `~/.config/winremote/winremote.toml`

```toml
[server]
host = "127.0.0.1"
port = 8090
auth_key = ""
ssl_certfile = ""       # Path to SSL certificate for HTTPS
ssl_keyfile = ""        # Path to SSL private key for HTTPS

[security]
ip_allowlist = ["127.0.0.1", "192.168.1.0/24"]
enable_tier3 = false
disable_tier2 = false
oauth_client_id = ""    # Expected OAuth client ID (optional)
oauth_client_secret = "" # OAuth client secret for confidential clients

[tools]
enable = ["Snapshot", "Click", "Type"]
exclude = []
```

**Precedence:** CLI flags override config file values; config file values override defaults.

### IP allowlist
```bash
# CLI
winremote-mcp --ip-allowlist 127.0.0.1,192.168.1.0/24

# Or via config [security].ip_allowlist
```

Supports both single IPs and CIDR ranges (IPv4/IPv6). Non-allowlisted clients receive HTTP 403 with a clear error.

### HTTPS / TLS

To enable HTTPS, provide SSL certificate and key files:

```bash
winremote-mcp --ssl-certfile cert.pem --ssl-keyfile key.pem
```

Or in `winremote.toml`:
```toml
[server]
ssl_certfile = "/path/to/cert.pem"
ssl_keyfile  = "/path/to/key.pem"
```

**Generate a self-signed certificate** (for local/LAN use):
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

### OAuth 2.0

WinRemote MCP includes a built-in OAuth 2.0 Authorization Server, compatible with Claude Desktop and other MCP clients that require OAuth.

Enable it with:
```bash
winremote-mcp --oauth-client-id my-client --oauth-client-secret my-secret
```

Or in `winremote.toml`:
```toml
[security]
oauth_client_id     = "my-client"
oauth_client_secret = "my-secret"
```

**Claude Desktop config** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "winremote": {
      "type": "http",
      "url": "https://your-host:8080/mcp/",
      "oauth": {
        "clientId": "my-client",
        "clientSecret": "my-secret"
      }
    }
  }
}
```

The OAuth server implements:
- `GET /.well-known/oauth-authorization-server` — server metadata (RFC 8414)
- `POST /oauth/register` — dynamic client registration (RFC 7591)
- `GET /oauth/authorize` — Authorization Code + PKCE (RFC 7636)
- `POST /oauth/token` — token exchange

### Health check
```bash
# Start MCP server (localhost only, no auth)
winremote-mcp

# Start with remote access and authentication
winremote-mcp --host 0.0.0.0 --port 8090 --auth-key "your-secret-key"

# Enable all tools including high-risk Tier 3 (Shell, FileWrite, etc.)
winremote-mcp --enable-all

# Start with hot reload for development
winremote-mcp --reload
```

### MCP Client Configuration

**For Claude Desktop (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "winremote": {
      "command": "winremote-mcp",
      "args": ["--transport", "stdio"]
    }
  }
}
```

**For HTTP MCP clients:**
```json
{
  "mcpServers": {
    "winremote": {
      "type": "streamable-http", 
      "url": "http://192.168.1.100:8090/mcp",
      "headers": {
        "Authorization": "Bearer your-secret-key"
      }
    }
  }
}
```

### Auto-Start on Boot
```bash
# Create Windows scheduled task
winremote-mcp install

# Remove scheduled task  
winremote-mcp uninstall
```

## Security

Tools are organized into three risk tiers. By default, only Tier 1-2 tools are enabled.

| Tier | Risk | Default | Examples |
|------|------|---------|----------|
| **Tier 1** | Read-only | ✅ Enabled | Snapshot, GetSystemInfo, FileList |
| **Tier 2** | Interactive | ✅ Enabled | Click, Type, Shortcut, Scrape |
| **Tier 3** | Destructive / server-side effects | ❌ Disabled | Shell, App, PlaySound, FileWrite |

```bash
# Enable all tiers (use with caution)
winremote-mcp --enable-all

# Always use auth for remote access
winremote-mcp --host 0.0.0.0 --auth-key "your-secret-key"
```

See [SECURITY.md](SECURITY.md) for the full security guide.

## Tools

| Tool | Description |
|------|-------------|
| **Desktop** | |
| Snapshot | Screenshot (JPEG, configurable quality/max_width) + window list + UI elements |
| AnnotatedSnapshot | Screenshot with numbered labels on interactive elements |
| OCR | Extract text from screen via OCR (pytesseract or Windows built-in) |
| ScreenRecord | Record screen activity as animated GIF |
| PlaySound | Play audio file on Windows host (.wav/.mp3/.ogg/.wma/.m4a, local path or URL) |
| **Input** | |
| Click | Mouse click (left/right/middle, single/double/hover) |
| Type | Type text at coordinates |
| Scroll | Vertical/horizontal scroll |
| Move | Move mouse / drag |
| Shortcut | Keyboard shortcuts |
| Wait | Pause execution |
| **Window Management** | |
| FocusWindow | Bring window to front (fuzzy title match) |
| MinimizeAll | Show desktop (Win+D) |
| App | Launch/switch/resize applications |
| **System** | |
| Shell | Execute PowerShell commands (with optional cwd) |
| GetClipboard | Read clipboard |
| SetClipboard | Write clipboard |
| ListProcesses | Process list with CPU/memory |
| KillProcess | Kill process by PID or name |
| GetSystemInfo | System information |
| Notification | Windows toast notification |
| LockScreen | Lock workstation |
| ReconnectSession | Reconnect disconnected Windows desktop session to console |
| **File System** | |
| FileRead | Read file content |
| FileWrite | Write file content |
| FileList | List directory contents |
| FileSearch | Search files by pattern |
| FileDownload | Download file as base64 (binary) |
| FileUpload | Upload file from base64 (binary) |
| **Registry & Services** | |
| RegRead | Read Windows Registry value |
| RegWrite | Write Windows Registry value |
| ServiceList | List Windows services |
| ServiceStart | Start a Windows service |
| ServiceStop | Stop a Windows service |
| **Scheduled Tasks** | |
| TaskList | List scheduled tasks |
| TaskCreate | Create a scheduled task |
| TaskDelete | Delete a scheduled task |
| **Network** | |
| Scrape | Fetch URL content |
| Ping | Ping a host |
| PortCheck | Check if a TCP port is open |
| NetConnections | List network connections |
| EventLog | Read Windows Event Log entries |

## How It Works

```mermaid
graph LR
    A["MCP Client<br/>(Claude/AI)"] -->|commands| B["WinRemote MCP<br/>Server"]
    B -->|API calls| C["Windows APIs<br/>(Win32/WMI/PS)"]
    C -->|results| B
    B -->|responses| A
```

**Transport Options:**
- **stdio**: Direct process communication (ideal for Claude Desktop)
- **HTTP**: RESTful API with optional authentication (ideal for remote access)

**Core Architecture:**
1. **Tool Layer**: 40+ Windows automation tools (screenshot, click, type, etc.)
2. **Task Manager**: Concurrency control and task cancellation
3. **Transport Layer**: MCP protocol over stdio or HTTP
4. **Security Layer**: Optional Bearer token authentication

## Working with Non-Standard UI Frameworks

`AnnotatedSnapshot` uses Win32 API to detect UI elements, which doesn't work with **Flutter, Electron, Qt**, or custom-drawn UIs. Three solutions:

| Approach | Setup | GPU | Best For |
|----------|-------|-----|----------|
| **Snapshot + Claude Vision** | None | No | Most users — Claude sees the screenshot and clicks |
| **[UI-TARS Desktop](https://github.com/bytedance/UI-TARS-desktop)** | Medium | 16 GB | Highest accuracy (94.2%), best Chinese UI support |
| **[OmniMCP](https://github.com/OpenAdaptAI/OmniMCP)** | Medium | 16 GB | Multi-LLM setups (LLM-agnostic) |

**Quick example** — no extra tools needed:
```
You:    "Take a screenshot with Snapshot, find the Connect button, and click it."
Claude:  1. Calls Snapshot() → sees the Flutter app screenshot
         2. Vision identifies "Connect" button at (520, 340)
         3. Calls Click(x=520, y=340)
```

For the complete guide with setup instructions, architecture diagrams, and comparison benchmarks, see **[docs/vision-guide.md](docs/vision-guide.md)**.

## Troubleshooting / FAQ

### Q: MCP server not starting?
**A:** Check Python version (requires 3.10+) and ensure no other service is using port 8090:
```bash
python --version
netstat -an | findstr :8090
```

### Q: Can't connect from remote machine?
**A:** Use `--host 0.0.0.0` to bind to all interfaces (default is localhost only):
```bash
winremote-mcp --host 0.0.0.0 --auth-key "secure-key"
```

### Q: Screenshot tool returns empty/black images?
**A:** Windows may be locked or display turned off. Ensure:
- Windows is unlocked and display is active
- No screen saver is running
- For multi-monitor setups, specify `monitor` parameter

### Q: OCR not working?
**A:** Install Tesseract OCR engine:
```bash
winget install UB-Mannheim.TesseractOCR
pip install winremote-mcp[ocr]
```

### Q: Permission errors with registry/services?
**A:** Run with administrator privileges:
```bash
# Right-click Command Prompt → "Run as administrator"
winremote-mcp
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/dddabtc/winremote-mcp.git
cd winremote-mcp
pip install -e ".[test]"
pytest  # Run tests
```

## Acknowledgments

Inspired by [Windows-MCP](https://github.com/CursorTouch/Windows-MCP) by CursorTouch. Thanks for the pioneering work on Windows desktop automation via MCP.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Ready to automate Windows with AI?** ⚡ Install `winremote-mcp` and connect your favorite AI agent to any Windows machine in under 30 seconds.
