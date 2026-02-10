"""Unit tests for helper functions."""

from __future__ import annotations


class TestTobool:
    def test_bool_values(self):
        from winremote.__main__ import _tobool
        assert _tobool(True) is True
        assert _tobool(False) is False

    def test_string_values(self):
        from winremote.__main__ import _tobool
        assert _tobool("true") is True
        assert _tobool("True") is True
        assert _tobool("1") is True
        assert _tobool("yes") is True
        assert _tobool("false") is False
        assert _tobool("0") is False
        assert _tobool("no") is False


class TestCheckWin32:
    def test_no_win32(self):
        from unittest.mock import patch

        import winremote.__main__ as mod
        from winremote.__main__ import _check_win32
        with patch.object(mod.desktop, "HAS_WIN32", False):
            result = _check_win32("TestTool")
            assert result is not None
            assert "pywin32" in result

    def test_has_win32(self):
        from unittest.mock import patch

        import winremote.__main__ as mod
        from winremote.__main__ import _check_win32
        with patch.object(mod.desktop, "HAS_WIN32", True):
            result = _check_win32("TestTool")
            assert result is None


class TestVersion:
    def test_version_string(self):
        from winremote import __version__
        assert __version__
        parts = __version__.split(".")
        assert len(parts) >= 2
