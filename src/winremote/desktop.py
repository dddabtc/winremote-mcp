"""Win32 desktop interactions — screenshots, window enumeration, UI elements."""

from __future__ import annotations

import base64
import ctypes
import io
import locale
import time
from dataclasses import dataclass, field
from typing import Optional

import pyautogui

# Win32 imports (will fail on non-Windows — caught at tool level)
try:
    import win32gui
    import win32con
    import win32api
    import win32process
    import win32clipboard

    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

from PIL import ImageGrab


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tobool(v: bool | str) -> bool:
    """Handle MCP's bool-as-string quirk."""
    if isinstance(v, bool):
        return v
    return str(v).lower() in ("true", "1", "yes")


def _get_system_language() -> str:
    """Return current Windows display language."""
    try:
        return locale.getdefaultlocale()[0] or "en_US"
    except Exception:
        return "en_US"


# ---------------------------------------------------------------------------
# Window info
# ---------------------------------------------------------------------------

@dataclass
class WindowInfo:
    handle: int
    title: str
    rect: tuple[int, int, int, int]  # left, top, right, bottom
    visible: bool
    pid: int = 0

    @property
    def width(self) -> int:
        return self.rect[2] - self.rect[0]

    @property
    def height(self) -> int:
        return self.rect[3] - self.rect[1]


def enumerate_windows() -> list[WindowInfo]:
    """List all visible top-level windows."""
    if not HAS_WIN32:
        raise RuntimeError("pywin32 not installed — run `pip install pywin32`")
    results: list[WindowInfo] = []

    def _cb(hwnd: int, _extra: None) -> bool:
        if not win32gui.IsWindowVisible(hwnd):
            return True
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return True
        rect = win32gui.GetWindowRect(hwnd)
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
        except Exception:
            pid = 0
        results.append(WindowInfo(handle=hwnd, title=title, rect=rect, visible=True, pid=pid))
        return True

    win32gui.EnumWindows(_cb, None)
    return results


def get_interactive_elements() -> list[dict]:
    """Simplified accessibility tree — enumerate child windows with class/text."""
    if not HAS_WIN32:
        raise RuntimeError("pywin32 not installed — run `pip install pywin32`")
    fg = win32gui.GetForegroundWindow()
    if not fg:
        return []
    elements: list[dict] = []
    idx = [0]

    def _cb(hwnd: int, _extra: None) -> bool:
        if not win32gui.IsWindowVisible(hwnd):
            return True
        cls = win32gui.GetClassName(hwnd)
        text = win32gui.GetWindowText(hwnd)
        try:
            rect = win32gui.GetWindowRect(hwnd)
        except Exception:
            return True
        idx[0] += 1
        elements.append({
            "index": idx[0],
            "class": cls,
            "text": text,
            "rect": {"left": rect[0], "top": rect[1], "right": rect[2], "bottom": rect[3]},
        })
        return True

    try:
        win32gui.EnumChildWindows(fg, _cb, None)
    except Exception:
        pass
    return elements


# ---------------------------------------------------------------------------
# Screenshot
# ---------------------------------------------------------------------------

def take_screenshot(quality: int = 75, max_width: int = 1920) -> str:
    """Capture full screen, return base64 JPEG. Resizes if wider than max_width."""
    img = ImageGrab.grab()
    # Resize if needed
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), resample=3)  # LANCZOS
    # Convert to JPEG
    if img.mode in ("RGBA", "LA"):
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


# ---------------------------------------------------------------------------
# Window management
# ---------------------------------------------------------------------------

def focus_window(title: Optional[str] = None, handle: Optional[int] = None) -> str:
    """Bring a window to the foreground. Fuzzy-match title if provided."""
    if not HAS_WIN32:
        return "Error: pywin32 not installed — run `pip install pywin32`"

    hwnd = None
    if handle:
        hwnd = handle
    elif title:
        from thefuzz import fuzz
        best_score = 0
        for w in enumerate_windows():
            score = fuzz.partial_ratio(title.lower(), w.title.lower())
            if score > best_score:
                best_score = score
                hwnd = w.handle
        if best_score < 50:
            return f"No window matching '{title}' (best score {best_score})"

    if not hwnd:
        return "No window found"

    try:
        # Restore if minimized
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        return f"Focused window handle={hwnd} title='{win32gui.GetWindowText(hwnd)}'"
    except Exception as e:
        return f"Failed to focus: {e}"


def minimize_all() -> str:
    """Win+D — show desktop."""
    try:
        pyautogui.hotkey("win", "d")
        return "Minimized all windows"
    except Exception as e:
        return f"Failed: {e}"


def launch_app(name: str, args: str = "") -> str:
    """Launch application via PowerShell Start-Process."""
    import subprocess
    try:
        cmd = f'Start-Process "{name}"'
        if args:
            cmd += f' -ArgumentList "{args}"'
        subprocess.run(["powershell", "-Command", cmd], timeout=10, capture_output=True)
        return f"Launched {name}"
    except Exception as e:
        return f"Failed to launch {name}: {e}"


def resize_window(handle: int, width: int, height: int) -> str:
    """Resize a window by handle."""
    if not HAS_WIN32:
        return "Error: pywin32 not installed — run `pip install pywin32`"
    try:
        rect = win32gui.GetWindowRect(handle)
        win32gui.MoveWindow(handle, rect[0], rect[1], width, height, True)
        return f"Resized {handle} to {width}x{height}"
    except Exception as e:
        return f"Failed: {e}"


# ---------------------------------------------------------------------------
# Clipboard
# ---------------------------------------------------------------------------

def get_clipboard() -> str:
    if not HAS_WIN32:
        return "Error: pywin32 not installed — run `pip install pywin32`"
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return data
    except Exception as e:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass
        return f"Error: {e}"


def set_clipboard(text: str) -> str:
    if not HAS_WIN32:
        return "Error: pywin32 not installed — run `pip install pywin32`"
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return "Clipboard set"
    except Exception as e:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# Lock screen
# ---------------------------------------------------------------------------

def lock_screen() -> str:
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Screen locked"
    except Exception as e:
        return f"Failed: {e}"


# ---------------------------------------------------------------------------
# Toast notification
# ---------------------------------------------------------------------------

def show_notification(title: str, message: str) -> str:
    """Show a Windows toast notification via PowerShell."""
    import subprocess
    ps = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$template = @"
<toast>
  <visual><binding template="ToastGeneric">
    <text>{title}</text>
    <text>{message}</text>
  </binding></visual>
</toast>
"@
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("winremote-mcp").Show($toast)
'''
    try:
        subprocess.run(["powershell", "-Command", ps], timeout=10, capture_output=True)
        return "Notification shown"
    except Exception as e:
        return f"Failed: {e}"
