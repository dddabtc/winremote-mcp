# Tool Tier Implementation Design

This document outlines the implementation plan for tool tier access controls.

## Overview

Allow users to control which tools are exposed via CLI flags, environment variables, or config file.

## Tool Tier Definitions

```python
TOOL_TIERS = {
    # Tier 1: Read-only (low risk, default enabled)
    "tier1": {
        "Snapshot", "AnnotatedSnapshot", "GetClipboard", "GetSystemInfo",
        "ListProcesses", "FileList", "FileSearch", "RegRead", "ServiceList",
        "TaskList", "EventLog", "Ping", "PortCheck", "NetConnections",
        "OCR", "ScreenRecord", "Notification", "Wait",
        "GetTaskStatus", "GetRunningTasks",
    },
    
    # Tier 2: Interactive (medium risk, default enabled)
    "tier2": {
        "Click", "Type", "Move", "Scroll", "Shortcut",
        "FocusWindow", "MinimizeAll", "App", "Scrape", "CancelTask",
    },
    
    # Tier 3: Destructive (high risk, default DISABLED)
    "tier3": {
        "Shell", "FileRead", "FileWrite", "FileDownload", "FileUpload",
        "KillProcess", "RegWrite", "ServiceStart", "ServiceStop",
        "TaskCreate", "TaskDelete", "SetClipboard", "LockScreen",
    },
}

DEFAULT_TIERS = {"tier1", "tier2"}  # tier3 disabled by default
```

## CLI Interface

```bash
# Enable tier 3 (all tiers active)
winremote-mcp --enable-tier3

# Disable tier 2 (only read-only tools)
winremote-mcp --disable-tier2

# Granular: specific tools only
winremote-mcp --tools Snapshot,Click,Type,GetSystemInfo

# Exclude specific tools
winremote-mcp --exclude-tools Shell,FileWrite

# Combine options
winremote-mcp --enable-tier3 --exclude-tools Shell
```

## Environment Variables

```bash
# Enable tier 3
WINREMOTE_ENABLE_TIER3=1 winremote-mcp

# Specific tools only
WINREMOTE_TOOLS=Snapshot,Click,Type winremote-mcp

# Exclude tools
WINREMOTE_EXCLUDE_TOOLS=Shell,FileWrite winremote-mcp
```

## Config File (winremote.toml)

```toml
# ~/.config/winremote/config.toml or ./winremote.toml

[security]
auth_key = "env:WINREMOTE_AUTH_KEY"  # reference env var
enable_tier3 = false
exclude_tools = ["Shell", "FileWrite"]

[server]
host = "127.0.0.1"
port = 8090

[logging]
audit_file = "/var/log/winremote/audit.log"  # optional
```

## Implementation Steps

### 1. Add tier registry (src/winremote/tiers.py)

```python
"""Tool tier definitions and access control."""

from __future__ import annotations

TOOL_TIERS: dict[str, set[str]] = {
    "tier1": {...},
    "tier2": {...},
    "tier3": {...},
}

def get_enabled_tools(
    enable_tier3: bool = False,
    disable_tier2: bool = False,
    tools: set[str] | None = None,
    exclude_tools: set[str] | None = None,
) -> set[str]:
    """Calculate the set of enabled tools based on options."""
    if tools:
        # Explicit tool list overrides tiers
        enabled = tools
    else:
        enabled = TOOL_TIERS["tier1"].copy()
        if not disable_tier2:
            enabled |= TOOL_TIERS["tier2"]
        if enable_tier3:
            enabled |= TOOL_TIERS["tier3"]
    
    if exclude_tools:
        enabled -= exclude_tools
    
    return enabled
```

### 2. Modify CLI (__main__.py)

```python
@click.option("--enable-tier3", is_flag=True, help="Enable high-risk tools (Shell, FileWrite, etc.)")
@click.option("--disable-tier2", is_flag=True, help="Disable interactive tools (Click, Type, etc.)")
@click.option("--tools", default="", help="Comma-separated list of tools to enable (overrides tiers)")
@click.option("--exclude-tools", default="", help="Comma-separated list of tools to disable")
def cli(ctx, transport, host, port, reload, auth_key, 
        enable_tier3, disable_tier2, tools, exclude_tools):
    ...
    enabled = get_enabled_tools(
        enable_tier3=enable_tier3,
        disable_tier2=disable_tier2,
        tools=set(tools.split(",")) if tools else None,
        exclude_tools=set(exclude_tools.split(",")) if exclude_tools else None,
    )
    
    # Filter mcp._tool_manager._tools
    filter_tools(mcp, enabled)
```

### 3. Filter tools at startup

```python
def filter_tools(mcp: FastMCP, enabled_tools: set[str]) -> None:
    """Remove tools not in the enabled set."""
    all_tools = list(mcp._tool_manager._tools.keys())
    for name in all_tools:
        if name not in enabled_tools:
            del mcp._tool_manager._tools[name]
    
    # Log what's active
    logging.info(f"Enabled {len(enabled_tools)} tools, disabled {len(all_tools) - len(enabled_tools)}")
```

### 4. Startup banner update

```
+----------------------------------+
|  winremote-mcp v0.5.0            |
|  by dddabtc                      |
|  github.com/dddabtc              |
|  [auth ON]                       |
|  [127.0.0.1:8090]                |
|  [tiers: 1,2] [tools: 30/43]     |  <-- NEW
+----------------------------------+
```

## Testing

```bash
# Test tier filtering
winremote-mcp --disable-tier2 &
curl http://localhost:8090/mcp -d '{"method":"tools/list"}' | jq '.result.tools[].name'
# Should NOT include Click, Type, etc.

# Test specific tools
winremote-mcp --tools Snapshot,GetSystemInfo &
curl http://localhost:8090/mcp -d '{"method":"tools/list"}' | jq '.result.tools | length'
# Should return 2
```

## Migration Notes

- Default behavior unchanged (tier1 + tier2 enabled)
- Tier 3 tools require explicit `--enable-tier3`
- Existing `--auth-key` behavior preserved
- Config file is optional, CLI flags take precedence

## Security Considerations

1. **Deny by default**: Tier 3 is off unless explicitly enabled
2. **Granular control**: `--tools` allows precise capability exposure
3. **Audit**: Log which tools are enabled at startup
4. **Validation**: Reject unknown tool names in `--tools` / `--exclude-tools`
