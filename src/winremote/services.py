"""Windows service and scheduled task management."""

from __future__ import annotations

import subprocess


def _ps(command: str, timeout: int = 30) -> str:
    """Run a PowerShell command and return output."""
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


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------


def service_list(filter_str: str = "") -> str:
    """List Windows services."""
    try:
        cmd = "Get-Service"
        if filter_str:
            cmd += f" | Where-Object {{ $_.DisplayName -like '*{filter_str}*' -or $_.Name -like '*{filter_str}*' }}"
        cmd += " | Format-Table Name, DisplayName, Status -AutoSize"
        return _ps(cmd)
    except Exception as e:
        return f"ServiceList error: {e}"


def service_start(name: str) -> str:
    """Start a Windows service."""
    try:
        return _ps(f'Start-Service -Name "{name}" -PassThru | Format-Table Name, Status -AutoSize')
    except Exception as e:
        return f"ServiceStart error: {e}"


def service_stop(name: str) -> str:
    """Stop a Windows service."""
    try:
        return _ps(f'Stop-Service -Name "{name}" -Force -PassThru | Format-Table Name, Status -AutoSize')
    except Exception as e:
        return f"ServiceStop error: {e}"


# ---------------------------------------------------------------------------
# Scheduled Tasks
# ---------------------------------------------------------------------------


def task_list(filter_str: str = "") -> str:
    """List scheduled tasks."""
    try:
        cmd = "Get-ScheduledTask"
        if filter_str:
            cmd += f" | Where-Object {{ $_.TaskName -like '*{filter_str}*' }}"
        cmd += " | Format-Table TaskName, State, TaskPath -AutoSize"
        return _ps(cmd)
    except Exception as e:
        return f"TaskList error: {e}"


def task_create(name: str, command: str, schedule: str) -> str:
    """Create a scheduled task using schtasks."""
    try:
        cmd = f'schtasks /Create /TN "{name}" /TR "{command}" /SC {schedule} /F'
        return _ps(cmd)
    except Exception as e:
        return f"TaskCreate error: {e}"


def task_delete(name: str) -> str:
    """Delete a scheduled task."""
    try:
        return _ps(f'schtasks /Delete /TN "{name}" /F')
    except Exception as e:
        return f"TaskDelete error: {e}"


# ---------------------------------------------------------------------------
# Event Log
# ---------------------------------------------------------------------------


def event_log(log_name: str = "System", count: int = 20, level: str = "") -> str:
    """Read Windows Event Log entries."""
    try:
        cmd = f"Get-WinEvent -LogName '{log_name}' -MaxEvents {count}"
        if level:
            level_map = {
                "critical": 1,
                "error": 2,
                "warning": 3,
                "information": 4,
                "verbose": 5,
            }
            lvl_num = level_map.get(level.lower())
            if lvl_num:
                cmd = f"Get-WinEvent -FilterHashtable @{{LogName='{log_name}';Level={lvl_num}}} -MaxEvents {count}"
        cmd += " | Format-Table TimeCreated, Id, LevelDisplayName, Message -AutoSize -Wrap"
        return _ps(cmd, timeout=30)
    except Exception as e:
        return f"EventLog error: {e}"
