# WinRemote MCP — Run MCP Servers Remotely on Windows

[![PyPI version](https://img.shields.io/pypi/v/winremote-mcp)](https://pypi.org/project/winremote-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/winremote-mcp)](https://pypi.org/project/winremote-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/dddabtc/winremote-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/dddabtc/winremote-mcp/actions/workflows/ci.yml)

**The ultimate Windows MCP server for remote desktop control and automation.** Control any Windows machine through the Model Context Protocol — perfect for AI agents, Claude Desktop, and OpenClaw integration. Transform your Windows desktop into a powerful, remotely-accessible automation endpoint.

Run **on the Windows machine** you want to control. Built with [FastMCP](https://github.com/jlowin/fastmcp) and the [Model Context Protocol](https://modelcontextprotocol.io/).

## Quickstart (30 seconds)

```bash
# Install from PyPI
pip install winremote-mcp

# Start the Windows MCP server
winremote-mcp
```

That's it! Your Windows MCP server is now running on `http://127.0.0.1:8090` and ready to accept commands from MCP clients like Claude Desktop or OpenClaw.

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
```bash
# Start MCP server (localhost only, no auth)
winremote-mcp

# Start with remote access and authentication
winremote-mcp --host 0.0.0.0 --port 8090 --auth-key "your-secret-key"

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

**For OpenClaw or other HTTP MCP clients:**
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

## How It Works

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │    │  WinRemote MCP   │    │  Windows APIs   │
│  (Claude/AI)    │───▶│     Server       │───▶│ (Win32/WMI/PS)  │
│                 │    │                  │    │                 │
│ • Send commands │    │ • HTTP/stdio     │    │ • Screenshot    │
│ • Get results   │◀───│ • Auth & routing │◀───│ • Mouse/Keys    │
│ • Stream data   │    │ • Task mgmt      │    │ • File/Registry │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**Transport Options:**
- **stdio**: Direct process communication (ideal for Claude Desktop)
- **HTTP**: RESTful API with optional authentication (ideal for remote access)

**Core Architecture:**
1. **Tool Layer**: 40+ Windows automation tools (screenshot, click, type, etc.)
2. **Task Manager**: Concurrency control and task cancellation
3. **Transport Layer**: MCP protocol over stdio or HTTP
4. **Security Layer**: Optional Bearer token authentication

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