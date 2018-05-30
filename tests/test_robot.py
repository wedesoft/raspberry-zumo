import pytest
from mock import MagicMock, call
import robot
from robot import *


@pytest.fixture(autouse=True)
def udp_server(monkeypatch):
    monkeypatch.setattr(robot, 'UDPServer', MagicMock(name='udp_server'))
    robot.UDPServer.return_value.read.return_value = "25.0,65.0"
    return robot.UDPServer


@pytest.fixture(autouse=True)
def gpio(monkeypatch):
    monkeypatch.setattr(robot, 'GPIO', MagicMock(name='gpio'))
    return robot.GPIO


@pytest.fixture
def target(udp_server, gpio):
    return Robot()


class TestRobot:
    def test_start_udp_server(self, target, udp_server):
        assert udp_server.called

    def test_start_drives(self, target, gpio):
        assert gpio.called


class TestRobotUpdate:
    def test_reads_udp_data(self, target, udp_server):
        target.update()
        assert udp_server.return_value.read.called

    def test_update_drives(self, target, gpio):
        target.update()
        gpio.return_value.update.assert_called_with(25.0, 0.0, 65.0, 0.0)

    def test_update_drives_when_reversing(self, target, gpio):
        robot.UDPServer.return_value.read.return_value = "-25.0,-65.0"
        target.update()
        gpio.return_value.update.assert_called_with(0.0, 25.0, 0.0, 65.0)

    def test_return_true(self, target):
        assert target.update()

    def test_ignore_none(self, target, gpio):
        robot.UDPServer.return_value.read.return_value = None
        target.update()
        assert not gpio.return_value.update.called

    def test_dont_return_true_if_no_message_received(self, target):
        robot.UDPServer.return_value.read.return_value = None
        assert not target.update()
