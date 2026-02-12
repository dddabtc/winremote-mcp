from pathlib import Path

import pytest

from winremote.config import discover_config_path, load_config
from winremote.security import parse_ip_allowlist
from winremote.tiers import resolve_enabled_tools


def test_config_loader_reads_toml(tmp_path: Path):
    cfg_file = tmp_path / "winremote.toml"
    cfg_file.write_text(
        """
[server]
host = "0.0.0.0"
port = 9000
auth_key = "abc"

[security]
ip_allowlist = ["127.0.0.1", "10.0.0.0/8"]
enable_tier3 = true
disable_tier2 = false

[tools]
enable = ["Snapshot", "Click", "Type"]
exclude = ["Type"]
""".strip(),
        encoding="utf-8",
    )

    cfg = load_config(cfg_file)
    assert cfg.server.host == "0.0.0.0"
    assert cfg.server.port == 9000
    assert cfg.server.auth_key == "abc"
    assert cfg.security.ip_allowlist == ["127.0.0.1", "10.0.0.0/8"]
    assert cfg.security.enable_tier3 is True
    assert cfg.tools.enable == ["Snapshot", "Click", "Type"]
    assert cfg.tools.exclude == ["Type"]


def test_discover_config_path_prefers_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    cfg = tmp_path / "winremote.toml"
    cfg.write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    found = discover_config_path(None)
    assert found == cfg


def test_tier_resolution_defaults():
    enabled = resolve_enabled_tools()
    assert "Snapshot" in enabled
    assert "Click" in enabled
    assert "Shell" not in enabled


def test_tier_resolution_flags():
    disabled_t2 = resolve_enabled_tools(disable_tier2=True)
    assert "Click" not in disabled_t2
    assert "Snapshot" in disabled_t2

    with_t3 = resolve_enabled_tools(enable_tier3=True)
    assert "Shell" in with_t3

    both = resolve_enabled_tools(enable_tier3=True, disable_tier2=True)
    assert "Click" not in both
    assert "Shell" in both


def test_explicit_tools_override_tiers():
    enabled = resolve_enabled_tools(
        enable_tier3=False,
        disable_tier2=True,
        explicit_tools=["snapshot", "click", "type"],
    )
    assert enabled == {"Snapshot", "Click", "Type"}


def test_invalid_tool_rejected():
    with pytest.raises(ValueError):
        resolve_enabled_tools(explicit_tools=["NopeTool"])


def test_ip_allowlist_parsing():
    nets = parse_ip_allowlist(["127.0.0.1", "192.168.1.0/24", "::1"])
    assert len(nets) == 3


def test_ip_allowlist_invalid():
    with pytest.raises(ValueError):
        parse_ip_allowlist(["not-an-ip"])
