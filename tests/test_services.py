"""Unit tests for services module (service_list, task_list, event_log, etc.)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch


class TestServiceList:
    @patch("winremote.services.subprocess.run")
    def test_service_list(self, mock_run):
        mock_run.return_value = MagicMock(stdout="sshd  OpenSSH  Running", stderr="", returncode=0)
        from winremote.services import service_list

        result = service_list()
        assert "sshd" in result

    @patch("winremote.services.subprocess.run")
    def test_service_list_filter(self, mock_run):
        mock_run.return_value = MagicMock(stdout="sshd  OpenSSH  Running", stderr="", returncode=0)
        from winremote.services import service_list

        result = service_list("ssh")
        assert "sshd" in result


class TestServiceStartStop:
    @patch("winremote.services.subprocess.run")
    def test_service_start(self, mock_run):
        mock_run.return_value = MagicMock(stdout="sshd Running", stderr="", returncode=0)
        from winremote.services import service_start

        result = service_start("sshd")
        assert "sshd" in result

    @patch("winremote.services.subprocess.run")
    def test_service_stop(self, mock_run):
        mock_run.return_value = MagicMock(stdout="sshd Stopped", stderr="", returncode=0)
        from winremote.services import service_stop

        result = service_stop("sshd")
        assert "sshd" in result


class TestTaskManagement:
    @patch("winremote.services.subprocess.run")
    def test_task_list(self, mock_run):
        mock_run.return_value = MagicMock(stdout="MyTask  Ready  \\", stderr="", returncode=0)
        from winremote.services import task_list

        result = task_list()
        assert "MyTask" in result

    @patch("winremote.services.subprocess.run")
    def test_task_create(self, mock_run):
        mock_run.return_value = MagicMock(stdout="SUCCESS", stderr="", returncode=0)
        from winremote.services import task_create

        result = task_create("TestTask", "echo hi", "DAILY")
        assert "SUCCESS" in result

    @patch("winremote.services.subprocess.run")
    def test_task_delete(self, mock_run):
        mock_run.return_value = MagicMock(stdout="SUCCESS", stderr="", returncode=0)
        from winremote.services import task_delete

        result = task_delete("TestTask")
        assert "SUCCESS" in result


class TestEventLog:
    @patch("winremote.services.subprocess.run")
    def test_event_log(self, mock_run):
        mock_run.return_value = MagicMock(stdout="2024-01-01 Error something", stderr="", returncode=0)
        from winremote.services import event_log

        result = event_log("System", 5)
        assert "2024" in result

    @patch("winremote.services.subprocess.run")
    def test_event_log_with_level(self, mock_run):
        mock_run.return_value = MagicMock(stdout="error entries", stderr="", returncode=0)
        from winremote.services import event_log

        result = event_log("System", 10, "error")
        assert "error" in result
