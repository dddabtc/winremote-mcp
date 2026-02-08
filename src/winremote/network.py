"""Network diagnostic tools."""

from __future__ import annotations

import socket
import subprocess


def ping(host: str, count: int = 4) -> str:
    """Ping a host."""
    try:
        result = subprocess.run(
            ["ping", "-n", str(count), host],
            capture_output=True,
            text=True,
            timeout=count * 5 + 10,
        )
        return result.stdout.strip() or result.stderr.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Ping timed out after {count * 5 + 10}s"
    except Exception as e:
        return f"Ping error: {e}"


def port_check(host: str, port: int, timeout: float = 5.0) -> str:
    """Check if a TCP port is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            return f"Port {port} on {host} is OPEN"
        else:
            return f"Port {port} on {host} is CLOSED (code {result})"
    except socket.timeout:
        return f"Port {port} on {host} — connection timed out ({timeout}s)"
    except Exception as e:
        return f"PortCheck error: {e}"


def net_connections(filter_str: str = "", limit: int = 50) -> str:
    """List network connections using psutil."""
    try:
        import psutil
        from tabulate import tabulate

        conns = psutil.net_connections(kind="inet")
        rows = []
        for c in conns:
            local = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else ""
            remote = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else ""
            status = c.status
            pid = c.pid or ""

            if filter_str:
                searchable = f"{local} {remote} {status} {pid}"
                if filter_str.lower() not in searchable.lower():
                    continue

            rows.append([local, remote, status, pid])

        if not rows:
            return "No connections found."
        rows = rows[:limit]
        return tabulate(rows, headers=["Local", "Remote", "Status", "PID"], tablefmt="simple")
    except Exception as e:
        return f"NetConnections error: {e}"
