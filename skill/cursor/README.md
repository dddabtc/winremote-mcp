# winremote-mcp for Cursor

## Setup

### 1. Install on Windows

```bash
pip install winremote-mcp
```

### 2. Configure Cursor

Create `.cursor/mcp.json` in your project root:

**Local (same machine):**
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

**Remote:**
```bash
# Start server on Windows first:
python -m winremote --auth-key "your-secret-key"
```

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

### 3. Verify

After adding the config, restart Cursor. You should see winremote tools available in the MCP tools panel.

## Use Cases in Cursor

- **UI testing** — Use `Snapshot` + `Click` + `Type` to automate UI testing
- **Desktop automation** — Launch apps, manage windows, interact with desktop
- **System debugging** — Check processes, services, event logs, network connections
- **File operations** — Read/write files on the Windows machine
- **Screen capture** — Take annotated screenshots for documentation
