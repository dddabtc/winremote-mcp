"""Unit tests for desktop control tools (Click, Type, Scroll, Move, Shortcut, Wait, etc.)."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pyautogui
import pytest

# The MCP tools are wrapped by task_manager; access the original functions
# via the module-level function objects before they're decorated, or call .fn
# Actually, the functions in __main__ are replaced by FunctionTool after @mcp.tool.
# We need to access the underlying function. Let's import and call the wrapped fn.


def _call_tool(tool_name, **kwargs):
    """Call an MCP tool by name, going through the task-manager-wrapped fn."""
    from winremote.__main__ import mcp
    tool = mcp._tool_manager._tools[tool_name]
    return tool.fn(**kwargs)


class TestClick:
    def test_left_click(self):
        result = _call_tool("Click", x=100, y=200)
        assert "Clicked left at (100,200)" in result

    def test_right_click(self):
        result = _call_tool("Click", x=50, y=60, button="right")
        assert "right" in result

    def test_double_click(self):
        result = _call_tool("Click", x=10, y=20, action="double")
        assert "Double-clicked" in result

    def test_hover(self):
        result = _call_tool("Click", x=300, y=400, action="hover")
        assert "Hovered" in result

    def test_click_error(self):
        pyautogui.click.side_effect = Exception("display error")
        result = _call_tool("Click", x=0, y=0)
        assert "error" in result.lower()
        pyautogui.click.side_effect = None


class TestType:
    def test_basic_type(self):
        result = _call_tool("Type", text="hello")
        assert "Typed 5 chars" in result

    def test_type_at_coords(self):
        _call_tool("Type", text="abc", x=100, y=200)
        pyautogui.click.assert_called_with(100, 200)

    def test_type_with_clear(self):
        _call_tool("Type", text="new", clear=True)
        pyautogui.hotkey.assert_called_with("ctrl", "a")

    def test_type_with_enter(self):
        _call_tool("Type", text="cmd", press_enter=True)
        pyautogui.press.assert_called_with("enter")

    def test_type_unicode(self):
        result = _call_tool("Type", text="你好")
        assert "Typed 2 chars" in result


class TestScroll:
    def test_vertical_scroll(self):
        result = _call_tool("Scroll", amount=3)
        assert "vertically" in result

    def test_horizontal_scroll(self):
        result = _call_tool("Scroll", amount=-2, horizontal=True)
        assert "horizontally" in result

    def test_scroll_at_position(self):
        _call_tool("Scroll", amount=5, x=100, y=200)
        pyautogui.moveTo.assert_called_with(100, 200)


class TestMove:
    def test_move(self):
        result = _call_tool("Move", x=500, y=600)
        assert "Moved to (500,600)" in result

    def test_drag(self):
        result = _call_tool("Move", x=700, y=800, drag=True, start_x=100, start_y=100)
        assert "Dragged" in result


class TestShortcut:
    def test_shortcut(self):
        result = _call_tool("Shortcut", keys="ctrl+c")
        assert "Executed shortcut" in result

    def test_complex_shortcut(self):
        _call_tool("Shortcut", keys="ctrl+shift+s")
        pyautogui.hotkey.assert_called_with("ctrl", "shift", "s")


class TestWait:
    def test_wait(self):
        with patch("time.sleep") as mock_sleep:
            result = _call_tool("Wait", seconds=0.01)
            assert "Waited" in result


class TestMinimizeAll:
    def test_minimize_all(self):
        result = _call_tool("MinimizeAll")
        assert "Minimized" in result or "task:" in result


class TestFocusWindow:
    def test_no_win32(self):
        with patch("winremote.__main__.desktop") as mock_desktop:
            mock_desktop.HAS_WIN32 = False
            result = _call_tool("FocusWindow", title="notepad")
            assert "pywin32" in result or "Error" in result

    def test_with_title(self):
        with patch("winremote.__main__.desktop") as mock_desktop:
            mock_desktop.HAS_WIN32 = True
            mock_desktop.focus_window.return_value = "Focused window"
            result = _call_tool("FocusWindow", title="notepad")
            assert "Focused" in result or "task:" in result
