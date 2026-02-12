# Security Guide

winremote-mcp exposes powerful Windows automation capabilities. This guide covers the security model, risk levels, and deployment best practices.

## Quick Start

```bash
# Safe: localhost only, read-only tools
winremote-mcp

# Remote access: ALWAYS use auth + firewall
winremote-mcp --host 0.0.0.0 --auth-key "$(openssl rand -hex 32)"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  AI Agent / MCP Client                                      │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/MCP Protocol
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  winremote-mcp server                                       │
│  ├─ Auth middleware (--auth-key)                           │
│  ├─ IP allowlist middleware (--ip-allowlist)               │
│  ├─ Tool controls (--enable-tier3/--disable-tier2/--tools) │
│  └─ Rate limiting [planned]                                │
└──────────────────────────┬──────────────────────────────────┘
                           │ pyautogui / pywin32 / subprocess
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Windows Desktop Session                                    │
│  ├─ GUI (mouse, keyboard, screenshots)                     │
│  ├─ File System                                            │
│  ├─ Registry                                               │
│  ├─ Services & Scheduled Tasks                             │
│  └─ PowerShell                                             │
└─────────────────────────────────────────────────────────────┘
```

## Tool Risk Tiers

All 43 tools are categorized into 3 risk tiers:

### Tier 1 — Read-Only (Low Risk) ✅ Default: Enabled

Safe, non-destructive tools that only observe the system.

| Tool | Description |
|------|-------------|
| `Snapshot` | Screenshot + window list |
| `AnnotatedSnapshot` | Screenshot with UI element labels |
| `GetClipboard` | Read clipboard content |
| `GetSystemInfo` | CPU, memory, disk, uptime |
| `ListProcesses` | Running processes |
| `FileList` | Directory listing |
| `FileSearch` | Find files by pattern |
| `RegRead` | Read registry values |
| `ServiceList` | Windows services status |
| `TaskList` | Scheduled tasks |
| `EventLog` | Windows event viewer |
| `Ping` | Network reachability |
| `PortCheck` | TCP port status |
| `NetConnections` | Active connections |
| `OCR` | Screen text extraction |
| `ScreenRecord` | Capture screen as GIF |
| `Notification` | Show toast (no system change) |
| `Wait` | Pause execution |
| `GetTaskStatus` | Internal task management |
| `GetRunningTasks` | Internal task management |

### Tier 2 — Interactive (Medium Risk) ✅ Default: Enabled

Desktop interaction tools. Can click, type, and control windows but cannot execute arbitrary code or modify system files.

| Tool | Description | Risk |
|------|-------------|------|
| `Click` | Mouse click at coordinates | UI manipulation |
| `Type` | Keyboard input | UI manipulation |
| `Move` | Mouse move/drag | UI manipulation |
| `Scroll` | Scroll wheel | UI manipulation |
| `Shortcut` | Keyboard shortcuts | Could trigger system actions |
| `FocusWindow` | Bring window to front | Window control |
| `MinimizeAll` | Show desktop | Window control |
| `App` | Launch/resize apps | Starts programs |
| `Scrape` | Fetch URL content | Network access (read-only) |
| `CancelTask` | Cancel running task | Internal management |

### Tier 3 — Destructive (High Risk) ⚠️ Default: Disabled

Tools that can modify files, execute code, or alter system state. Enable only when needed.

| Tool | Description | Risk |
|------|-------------|------|
| `Shell` | Execute PowerShell | **Arbitrary code execution** |
| `FileRead` | Read any file | Sensitive data exposure |
| `FileWrite` | Write any file | Data modification/loss |
| `FileDownload` | Export files (base64) | Data exfiltration |
| `FileUpload` | Import files (base64) | Malware upload |
| `KillProcess` | Terminate processes | Service disruption |
| `RegWrite` | Modify registry | System instability |
| `ServiceStart` | Start services | Security implications |
| `ServiceStop` | Stop services | Service disruption |
| `TaskCreate` | Create scheduled task | Persistence mechanism |
| `TaskDelete` | Delete scheduled task | Remove security tools |
| `SetClipboard` | Modify clipboard | Data injection |
| `LockScreen` | Lock workstation | Denial of access |

## Authentication

### Bearer Token Auth

```bash
# Set via CLI
winremote-mcp --auth-key "my-secret-key"

# Or environment variable
export WINREMOTE_AUTH_KEY="my-secret-key"
winremote-mcp
```

Clients must include the header:
```
Authorization: Bearer my-secret-key
```

The `/health` endpoint is always public (for monitoring).

### IP Allowlist

Restrict which client IPs can access MCP endpoints:

```bash
# Allow only localhost + one LAN subnet
winremote-mcp --ip-allowlist 127.0.0.1/32,192.168.1.0/24
```

- Supports single IPs and CIDR ranges (IPv4/IPv6)
- Non-allowlisted clients receive `403 Forbidden`
- `/health` remains accessible for monitoring

### Generating Strong Keys

```bash
# 32-byte hex (64 chars)
openssl rand -hex 32

# Or use Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Network Security

### Binding Address

| Flag | Access | Use Case |
|------|--------|----------|
| (default) | `127.0.0.1` | Local only, safest |
| `--host 0.0.0.0` | All interfaces | Remote access |

### Firewall Rules (Windows)

```powershell
# Allow only specific IP
New-NetFirewallRule -DisplayName "winremote-mcp" `
  -Direction Inbound -LocalPort 8090 -Protocol TCP `
  -RemoteAddress 192.168.1.100 -Action Allow

# Block all others
New-NetFirewallRule -DisplayName "winremote-mcp-block" `
  -Direction Inbound -LocalPort 8090 -Protocol TCP `
  -Action Block
```

### Reverse Proxy with TLS (Recommended)

For production deployments, use nginx/caddy as a reverse proxy:

```nginx
# nginx example
server {
    listen 443 ssl;
    server_name winremote.internal;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8090;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Config File Security (winremote.toml)

You can store security settings in config, with precedence:

**CLI flags > config file > defaults**

```toml
[security]
auth_key = "change-me"
ip_allowlist = ["127.0.0.1/32", "192.168.1.0/24"]
enable_tier3 = false
disable_tier2 = false
```

## Deployment Scenarios

### 1. Local Development (Recommended)

```bash
winremote-mcp
# Binds to 127.0.0.1:8090, no auth needed
```

**Risk**: Minimal — only local processes can connect.

### 2. Home Lab / Trusted LAN

```bash
winremote-mcp --host 0.0.0.0 --auth-key "$SECRET"
```

- ✅ Auth key required
- ✅ Firewall allows only your devices
- ⚠️ Anyone on LAN with the key has full access

### 3. Production / Untrusted Network

```bash
# On Windows
winremote-mcp --host 127.0.0.1 --auth-key "$SECRET"

# TLS termination at reverse proxy
caddy reverse-proxy --from :443 --to :8090
```

- ✅ TLS encryption
- ✅ Auth key
- ✅ Consider VPN/WireGuard for additional layer
- ⚠️ Disable Tier 3 tools if possible

### 4. Air-Gapped / Isolated Network

If the Windows machine is on a separate VLAN with no internet access:

```bash
winremote-mcp --host 0.0.0.0 --auth-key "$SECRET"
```

- Network segmentation provides isolation
- Still use auth key (defense in depth)

## Known Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Shell command injection | Critical | Disable `Shell` tool if not needed |
| Credential theft via FileRead | High | Disable Tier 3 file tools |
| Screenshot data leakage | Medium | Network encryption (TLS) |
| Keystroke injection attacks | Medium | Restrict Tier 2 in untrusted scenarios |
| Denial of service | Low | Rate limiting (planned) |

## Security Checklist

Before deploying:

- [ ] Using strong auth key (32+ chars)?
- [ ] Binding to localhost or specific interface?
- [ ] Firewall restricting access?
- [ ] TLS enabled (via reverse proxy)?
- [ ] Tier 3 tools disabled (if not needed)?
- [ ] Running under least-privilege user account?
- [ ] Audit logging enabled (if compliance required)?

## Reporting Vulnerabilities

Found a security issue? Please report privately:

1. **Email**: Create an issue titled "Security" on GitHub (we'll provide a private contact)
2. **Do not** post exploits or vulnerabilities publicly
3. We aim to respond within 48 hours

## Roadmap

Security features planned for future releases:

- [ ] `--enable-tier3` / `--disable-tier2` CLI flags
- [ ] `--tools snapshot,click,type` granular tool selection
- [ ] Environment variable: `WINREMOTE_ENABLED_TOOLS`
- [ ] Config file support (`winremote.toml`)
- [ ] Per-tool rate limiting
- [ ] IP allowlist
- [ ] Audit logging to file/syslog
- [ ] Session timeouts
- [ ] Tool usage statistics

---

**Remember**: winremote-mcp is designed for trusted environments. The combination of desktop control + shell access is extremely powerful. Always apply the principle of least privilege.
