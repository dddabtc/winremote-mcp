"""winremote-mcp — CLI entry point and MCP tool definitions."""

from __future__ import annotations

import base64
import subprocess
import time
from datetime import datetime
from pathlib import Path

import click
import pyautogui
from dotenv import load_dotenv
from fastmcp import FastMCP
from mcp.types import ImageContent, TextContent

try:
    from mcp.types import ToolAnnotations
except ImportError:
    from fastmcp.tools import ToolAnnotations

from starlette.responses import JSONResponse

from winremote import __version__, desktop, process_mgr

load_dotenv()

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05

mcp = FastMCP(
    "winremote-mcp",
    instructions=(
        "Windows Remote MCP Server. Provides desktop control, window management, "
        "shell execution, file operations, and system management tools for a Windows machine."
    ),
)


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({"status": "ok", "version": __version__})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _tobool(v: bool | str) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).lower() in ("true", "1", "yes")


def _check_win32(tool_name: str = "This tool") -> str | None:
    """Return an error string if pywin32 is unavailable, else None."""
    if not desktop.HAS_WIN32:
        return f"Error: pywin32 not installed — {tool_name} requires it. Run `pip install pywin32` on the Windows host."
    return None


# ============================= DESKTOP CONTROL =============================


@mcp.tool(
    annotations=ToolAnnotations(
        title="Snapshot",
        readOnlyHint=True,
        openWorldHint=False,
    )
)
def Snapshot(
    use_vision: bool | str = True,
    quality: int = 75,
    max_width: int = 1920,
) -> list:
    """Capture desktop screenshot, window list, and interactive UI elements.

    Args:
        use_vision: Include screenshot image (default True).
        quality: JPEG quality 1-100 (default 75). Lower = smaller.
        max_width: Max image width in pixels (default 1920). Resized keeping aspect ratio.

    Returns a list containing:
    - Screenshot image as JPEG (if use_vision=True)
    - Text summary of windows and UI elements
    """
    try:
        parts = []
        use_vision = _tobool(use_vision)

        # Screenshot
        if use_vision:
            b64 = desktop.take_screenshot(quality=quality, max_width=max_width)
            parts.append(ImageContent(type="image", data=b64, mimeType="image/jpeg"))

        # Window list
        windows = desktop.enumerate_windows()
        win_lines = [f"**System Language:** {desktop._get_system_language()}", "", "**Windows:**"]
        for w in windows:
            win_lines.append(f"  [{w.handle}] {w.title} ({w.width}x{w.height} at {w.rect[0]},{w.rect[1]})")

        # Interactive elements from foreground window
        elements = desktop.get_interactive_elements()
        if elements:
            win_lines.append("")
            win_lines.append("**Interactive Elements (foreground window):**")
            for el in elements[:50]:  # limit
                r = el["rect"]
                cx = (r["left"] + r["right"]) // 2
                cy = (r["top"] + r["bottom"]) // 2
                label = el["text"] or el["class"]
                win_lines.append(f"  [{el['index']}] {label} — center ({cx},{cy})")

        parts.append(TextContent(type="text", text="\n".join(win_lines)))
        return parts
    except Exception as e:
        return [f"Snapshot error: {e}"]


@mcp.tool(
    annotations=ToolAnnotations(
        title="Click",
        destructiveHint=False,
        openWorldHint=False,
    )
)
def Click(
    x: int,
    y: int,
    button: str = "left",
    action: str = "click",
) -> str:
    """Mouse click at screen coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        button: 'left', 'right', or 'middle'.
        action: 'click', 'double', or 'hover'.
    """
    try:
        if action == "hover":
            pyautogui.moveTo(x, y)
            return f"Hovered at ({x},{y})"
        elif action == "double":
            pyautogui.doubleClick(x, y, button=button)
            return f"Double-clicked {button} at ({x},{y})"
        else:
            pyautogui.click(x, y, button=button)
            return f"Clicked {button} at ({x},{y})"
    except Exception as e:
        return f"Click error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="Type",
        destructiveHint=False,
        openWorldHint=False,
    )
)
def Type(
    text: str,
    x: int = 0,
    y: int = 0,
    clear: bool | str = False,
    press_enter: bool | str = False,
) -> str:
    """Type text, optionally at specific coordinates.

    Args:
        text: Text to type.
        x: X coordinate (0 = current position).
        y: Y coordinate (0 = current position).
        clear: Clear existing content first (Ctrl+A, Delete).
        press_enter: Press Enter after typing.
    """
    try:
        if x and y:
            pyautogui.click(x, y)
            time.sleep(0.1)
        if _tobool(clear):
            pyautogui.hotkey("ctrl", "a")
            pyautogui.press("delete")
            time.sleep(0.05)
        pyautogui.typewrite(text, interval=0.02) if text.isascii() else pyautogui.write(text)
        if _tobool(press_enter):
            pyautogui.press("enter")
        return f"Typed {len(text)} chars"
    except Exception as e:
        return f"Type error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="Scroll",
        destructiveHint=False,
        openWorldHint=False,
    )
)
def Scroll(
    amount: int,
    x: int = 0,
    y: int = 0,
    horizontal: bool | str = False,
) -> str:
    """Scroll at a position.

    Args:
        amount: Scroll amount (positive=up/right, negative=down/left).
        x: X coordinate (0 = current).
        y: Y coordinate (0 = current).
        horizontal: Horizontal scroll instead of vertical.
    """
    try:
        if x and y:
            pyautogui.moveTo(x, y)
        if _tobool(horizontal):
            pyautogui.hscroll(amount)
        else:
            pyautogui.scroll(amount)
        direction = "horizontally" if _tobool(horizontal) else "vertically"
        return f"Scrolled {amount} {direction}"
    except Exception as e:
        return f"Scroll error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="Move",
        destructiveHint=False,
        openWorldHint=False,
    )
)
def Move(
    x: int,
    y: int,
    drag: bool | str = False,
    start_x: int = 0,
    start_y: int = 0,
    duration: float = 0.3,
) -> str:
    """Move mouse or drag to position.

    Args:
        x: Target X.
        y: Target Y.
        drag: If true, drag from start position to target.
        start_x: Drag start X.
        start_y: Drag start Y.
        duration: Movement duration in seconds.
    """
    try:
        if _tobool(drag):
            if start_x and start_y:
                pyautogui.moveTo(start_x, start_y)
            pyautogui.drag(x - pyautogui.position()[0], y - pyautogui.position()[1], duration=duration)
            return f"Dragged to ({x},{y})"
        else:
            pyautogui.moveTo(x, y, duration=duration)
            return f"Moved to ({x},{y})"
    except Exception as e:
        return f"Move error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="Shortcut",
        destructiveHint=False,
        openWorldHint=False,
    )
)
def Shortcut(keys: str) -> str:
    """Execute keyboard shortcut.

    Args:
        keys: Shortcut string, e.g. 'ctrl+c', 'alt+tab', 'win+e'.
    """
    try:
        parts = [k.strip() for k in keys.lower().split("+")]
        pyautogui.hotkey(*parts)
        return f"Executed shortcut: {keys}"
    except Exception as e:
        return f"Shortcut error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="Wait",
        readOnlyHint=True,
        openWorldHint=False,
    )
)
def Wait(seconds: float = 1.0) -> str:
    """Pause execution.

    Args:
        seconds: Seconds to wait.
    """
    time.sleep(seconds)
    return f"Waited {seconds}s"


# =========================== WINDOW MANAGEMENT ============================


@mcp.tool(
    annotations=ToolAnnotations(
        title="FocusWindow",
        destructiveHint=False,
        openWorldHint=False,
    )
)
def FocusWindow(title: str = "", handle: int = 0) -> str:
    """Bring a window to the foreground.

    Args:
        title: Window title (fuzzy matched).
        handle: Window handle (exact).
    """
    err = _check_win32("FocusWindow")
    if err:
        return err
    try:
        return desktop.focus_window(title=title or None, handle=handle or None)
    except Exception as e:
        return f"FocusWindow error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="MinimizeAll",
        destructiveHint=False,
        openWorldHint=False,
    )
)
def MinimizeAll() -> str:
    """Minimize all windows (Win+D — show desktop)."""
    try:
        return desktop.minimize_all()
    except Exception as e:
        return f"MinimizeAll error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="App",
        destructiveHint=False,
        openWorldHint=True,
    )
)
def App(
    action: str = "launch",
    name: str = "",
    args: str = "",
    handle: int = 0,
    width: int = 0,
    height: int = 0,
) -> str:
    """Launch, switch to, or resize an application.

    Args:
        action: 'launch', 'switch', or 'resize'.
        name: Application name or path (for launch/switch).
        args: Arguments (for launch).
        handle: Window handle (for resize/switch).
        width: New width (for resize).
        height: New height (for resize).
    """
    try:
        if action == "launch":
            return desktop.launch_app(name, args)
        elif action == "switch":
            err = _check_win32("App(switch)")
            if err:
                return err
            return desktop.focus_window(title=name or None, handle=handle or None)
        elif action == "resize":
            err = _check_win32("App(resize)")
            if err:
                return err
            if not handle:
                return "resize requires a window handle"
            return desktop.resize_window(handle, width, height)
        return f"Unknown action: {action}"
    except Exception as e:
        return f"App error: {e}"


# =========================== REMOTE MANAGEMENT ============================


@mcp.tool(
    annotations=ToolAnnotations(
        title="Shell",
        destructiveHint=True,
        openWorldHint=True,
    )
)
def Shell(command: str, timeout: int = 30, cwd: str = "") -> str:
    """Execute a PowerShell command.

    Args:
        command: PowerShell command to execute.
        timeout: Timeout in seconds (default 30).
        cwd: Working directory. If provided, the command runs inside that directory.
    """
    try:
        if cwd:
            command = f"cd {cwd}; {command}"
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR] {result.stderr}"
        if result.returncode != 0:
            output += f"\n[Exit code: {result.returncode}]"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout}s"
    except Exception as e:
        return f"Shell error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="GetClipboard",
        readOnlyHint=True,
        openWorldHint=False,
    )
)
def GetClipboard() -> str:
    """Read the Windows clipboard text content."""
    err = _check_win32("GetClipboard")
    if err:
        return err
    try:
        return desktop.get_clipboard()
    except Exception as e:
        return f"GetClipboard error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="SetClipboard",
        destructiveHint=False,
        openWorldHint=False,
    )
)
def SetClipboard(text: str) -> str:
    """Set the Windows clipboard text content.

    Args:
        text: Text to place on clipboard.
    """
    err = _check_win32("SetClipboard")
    if err:
        return err
    try:
        return desktop.set_clipboard(text)
    except Exception as e:
        return f"SetClipboard error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="ListProcesses",
        readOnlyHint=True,
        openWorldHint=False,
    )
)
def ListProcesses(
    filter: str = "",
    sort_by: str = "memory",
    limit: int = 30,
) -> str:
    """List running processes with CPU and memory usage.

    Args:
        filter: Fuzzy filter by process name.
        sort_by: Sort by 'cpu', 'memory', or 'name'.
        limit: Max number of processes to return.
    """
    try:
        return process_mgr.list_processes(filter_name=filter, sort_by=sort_by, limit=limit)
    except Exception as e:
        return f"ListProcesses error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="KillProcess",
        destructiveHint=True,
        openWorldHint=False,
    )
)
def KillProcess(pid: int = 0, name: str = "") -> str:
    """Kill a process by PID or name.

    Args:
        pid: Process ID.
        name: Process name (fuzzy matched).
    """
    try:
        return process_mgr.kill_process(pid=pid, name=name)
    except Exception as e:
        return f"KillProcess error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="GetSystemInfo",
        readOnlyHint=True,
        openWorldHint=False,
    )
)
def GetSystemInfo() -> str:
    """Get system information: CPU, memory, disk, network, uptime."""
    try:
        return process_mgr.get_system_info()
    except Exception as e:
        return f"GetSystemInfo error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="Notification",
        destructiveHint=False,
        openWorldHint=False,
    )
)
def Notification(title: str = "winremote-mcp", message: str = "") -> str:
    """Show a Windows toast notification.

    Args:
        title: Notification title.
        message: Notification body text.
    """
    try:
        return desktop.show_notification(title, message)
    except Exception as e:
        return f"Notification error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="LockScreen",
        destructiveHint=True,
        openWorldHint=False,
    )
)
def LockScreen() -> str:
    """Lock the Windows workstation."""
    try:
        return desktop.lock_screen()
    except Exception as e:
        return f"LockScreen error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="Scrape",
        readOnlyHint=True,
        openWorldHint=True,
    )
)
def Scrape(url: str) -> str:
    """Fetch URL content and return as markdown.

    Args:
        url: URL to fetch.
    """
    try:
        import urllib.request

        from markdownify import markdownify

        req = urllib.request.Request(url, headers={"User-Agent": "winremote-mcp/0.2"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        md = markdownify(html, heading_style="ATX", strip=["script", "style"])
        # Truncate
        if len(md) > 50000:
            md = md[:50000] + "\n\n[... truncated]"
        return md
    except Exception as e:
        return f"Scrape error: {e}"


# ============================== FILE OPERATIONS ============================


@mcp.tool(
    annotations=ToolAnnotations(
        title="FileRead",
        readOnlyHint=True,
        openWorldHint=False,
    )
)
def FileRead(path: str, encoding: str = "utf-8") -> str:
    """Read file content. Returns base64 for binary files.

    Args:
        path: File path.
        encoding: Text encoding (default utf-8). Use 'binary' for base64 output.
    """
    try:
        p = Path(path)
        if not p.exists():
            return f"File not found: {path}"
        if encoding == "binary":
            data = p.read_bytes()
            return base64.b64encode(data).decode()
        else:
            text = p.read_text(encoding=encoding, errors="replace")
            if len(text) > 100000:
                text = text[:100000] + "\n\n[... truncated at 100KB]"
            return text
    except Exception as e:
        return f"FileRead error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="FileWrite",
        destructiveHint=True,
        openWorldHint=False,
    )
)
def FileWrite(path: str, content: str, encoding: str = "utf-8", append: bool | str = False) -> str:
    """Write content to a file.

    Args:
        path: File path.
        content: Content to write.
        encoding: Text encoding (default utf-8).
        append: Append instead of overwrite.
    """
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if _tobool(append) else "w"
        with open(p, mode, encoding=encoding) as f:
            f.write(content)
        return f"Written {len(content)} chars to {path}"
    except Exception as e:
        return f"FileWrite error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="FileList",
        readOnlyHint=True,
        openWorldHint=False,
    )
)
def FileList(path: str = ".", show_hidden: bool | str = False) -> str:
    """List directory contents with size and modification date.

    Args:
        path: Directory path.
        show_hidden: Include hidden files/folders.
    """
    try:
        from tabulate import tabulate

        p = Path(path)
        if not p.is_dir():
            return f"Not a directory: {path}"

        rows = []
        for item in sorted(p.iterdir()):
            name = item.name
            if not _tobool(show_hidden) and name.startswith("."):
                continue
            try:
                stat = item.stat()
                size = stat.st_size
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                kind = "DIR" if item.is_dir() else "FILE"
                if item.is_dir():
                    size_str = "<DIR>"
                elif size < 1024:
                    size_str = f"{size}B"
                elif size < 1048576:
                    size_str = f"{size // 1024}KB"
                else:
                    size_str = f"{size // 1048576}MB"
                rows.append([kind, name, size_str, mtime])
            except Exception:
                rows.append(["?", name, "?", "?"])

        if not rows:
            return "Directory is empty."
        return tabulate(rows, headers=["Type", "Name", "Size", "Modified"], tablefmt="simple")
    except Exception as e:
        return f"FileList error: {e}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="FileSearch",
        readOnlyHint=True,
        openWorldHint=False,
    )
)
def FileSearch(pattern: str, path: str = ".", recursive: bool | str = True, limit: int = 50) -> str:
    """Search files by name pattern.

    Args:
        pattern: Glob pattern (e.g. '*.py', 'report*').
        path: Root directory to search.
        recursive: Search subdirectories.
        limit: Max results.
    """
    try:
        p = Path(path)
        if _tobool(recursive):
            matches = list(p.rglob(pattern))
        else:
            matches = list(p.glob(pattern))

        if not matches:
            return f"No files matching '{pattern}' in {path}"

        lines = []
        for m in matches[:limit]:
            try:
                size = m.stat().st_size
                lines.append(f"  {m} ({size} bytes)")
            except Exception:
                lines.append(f"  {m}")

        result = f"Found {len(matches)} files"
        if len(matches) > limit:
            result += f" (showing first {limit})"
        result += ":\n" + "\n".join(lines)
        return result
    except Exception as e:
        return f"FileSearch error: {e}"


# ================================== CLI ====================================


@click.group(invoke_without_command=True)
@click.option("--transport", default="streamable-http", type=click.Choice(["stdio", "streamable-http"]))
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8090, type=int)
@click.option("--reload", is_flag=True, default=False, help="Enable hot reload (streamable-http only)")
@click.pass_context
def cli(ctx, transport: str, host: str, port: int, reload: bool):
    """Start the winremote MCP server."""
    if ctx.invoked_subcommand is not None:
        return  # subcommand will handle it
    import logging

    class BannerFilter(logging.Filter):
        """Inject our banner after uvicorn's 'Application startup complete' log."""

        _shown = False

        def filter(self, record):
            if not self._shown and "Application startup complete" in record.getMessage():
                self._shown = True
                print(
                    "\n"
                    "  ╔═══════════════════════════════════════╗\n"
                    "  ║  winremote-mcp v0.2.0                 ║\n"
                    "  ║  by dddabtc                           ║\n"
                    "  ║  https://github.com/dddabtc           ║\n"
                    "  ╚═══════════════════════════════════════╝\n",
                    flush=True,
                )
            return True

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        logging.getLogger("uvicorn.error").addFilter(BannerFilter())
        run_kwargs = dict(transport="streamable-http", host=host, port=port)
        if reload:
            run_kwargs["uvicorn_args"] = {"reload": True}
        mcp.run(**run_kwargs)


@cli.command()
def install():
    """Create a Windows scheduled task for auto-start."""
    import getpass

    username = getpass.getuser()
    task_cmd = f'schtasks /Create /SC ONSTART /TN "WinRemoteMCP" /TR "python -m winremote" /RU {username} /F'
    try:
        result = subprocess.run(task_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            click.echo("✅ Scheduled task 'WinRemoteMCP' created for auto-start.")
        else:
            click.echo(f"❌ Failed to create task:\n{result.stderr or result.stdout}")
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
def uninstall():
    """Remove the WinRemoteMCP scheduled task."""
    task_cmd = 'schtasks /Delete /TN "WinRemoteMCP" /F'
    try:
        result = subprocess.run(task_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            click.echo("✅ Scheduled task 'WinRemoteMCP' removed.")
        else:
            click.echo(f"❌ Failed to remove task:\n{result.stderr or result.stdout}")
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
def health():
    """Print health status JSON."""
    import json

    click.echo(json.dumps({"status": "ok", "version": __version__}))


if __name__ == "__main__":
    cli()
