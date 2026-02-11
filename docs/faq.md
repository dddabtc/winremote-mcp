# Frequently Asked Questions

## General Questions

### What is WinRemote MCP?

WinRemote MCP is a Model Context Protocol (MCP) server that enables AI agents and applications to remotely control Windows desktops. It provides 40+ tools for desktop automation, file operations, system administration, and more.

### How is this different from RDP or VNC?

Unlike screen sharing solutions:
- **API-based**: Structured commands instead of pixel streaming
- **AI-optimized**: Perfect for AI agents and automation scripts  
- **Lightweight**: Much lower bandwidth and resource usage
- **Programmatic**: Easy integration with code and workflows

### Is WinRemote MCP safe to use?

Yes, when used properly:
- **Localhost-only by default** - no external network access
- **Optional authentication** with Bearer tokens
- **Tool-level error handling** prevents crashes
- **Open source** - audit the code yourself

⚠️ **Important**: Only enable remote access (`--host 0.0.0.0`) with authentication (`--auth-key`) on trusted networks.

## Installation & Setup

### Q: Installation fails with "Python 3.9 is not supported"

**A:** WinRemote MCP requires Python 3.10 or higher.

```bash
# Check your Python version
python --version

# Install Python 3.11 (recommended)
winget install Python.Python.3.11

# Or download from python.org
```

### Q: "ModuleNotFoundError: No module named 'win32api'"

**A:** Install Windows-specific dependencies:

```bash
pip install pywin32
```

If this doesn't work:
```bash
pip uninstall pywin32
pip install pywin32==306
python Scripts/pywin32_postinstall.py -install
```

### Q: OCR not working - "TesseractNotFoundError"

**A:** Install Tesseract OCR engine:

```bash
# Method 1: Winget (recommended)
winget install UB-Mannheim.TesseractOCR

# Method 2: Manual download
# Go to https://github.com/UB-Mannheim/tesseract/wiki
# Download and install the Windows installer

# Then install Python package
pip install winremote-mcp[ocr]
```

### Q: Can I install this without administrator rights?

**A:** Yes, for basic functionality:

```bash
# Install to user directory
pip install --user winremote-mcp

# Run with limited permissions (no registry/service access)
winremote-mcp
```

Some tools (registry, services, scheduled tasks) require administrator privileges.

## Server Configuration

### Q: How do I enable remote access?

**A:** Use `--host 0.0.0.0` with authentication:

```bash
# Generate a strong auth key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Start with remote access
winremote-mcp --host 0.0.0.0 --auth-key "your-generated-key"
```

Never use `--host 0.0.0.0` without `--auth-key` on untrusted networks.

### Q: Can I change the default port (8090)?

**A:** Yes:

```bash
winremote-mcp --port 8091
```

Choose a port not used by other services. Common alternatives: 8080, 8000, 9090.

### Q: How do I run WinRemote MCP on startup?

**A:** Several options:

**Option 1: Scheduled Task (recommended)**
```bash
winremote-mcp install  # Creates Windows scheduled task
```

**Option 2: Startup Folder**
1. Press `Win+R`, type `shell:startup`
2. Create a batch file with: `winremote-mcp --host 127.0.0.1`

**Option 3: Windows Service**
Use tools like `nssm` to run as a Windows service.

### Q: Server starts but I can't connect from MCP clients

**A:** Check these common issues:

1. **Firewall blocking**: Allow port 8090 in Windows Defender
2. **Wrong URL**: Use `http://localhost:8090/mcp` (not just the port)
3. **Authentication**: Include `Authorization: Bearer your-key` header
4. **Server not running**: Check `curl http://localhost:8090/health`

## MCP Client Integration

### Q: How do I configure Claude Desktop?

**A:** Edit `claude_desktop_config.json`:

**Local connection (stdio):**
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

**Remote connection (HTTP):**
```json
{
  "mcpServers": {
    "winremote": {
      "type": "streamable-http", 
      "url": "http://192.168.1.100:8090/mcp",
      "headers": {
        "Authorization": "Bearer your-key"
      }
    }
  }
}
```

### Q: OpenClaw can't connect to WinRemote MCP

**A:** Ensure OpenClaw is configured for HTTP transport:

```json
{
  "mcpServers": {
    "winremote": {
      "type": "streamable-http",
      "url": "http://localhost:8090/mcp"
    }
  }
}
```

Check that WinRemote MCP is running with: `curl http://localhost:8090/health`

### Q: Cursor integration not working

**A:** Create `.cursor/mcp.json` in your project root:

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

Restart Cursor after creating the file.

## Tool Usage Issues

### Q: Screenshots are black or empty

**A:** Common causes and solutions:

- **Windows is locked**: Unlock the computer
- **Display turned off**: Wake up the display
- **Screen saver active**: Disable or wake up
- **Running as service**: Services can't capture desktop, run as user
- **Multi-monitor setup**: Specify `monitor` parameter

### Q: Mouse clicks not working accurately

**A:** Check these factors:

- **DPI scaling**: Windows display scaling affects coordinates
- **Multi-monitor**: Coordinates are relative to primary monitor
- **Window focus**: Target window must be visible and active
- **Screen resolution**: Use current resolution for coordinates

**Debug tip**: Take a screenshot first to see current state and coordinates.

### Q: Keyboard shortcuts not working

**A:** Common issues:

- **Application not focused**: Use `FocusWindow` first
- **Key format**: Use lowercase with `+` (e.g., `ctrl+c`, not `Ctrl+C`)
- **Timing**: Some apps need delays between keystrokes
- **UAC prompts**: Administrator prompts block automation

**Valid shortcut examples:**
- `ctrl+c`, `ctrl+v`, `ctrl+z`
- `alt+tab`, `alt+f4`
- `win+r`, `win+l`
- `shift+f10`, `f11`

### Q: File operations fail with permission errors

**A:** Solutions:

1. **Run as Administrator**: Right-click Command Prompt → "Run as administrator"
2. **Check file permissions**: Ensure the file isn't read-only or locked
3. **Use full paths**: Avoid relative paths that might resolve incorrectly
4. **File in use**: Close applications that might have the file open

### Q: PowerShell commands timeout

**A:** Increase timeout or optimize commands:

```json
{
  "tool": "Shell",
  "arguments": {
    "command": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10",
    "timeout": 60
  }
}
```

For long-running commands, consider running them in the background.

## Performance & Optimization

### Q: Screenshots are too large/slow

**A:** Use compression parameters:

```json
{
  "tool": "Snapshot",
  "arguments": {
    "quality": 70,
    "max_width": 1920
  }
}
```

Lower quality (50-80) and smaller max_width reduce file size significantly.

### Q: Too many concurrent tasks causing issues

**A:** WinRemote MCP automatically limits concurrency:

- Desktop tools (mouse, keyboard): 1 at a time
- File operations: up to 3 concurrent
- System queries: up to 5 concurrent

Use task management tools:
```python
# Check running tasks
"Show all running tasks"

# Cancel if needed  
"Cancel task abc123"
```

### Q: Memory usage keeps growing

**A:** This typically happens with:

- **Large screenshots**: Use `max_width` parameter
- **File transfers**: Large base64 file operations
- **Long-running shell commands**: Set appropriate timeouts

Restart the server periodically if memory usage becomes problematic.

## Security & Network

### Q: Is it safe to expose WinRemote MCP to the internet?

**A:** **No, not recommended.** WinRemote MCP is designed for:
- Local development (127.0.0.1)
- Trusted networks (home/office LAN)  
- VPN connections

If you must expose it:
1. Use strong authentication: `--auth-key "$(python -c 'import secrets; print(secrets.token_urlsafe(32))')`
2. Use a reverse proxy with TLS (nginx/Caddy)
3. Implement IP restrictions
4. Monitor access logs

### Q: How do I secure remote access?

**A:** Security layers:

**1. Strong Authentication:**
```bash
# Generate cryptographically secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"
winremote-mcp --host 0.0.0.0 --auth-key "generated-key"
```

**2. Firewall Rules:**
```powershell
# Allow only private networks
netsh advfirewall firewall add rule name="WinRemote MCP" dir=in action=allow protocol=TCP localport=8090 profile=private

# Block public networks  
netsh advfirewall firewall add rule name="WinRemote Block Public" dir=in action=block protocol=TCP localport=8090 profile=public
```

**3. Reverse Proxy (nginx example):**
```nginx
server {
    listen 443 ssl;
    server_name winremote.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8090;
        proxy_set_header Authorization "Bearer your-key";
    }
}
```

### Q: Can I limit what tools are available?

**A:** Currently, all 40+ tools are available when the server starts. Per-tool permissions are planned for a future release.

Workaround: Run separate instances with different authentication keys for different use cases.

## Troubleshooting

### Q: Server won't start - "Address already in use"

**A:** Another service is using port 8090:

```bash
# Find what's using the port
netstat -ano | findstr :8090

# Kill the process (replace PID)
taskkill /PID 1234 /F

# Or use a different port
winremote-mcp --port 8091
```

### Q: "Access denied" errors for registry/services

**A:** Run with administrator privileges:

1. Right-click Command Prompt or PowerShell
2. Select "Run as administrator"  
3. Run `winremote-mcp`

### Q: Tools return "Task failed" without details

**A:** Enable debug mode:

```bash
winremote-mcp --debug
```

This provides detailed error messages and stack traces.

### Q: Client can connect but tools don't work

**A:** Check Windows version compatibility:

- **Minimum**: Windows 10
- **Recommended**: Windows 11
- **Server editions**: Basic support (some GUI tools may not work)

### Q: Performance is slow on older hardware

**A:** Optimization tips:

1. **Reduce screenshot quality**: Use `quality: 60-80`
2. **Limit concurrent tasks**: Most are already limited automatically
3. **Use smaller regions**: For OCR and screen recording
4. **Close unnecessary applications**: Free up system resources

## Getting Help

### Still having issues?

1. **Check the logs**: Run with `--debug` for detailed output
2. **Search GitHub issues**: [github.com/dddabtc/winremote-mcp/issues](https://github.com/dddabtc/winremote-mcp/issues)
3. **File a bug report**: Include OS version, Python version, and error messages
4. **Community support**: Discussion forum in GitHub Discussions

### Useful diagnostic commands:

```bash
# System info
winremote-mcp --version
python --version
curl http://localhost:8090/health

# Network test
netstat -ano | findstr :8090
telnet localhost 8090

# Permissions test  
whoami /priv
```