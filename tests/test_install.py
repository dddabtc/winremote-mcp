"""Tests for Windows scheduled-task installer helpers."""

from __future__ import annotations

from subprocess import CompletedProcess

from click.testing import CliRunner


class _RunRecorder:
    def __init__(self):
        self.calls: list[list[str]] = []

    def __call__(self, cmd, capture_output=True, text=True):
        self.calls.append(list(cmd))
        return CompletedProcess(cmd, 0, stdout="OK", stderr="")


def test_install_persists_server_args_and_uses_background_batch(tmp_path, monkeypatch):
    import winremote.__main__ as mod

    runner = CliRunner()
    run_recorder = _RunRecorder()
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setattr(mod.subprocess, "run", run_recorder)

    result = runner.invoke(
        mod.cli,
        [
            "install",
            "--transport",
            "streamable-http",
            "--host",
            "0.0.0.0",
            "--port",
            "8090",
            "--auth-key",
            "pretty?key",
        ],
    )

    assert result.exit_code == 0, result.output
    script_path = tmp_path / "start_mcp.bat"
    script = script_path.read_text(encoding="utf-8")
    assert 'start "" /B cmd /c' in script
    assert "-m winremote" in script
    assert "--transport streamable-http" in script
    assert "--host 0.0.0.0" in script
    assert "--port 8090" in script
    assert "--auth-key pretty?key" in script
    assert "winget" not in script
    assert "ps2exe" not in script

    assert run_recorder.calls
    create_cmd = run_recorder.calls[0]
    assert create_cmd[:4] == ["schtasks", "/Create", "/SC", "ONLOGON"]
    assert "/TN" in create_cmd
    assert "WinRemoteMCP" in create_cmd
    assert str(script_path) in create_cmd
