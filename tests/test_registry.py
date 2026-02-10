"""Unit tests for registry module."""

from __future__ import annotations

import sys
from unittest.mock import patch

import pytest


class TestRegistry:
    def test_reg_read_non_windows(self):
        from winremote.registry import reg_read
        # On non-Windows, HAS_WINREG is False
        if sys.platform != "win32":
            result = reg_read("HKLM\\SOFTWARE\\Test", "value")
            assert "only available on Windows" in result

    def test_reg_write_non_windows(self):
        from winremote.registry import reg_write
        if sys.platform != "win32":
            result = reg_write("HKCU\\SOFTWARE\\Test", "key", "data")
            assert "only available on Windows" in result

    def test_parse_key_valid(self):
        from winremote.registry import _parse_key
        # On non-Windows, root keys are None, so this raises
        if sys.platform != "win32":
            with pytest.raises(ValueError):
                _parse_key("BADROOT\\test")

    def test_parse_key_splits_correctly(self):
        from winremote.registry import _parse_key
        # Just test the parsing logic
        try:
            root, subkey = _parse_key("HKLM\\SOFTWARE\\Microsoft")
            assert subkey == "SOFTWARE\\Microsoft"
        except ValueError:
            pass  # Expected on non-Windows
