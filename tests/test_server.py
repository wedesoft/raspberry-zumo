import pytest
from mock import MagicMock, call
import server
from server import *


@pytest.fixture(autouse=True)
def udp_server(monkeypatch):
    monkeypatch.setattr(server, 'UDPServer', MagicMock(name='udp_server'))
    server.UDPServer.return_value.read.return_value = "25.0,65.0"
    return server.UDPServer


@pytest.fixture(autouse=True)
def gpio(monkeypatch):
    monkeypatch.setattr(server, 'GPIO', MagicMock(name='gpio'))
    return server.GPIO


@pytest.fixture
def target(udp_server, gpio):
    return Server()


class TestServer:
    def test_start_udp_server(self, target, udp_server):
        assert udp_server.called

    def test_start_drives(self, target, gpio):
        assert gpio.called


class TestServerUpdate:
    def test_reads_udp_data(self, target, udp_server):
        target.update()
        assert udp_server.return_value.read.called

    def test_update_drives(self, target, gpio):
        target.update()
        gpio.return_value.update.assert_called_with(25.0, 0.0, 65.0, 0.0)

    def test_update_drives_when_reversing(self, target, gpio):
        server.UDPServer.return_value.read.return_value = "-25.0,-65.0"
        target.update()
        gpio.return_value.update.assert_called_with(0.0, 25.0, 0.0, 65.0)
