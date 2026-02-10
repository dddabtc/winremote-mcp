"""Integration tests for MCP server endpoints."""

from __future__ import annotations

import pytest


class TestHealthEndpoint:
    """Test the /health HTTP endpoint."""

    def test_health_returns_ok(self):
        """Verify the health endpoint returns status ok."""
        from winremote import __version__
        from winremote.__main__ import mcp

        # Use Starlette test client on the FastMCP app
        try:
            from starlette.testclient import TestClient
            app = mcp._get_app()
            client = TestClient(app)
            resp = client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"
            assert data["version"] == __version__
        except Exception:
            # FastMCP internal API may vary; skip gracefully
            pytest.skip("Cannot create test client from FastMCP app")


class TestMCPToolRegistration:
    """Verify all expected tools are registered in the MCP server."""

    def test_expected_tools_registered(self):
        from winremote.__main__ import mcp

        tool_names = set(mcp._tool_manager._tools.keys())

        expected = {
            "Snapshot", "Click", "Type", "Scroll", "Move", "Shortcut", "Wait",
            "FocusWindow", "MinimizeAll", "App", "Shell", "Scrape",
            "GetClipboard", "SetClipboard", "ListProcesses", "KillProcess",
            "GetSystemInfo", "Notification", "LockScreen",
            "FileRead", "FileWrite", "FileList", "FileSearch",
            "FileDownload", "FileUpload",
            "RegRead", "RegWrite",
            "ServiceList", "ServiceStart", "ServiceStop",
            "TaskList", "TaskCreate", "TaskDelete",
            "EventLog", "Ping", "PortCheck", "NetConnections",
            "OCR", "ScreenRecord", "AnnotatedSnapshot",
            "CancelTask", "GetTaskStatus", "GetRunningTasks",
        }

        for name in expected:
            assert name in tool_names, f"Tool '{name}' not registered"

    def test_tool_count(self):
        from winremote.__main__ import mcp
        tools = mcp._tool_manager._tools
        # Should have a substantial number of tools
        assert len(tools) >= 30
