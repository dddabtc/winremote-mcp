"""Unit tests for Shell, Scrape, App tools."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def _call_tool(tool_name, **kwargs):
    from winremote.__main__ import mcp
    tool = mcp._tool_manager._tools[tool_name]
    return tool.fn(**kwargs)


class TestShell:
    @patch("subprocess.run")
    def test_shell_success(self, mock_run):
        mock_run.return_value = MagicMock(stdout="hello", stderr="", returncode=0)
        result = _call_tool("Shell", command="echo hello")
        assert "hello" in result

    @patch("subprocess.run")
    def test_shell_stderr(self, mock_run):
        mock_run.return_value = MagicMock(stdout="", stderr="error msg", returncode=1)
        result = _call_tool("Shell", command="bad")
        assert "STDERR" in result or "error" in result.lower()

    @patch("subprocess.run")
    def test_shell_timeout(self, mock_run):
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)
        result = _call_tool("Shell", command="long", timeout=30)
        assert "timed out" in result.lower()


class TestScrape:
    @patch("urllib.request.urlopen")
    def test_scrape_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"<html><body><h1>Hello</h1></body></html>"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp
        result = _call_tool("Scrape", url="https://example.com")
        assert "Hello" in result or "task:" in result

    def test_scrape_error(self):
        with patch("urllib.request.urlopen", side_effect=Exception("network error")):
            result = _call_tool("Scrape", url="https://bad.url")
            assert "error" in result.lower()


class TestApp:
    @patch("winremote.__main__.desktop")
    def test_app_launch(self, mock_desktop):
        mock_desktop.launch_app.return_value = "Launched notepad"
        result = _call_tool("App", action="launch", name="notepad")
        assert "Launched" in result or "task:" in result

    def test_app_unknown_action(self):
        result = _call_tool("App", action="unknown")
        assert "Unknown" in result or "task:" in result
