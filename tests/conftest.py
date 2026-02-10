"""Shared fixtures for winremote-mcp tests.

Mocks win32 and display-dependent modules so tests run on headless Linux.
"""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Must happen before ANY winremote import
# ---------------------------------------------------------------------------

os.environ.setdefault("DISPLAY", ":0")

# Mock all problematic native modules
_mock_modules = [
    "Xlib", "Xlib.display", "Xlib.xauth", "Xlib.error",
    "Xlib.protocol", "Xlib.protocol.display", "Xlib.protocol.rq",
    "Xlib.support", "Xlib.support.connect", "Xlib.support.unix_connect",
    "Xlib.ext", "Xlib.ext.xtest", "Xlib.X", "Xlib.XK",
    "Xlib.keysymdef", "Xlib.keysymdef.latin1",
    "mouseinfo",
    "win32api", "win32gui", "win32con", "win32process", "win32clipboard",
    "winreg",
]

for mod_name in _mock_modules:
    if mod_name not in sys.modules:
        m = MagicMock()
        m.__path__ = []
        m.__file__ = f"<mock {mod_name}>"
        m.__spec__ = None
        sys.modules[mod_name] = m

# Now import pyautogui safely
import pyautogui  # noqa: E402

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_pyautogui(monkeypatch):
    """Prevent any real mouse/keyboard actions during tests."""
    monkeypatch.setattr(pyautogui, "click", MagicMock())
    monkeypatch.setattr(pyautogui, "doubleClick", MagicMock())
    monkeypatch.setattr(pyautogui, "moveTo", MagicMock())
    monkeypatch.setattr(pyautogui, "drag", MagicMock())
    monkeypatch.setattr(pyautogui, "scroll", MagicMock())
    monkeypatch.setattr(pyautogui, "hscroll", MagicMock())
    monkeypatch.setattr(pyautogui, "hotkey", MagicMock())
    monkeypatch.setattr(pyautogui, "press", MagicMock())
    monkeypatch.setattr(pyautogui, "typewrite", MagicMock())
    monkeypatch.setattr(pyautogui, "write", MagicMock())
    monkeypatch.setattr(pyautogui, "position", MagicMock(return_value=(500, 500)))
