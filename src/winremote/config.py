"""Configuration loading and merge utilities for winremote-mcp."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib


@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8090
    auth_key: str | None = None


@dataclass
class SecurityConfig:
    ip_allowlist: list[str] = field(default_factory=list)
    enable_tier3: bool = False
    disable_tier2: bool = False


@dataclass
class ToolsConfig:
    enable: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)


@dataclass
class WinRemoteConfig:
    server: ServerConfig = field(default_factory=ServerConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    tools: ToolsConfig = field(default_factory=ToolsConfig)
    source_path: Path | None = None


def discover_config_path(explicit_path: str | None) -> Path | None:
    """Find config path using precedence: explicit > cwd > ~/.config."""
    if explicit_path:
        path = Path(explicit_path).expanduser()
        return path

    cwd_path = Path.cwd() / "winremote.toml"
    if cwd_path.exists():
        return cwd_path

    user_path = Path("~/.config/winremote/winremote.toml").expanduser()
    if user_path.exists():
        return user_path
    return None


def _list_of_strings(raw: object, key: str) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list) or not all(isinstance(i, str) for i in raw):
        raise ValueError(f"{key} must be an array of strings")
    return raw


def load_config(path: Path | None) -> WinRemoteConfig:
    """Load and validate TOML config file. Returns defaults when path is None."""
    cfg = WinRemoteConfig()
    if path is None:
        return cfg

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    data = tomllib.loads(path.read_text(encoding="utf-8"))

    server = data.get("server", {})
    security = data.get("security", {})
    tools = data.get("tools", {})

    if "host" in server:
        cfg.server.host = str(server["host"])
    if "port" in server:
        cfg.server.port = int(server["port"])
    if "auth_key" in server:
        cfg.server.auth_key = str(server["auth_key"])

    if "ip_allowlist" in security:
        cfg.security.ip_allowlist = _list_of_strings(security["ip_allowlist"], "security.ip_allowlist")
    if "enable_tier3" in security:
        cfg.security.enable_tier3 = bool(security["enable_tier3"])
    if "disable_tier2" in security:
        cfg.security.disable_tier2 = bool(security["disable_tier2"])

    if "enable" in tools:
        cfg.tools.enable = _list_of_strings(tools["enable"], "tools.enable")
    if "exclude" in tools:
        cfg.tools.exclude = _list_of_strings(tools["exclude"], "tools.exclude")

    cfg.source_path = path
    return cfg
