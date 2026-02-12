"""Tool tier definitions and access control."""

from __future__ import annotations

# Tool tier definitions based on security risk level
TOOL_TIERS: dict[str, set[str]] = {
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


def get_enabled_tools(
    enable_all: bool = False,
    disable_tier2: bool = False,
    tools: set[str] | None = None,
    exclude_tools: set[str] | None = None,
) -> set[str]:
    """Calculate the set of enabled tools based on options.
    
    Args:
        enable_all: Enable all tiers (including high-risk tier3 tools)
        disable_tier2: Disable interactive tools (Click, Type, etc.)
        tools: Explicit tool list overrides tiers
        exclude_tools: Tools to exclude from the enabled set
        
    Returns:
        Set of enabled tool names
    """
    if tools:
        # Explicit tool list overrides tiers
        enabled = tools
    else:
        enabled = TOOL_TIERS["tier1"].copy()
        if not disable_tier2:
            enabled |= TOOL_TIERS["tier2"]
        if enable_all:
            enabled |= TOOL_TIERS["tier3"]
    
    if exclude_tools:
        enabled -= exclude_tools
    
    return enabled


def filter_tools(mcp, enabled_tools: set[str]) -> dict[str, int]:
    """Remove tools not in the enabled set from the MCP server.
    
    Args:
        mcp: FastMCP instance
        enabled_tools: Set of tool names to keep enabled
        
    Returns:
        Dictionary with counts: {"enabled": int, "disabled": int, "total": int}
    """
    all_tools = list(mcp._tool_manager._tools.keys())
    total_count = len(all_tools)
    
    # Remove disabled tools
    for name in all_tools:
        if name not in enabled_tools:
            del mcp._tool_manager._tools[name]
    
    enabled_count = len(enabled_tools)
    disabled_count = total_count - enabled_count
    
    return {
        "enabled": enabled_count,
        "disabled": disabled_count, 
        "total": total_count
    }


def get_tier_names(enabled_tools: set[str]) -> list[str]:
    """Get list of enabled tier names based on tools.
    
    Args:
        enabled_tools: Set of enabled tool names
        
    Returns:
        List of enabled tier names (e.g., ["1", "2"] or ["1", "2", "3"])
    """
    enabled_tiers = []
    
    if TOOL_TIERS["tier1"] & enabled_tools:
        enabled_tiers.append("1")
    if TOOL_TIERS["tier2"] & enabled_tools:
        enabled_tiers.append("2") 
    if TOOL_TIERS["tier3"] & enabled_tools:
        enabled_tiers.append("3")
        
    return enabled_tiers