"""Unit tests for desktop control tools (Click, Type, Scroll, Move, Shortcut, Wait, etc.)."""

from __future__ import annotations

from unittest.mock import patch

import pyautogui

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
        with patch("time.sleep") as _mock_sleep:
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


class TestReconnectSession:
    def test_session_found_and_reconnected(self):
        with patch("winremote.__main__._ensure_session_connected") as mock_ensure:
            mock_ensure.return_value = None  # Success

            result = _call_tool("ReconnectSession")

            assert isinstance(result, list)
            assert len(result) == 1
            assert "connected to console" in result[0].text.lower()

    def test_session_already_connected(self):
        with patch("winremote.__main__._ensure_session_connected") as mock_ensure:
            mock_ensure.return_value = None  # Already connected

            result = _call_tool("ReconnectSession")

            assert isinstance(result, list)
            assert len(result) == 1
            assert "connected to console" in result[0].text.lower()

    def test_reconnect_failed(self):
        with patch("winremote.__main__._ensure_session_connected") as mock_ensure:
            mock_ensure.return_value = "Access denied"

            result = _call_tool("ReconnectSession")

            assert isinstance(result, list)
            assert len(result) == 1
            assert "failed" in result[0].text.lower()
            assert "access denied" in result[0].text.lower()

    def test_force_reconnect(self):
        from unittest.mock import MagicMock

        mock_result_query = MagicMock()
        mock_result_query.returncode = 0
        mock_result_query.stdout = """SESSIONNAME       USERNAME                 ID  STATE   TYPE        DEVICE
 console                                    0  Conn    wdcon
 rdp-tcp#0         testuser                 1  Active  rdpwd
"""

        mock_result_tscon = MagicMock()
        mock_result_tscon.returncode = 0

        with patch("winremote.__main__.subprocess.run") as mock_subprocess:
            mock_subprocess.side_effect = [mock_result_query, mock_result_tscon]

            result = _call_tool("ReconnectSession", force=True)

            assert isinstance(result, list)
            assert len(result) == 1
            assert "reconnected session" in result[0].text.lower()


class TestSnapshotAutoReconnect:
    def test_snapshot_screenshot_fails_then_succeeds_after_reconnect(self):
        with patch("winremote.__main__.desktop") as mock_desktop:
            # First call fails, second succeeds
            mock_desktop.take_screenshot.side_effect = [Exception("screen grab failed"), "base64data"]
            mock_desktop.enumerate_windows.return_value = []
            mock_desktop.get_interactive_elements.return_value = []
            mock_desktop._get_system_language.return_value = "en-US"

            with patch("winremote.__main__._ensure_session_connected") as mock_ensure:
                mock_ensure.return_value = None  # Success

                with patch("winremote.__main__.time.sleep"):
                    result = _call_tool("Snapshot")

                    # Should succeed after reconnect
                    assert isinstance(result, list)
                    # Should have called ensure_session_connected
                    mock_ensure.assert_called_once()
                    # Should have retried screenshot
                    assert mock_desktop.take_screenshot.call_count == 2

    def test_snapshot_non_screen_error_not_retried(self):
        with patch("winremote.__main__.desktop") as mock_desktop:
            # Non-screen-related error should not trigger reconnect
            mock_desktop.take_screenshot.side_effect = Exception("some other error")

            result = _call_tool("Snapshot")

            assert isinstance(result, list)
            assert len(result) == 1
            assert "error" in result[0].lower()

    def test_snapshot_reconnect_fails(self):
        with patch("winremote.__main__.desktop") as mock_desktop:
            mock_desktop.take_screenshot.side_effect = Exception("screen grab failed")

            with patch("winremote.__main__._ensure_session_connected") as mock_ensure:
                mock_ensure.return_value = "Failed to reconnect"

                result = _call_tool("Snapshot")

                assert isinstance(result, list)
                assert len(result) == 1
                assert "auto-reconnect failed" in result[0].lower()
