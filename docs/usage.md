# Usage Guide

## Starting the Server

### Basic Usage

```bash
# Start MCP server (localhost only)
winremote-mcp

# Start with custom port
winremote-mcp --port 8091

# Start with hot reload (development)
winremote-mcp --reload
```

### Remote Access

```bash
# Enable remote access with authentication
winremote-mcp --host 0.0.0.0 --auth-key "your-secret-key"

# Custom port and auth
winremote-mcp --host 0.0.0.0 --port 8090 --auth-key "secure-token-123"
```

### Environment Variables

```bash
# Set auth key via environment
set WINREMOTE_AUTH_KEY=my-secret-key
winremote-mcp --host 0.0.0.0

# Linux/macOS style
export WINREMOTE_AUTH_KEY=my-secret-key
winremote-mcp --host 0.0.0.0
```

## MCP Client Configuration

### Claude Desktop

Edit your `claude_desktop_config.json`:

**Local (stdio transport):**
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

**Remote (HTTP transport):**
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

### OpenClaw

Add to your OpenClaw skill configuration:

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

### Cursor

Create/edit `.cursor/mcp.json` in your project:

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

## Common Usage Examples

### Basic Desktop Automation

```python
# Example MCP client commands (via Claude/AI agent):

# Take a screenshot
"Take a screenshot of the current desktop"

# Click at specific coordinates  
"Click at position 500, 300"

# Type text
"Type 'Hello World' at the current cursor position"

# Use keyboard shortcuts
"Press Ctrl+C to copy"

# Launch application
"Open notepad"
```

### File Operations

```python
# Read a file
"Read the contents of C:\\Users\\username\\Desktop\\notes.txt"

# Write to a file
"Write 'New content' to C:\\temp\\output.txt"

# List directory contents
"List all files in C:\\Users\\username\\Documents"

# Search for files
"Find all .pdf files in C:\\Documents"
```

### System Administration

```python
# Get system information
"Show current system information including CPU and memory usage"

# List running processes
"List all running processes with CPU and memory usage"

# Manage Windows services
"List all Windows services"
"Start the Windows Update service"
"Stop the Windows Update service"

# Registry operations
"Read the registry key HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion"
"Set registry value HKEY_CURRENT_USER\\Software\\MyApp\\Setting to 'value'"
```

### Advanced Features

```python
# OCR text extraction
"Extract text from the screen region at coordinates 100,100 to 500,400"

# Screen recording
"Record a 5-second screen recording as an animated GIF"

# Annotated screenshot
"Take an annotated screenshot showing numbered labels on all clickable elements"

# Multi-monitor support  
"Take a screenshot of monitor 2"
```

## Auto-Start Configuration

### Windows Scheduled Task

```bash
# Install as Windows scheduled task (runs on startup)
winremote-mcp install

# Remove scheduled task
winremote-mcp uninstall

# Check if installed
winremote-mcp status
```

The scheduled task runs with these default settings:
- **Trigger**: At system startup
- **User**: Current user account
- **Command**: `winremote-mcp --host 127.0.0.1`

### Custom Auto-Start

Create a batch file for custom startup:

```batch
@echo off
cd /d "C:\path\to\your\project"
winremote-mcp --host 0.0.0.0 --auth-key "your-key" --port 8090
pause
```

Add this batch file to Windows startup folder:
- Press `Win+R`, type `shell:startup`, press Enter
- Copy your batch file to the opened folder

## Security Best Practices

### Network Security

```bash
# ✅ Good: Localhost only (default)
winremote-mcp

# ✅ Good: Remote with authentication
winremote-mcp --host 0.0.0.0 --auth-key "strong-random-key-123"

# ❌ Bad: Remote without authentication
winremote-mcp --host 0.0.0.0  # Anyone on network has full access!
```

### Authentication

```bash
# Generate strong auth key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Use environment variable (recommended)
set WINREMOTE_AUTH_KEY=xvYz9pQmN4kLwR2sE8tU6vX1cF3nH7bA

# Start with auth
winremote-mcp --host 0.0.0.0
```

### Firewall Configuration

Windows Defender Firewall rules:
```powershell
# Allow on private networks only
netsh advfirewall firewall add rule name="WinRemote MCP" dir=in action=allow protocol=TCP localport=8090 profile=private

# Block on public networks
netsh advfirewall firewall add rule name="WinRemote MCP Block Public" dir=in action=block protocol=TCP localport=8090 profile=public
```

## Health Monitoring

### Health Endpoint

```bash
# Check server status
curl http://localhost:8090/health

# Expected response
{"status":"ok","version":"0.4.4"}
```

### Task Management

```python
# Monitor running tasks (via MCP client)
"Show all currently running tasks"
"Get status of task abc123"
"Cancel task def456"
```

## Performance Optimization

### Concurrency Settings

WinRemote MCP automatically manages concurrency:
- **Desktop tools** (mouse, keyboard, screenshot): Exclusive (one at a time)
- **File tools**: Up to 3 concurrent
- **Query tools** (processes, system info): Up to 5 concurrent
- **Shell tools**: Up to 2 concurrent
- **Network tools**: Up to 3 concurrent

### Memory Management

```bash
# Monitor memory usage
winremote-mcp --debug  # Shows detailed memory stats

# Reduce memory for large screenshots
# Request max_width parameter: "Take a screenshot with max width 1920"
```

## Troubleshooting

### Connection Issues

```bash
# Test local connection
curl http://localhost:8090/health

# Test remote connection  
curl http://192.168.1.100:8090/health

# Test with authentication
curl -H "Authorization: Bearer your-key" http://192.168.1.100:8090/health
```

### Common Problems

| Problem | Solution |
|---------|----------|
| `Server not responding` | Check if port 8090 is blocked by firewall |
| `Authentication failed` | Verify `Authorization: Bearer <key>` header |
| `Screenshot is black` | Ensure Windows is unlocked and display active |
| `Permission denied` | Run as Administrator for registry/service operations |
| `OCR not working` | Install Tesseract: `winget install UB-Mannheim.TesseractOCR` |

### Debug Mode

```bash
# Enable detailed logging
winremote-mcp --debug

# Check logs for errors
winremote-mcp --debug 2>&1 | tee winremote.log
```

## Integration Examples

See our ready-to-use configurations:

- **[Claude Desktop](https://github.com/dddabtc/winremote-mcp/tree/master/skill/claude)**: Complete setup guide
- **[OpenClaw](https://github.com/dddabtc/winremote-mcp/tree/master/skill/openclaw)**: Full skill package  
- **[Cursor](https://github.com/dddabtc/winremote-mcp/tree/master/skill/cursor)**: `.cursor/mcp.json` config