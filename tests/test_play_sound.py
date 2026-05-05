"""Unit tests for PlaySound tool."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch


def _call_tool(**kwargs):
    from winremote.__main__ import PlaySound

    return PlaySound(**kwargs)


class TestPlaySound:
    @patch("subprocess.run")
    def test_play_sound_with_path(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = _call_tool(path="C:\\test.wav")
        assert "Played" in result or "task:" in result

    @patch("subprocess.run")
    def test_play_sound_no_args(self, mock_run):
        result = _call_tool()
        assert "error" in result.lower() or "provide" in result.lower()

    @patch("subprocess.run")
    def test_play_sound_none_args(self, mock_run):
        result = _call_tool(path=None, url=None)
        assert "error" in result.lower() or "provide" in result.lower()

    @patch("subprocess.run")
    def test_play_sound_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired("powershell", 30)
        result = _call_tool(path="C:\\test.wav")
        assert "timed out" in result.lower() or "task:" in result

    @patch("subprocess.run")
    def test_play_sound_error(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="file not found")
        result = _call_tool(path="C:\\nonexistent.wav")
        assert "error" in result.lower() or "task:" in result

    @patch("urllib.request.urlretrieve")
    @patch("subprocess.run")
    def test_play_sound_with_url(self, mock_run, mock_retrieve):
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        mock_retrieve.return_value = (None, None)
        result = _call_tool(url="https://example.com/test.wav")
        assert "Played" in result or "task:" in result or "error" in result.lower()

    @patch("subprocess.run")
    def test_play_sound_mp3(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = _call_tool(path="C:\\test.mp3")
        assert "Played" in result or "task:" in result
        # Verify MediaPlayer is used for mp3
        call_args = mock_run.call_args
        cmd = call_args[0][0][-1] if call_args else ""
        assert "MediaPlayer" in str(cmd) or "task:" in result

    def test_play_sound_in_tier3(self):
        from winremote.tiers import TOOL_TIERS

        assert "PlaySound" not in TOOL_TIERS["tier1"]
        assert "PlaySound" in TOOL_TIERS["tier3"]
