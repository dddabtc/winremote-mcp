"""Unit tests for network module."""

from __future__ import annotations

import socket
from unittest.mock import MagicMock, patch


class TestPing:
    @patch("winremote.network.subprocess.run")
    def test_ping_success(self, mock_run):
        mock_run.return_value = MagicMock(stdout="Reply from 8.8.8.8: bytes=32", stderr="", returncode=0)
        from winremote.network import ping
        result = ping("8.8.8.8", count=2)
        assert "Reply" in result

    @patch("winremote.network.subprocess.run")
    def test_ping_timeout(self, mock_run):
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("ping", 20)
        from winremote.network import ping
        result = ping("unreachable.host")
        assert "timed out" in result.lower()


class TestPortCheck:
    @patch("socket.socket")
    def test_port_open(self, mock_socket_cls):
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 0
        mock_socket_cls.return_value = mock_sock
        from winremote.network import port_check
        result = port_check("localhost", 80)
        assert "OPEN" in result

    @patch("socket.socket")
    def test_port_closed(self, mock_socket_cls):
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 111
        mock_socket_cls.return_value = mock_sock
        from winremote.network import port_check
        result = port_check("localhost", 9999)
        assert "CLOSED" in result

    @patch("socket.socket")
    def test_port_timeout(self, mock_socket_cls):
        mock_sock = MagicMock()
        mock_sock.connect_ex.side_effect = socket.timeout("timed out")
        mock_socket_cls.return_value = mock_sock
        from winremote.network import port_check
        result = port_check("slow.host", 80)
        assert "timed out" in result


class TestNetConnections:
    @patch("psutil.net_connections")
    def test_net_connections(self, mock_net):
        mock_conn = MagicMock()
        mock_conn.laddr = MagicMock(ip="127.0.0.1", port=8080)
        mock_conn.raddr = MagicMock(ip="10.0.0.1", port=443)
        mock_conn.status = "ESTABLISHED"
        mock_conn.pid = 1234
        mock_net.return_value = [mock_conn]
        from winremote.network import net_connections
        result = net_connections()
        assert "127.0.0.1" in result or "ESTABLISHED" in result

    @patch("psutil.net_connections")
    def test_net_connections_empty(self, mock_net):
        mock_net.return_value = []
        from winremote.network import net_connections
        result = net_connections()
        assert "No connections" in result
