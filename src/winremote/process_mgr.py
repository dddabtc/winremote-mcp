"""Process management utilities."""

from __future__ import annotations

import psutil
from tabulate import tabulate
from thefuzz import fuzz


def list_processes(
    filter_name: str = "",
    sort_by: str = "memory",
    limit: int = 30,
) -> str:
    """List running processes with CPU/memory usage.

    Args:
        filter_name: Fuzzy filter by process name.
        sort_by: Sort key — 'cpu', 'memory', or 'name'.
        limit: Max rows to return.
    """
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "status"]):
        try:
            info = p.info
            name = info["name"] or ""
            if filter_name:
                if fuzz.partial_ratio(filter_name.lower(), name.lower()) < 60:
                    continue
            mem_mb = (info["memory_info"].rss / 1048576) if info["memory_info"] else 0
            procs.append(
                {
                    "PID": info["pid"],
                    "Name": name,
                    "CPU%": info["cpu_percent"] or 0,
                    "Mem(MB)": round(mem_mb, 1),
                    "Status": info["status"],
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    key_map = {"cpu": "CPU%", "memory": "Mem(MB)", "name": "Name"}
    sort_key = key_map.get(sort_by, "Mem(MB)")
    reverse = sort_key != "Name"
    procs.sort(key=lambda x: x[sort_key], reverse=reverse)
    procs = procs[:limit]

    if not procs:
        return "No processes found."
    return tabulate(procs, headers="keys", tablefmt="simple")


def kill_process(pid: int = 0, name: str = "") -> str:
    """Kill a process by PID or name."""
    if pid:
        try:
            p = psutil.Process(pid)
            p.kill()
            return f"Killed PID {pid} ({p.name()})"
        except psutil.NoSuchProcess:
            return f"PID {pid} not found"
        except psutil.AccessDenied:
            return f"Access denied for PID {pid}"
        except Exception as e:
            return f"Error: {e}"

    if name:
        killed = []
        for p in psutil.process_iter(["pid", "name"]):
            try:
                if p.info["name"] and fuzz.ratio(name.lower(), p.info["name"].lower()) > 80:
                    p.kill()
                    killed.append(f"{p.info['name']} (PID {p.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if killed:
            return f"Killed: {', '.join(killed)}"
        return f"No process matching '{name}'"

    return "Provide pid or name."


def get_system_info() -> str:
    """Return system info: CPU, memory, disk, network, uptime."""
    import datetime
    import platform

    cpu_pct = psutil.cpu_percent(interval=0.5)
    cpu_count = psutil.cpu_count()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\") if platform.system() == "Windows" else psutil.disk_usage("/")
    boot = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot

    net = psutil.net_io_counters()

    lines = [
        f"**System:** {platform.system()} {platform.release()} ({platform.machine()})",
        f"**CPU:** {cpu_pct}% ({cpu_count} cores)",
        f"**Memory:** {mem.percent}% — {mem.used // 1048576}MB / {mem.total // 1048576}MB",
        f"**Disk (C:):** {disk.percent}% — {disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB",
        f"**Network:** Sent {net.bytes_sent // 1048576}MB / Recv {net.bytes_recv // 1048576}MB",
        f"**Uptime:** {str(uptime).split('.')[0]} (boot: {boot.strftime('%Y-%m-%d %H:%M')})",
    ]
    return "\n".join(lines)
