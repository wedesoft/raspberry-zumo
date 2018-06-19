import pytest
from mock import MagicMock, call
import robot
from robot import *


@pytest.fixture(autouse=True)
def udp_server(monkeypatch):
    monkeypatch.setattr(robot, 'UDPServer', MagicMock(name='udp_server'))
    robot.UDPServer.return_value.read.return_value = "25.0,65.0,0"
    return robot.UDPServer


@pytest.fixture(autouse=True)
def gpio(monkeypatch):
    monkeypatch.setattr(robot, 'GPIO', MagicMock(name='gpio'))
    return robot.GPIO


@pytest.fixture(autouse=True)
def camera(monkeypatch):
    monkeypatch.setattr(robot, 'Camera', MagicMock(name='camera'))
    return robot.Camera


@pytest.fixture(autouse=True)
def image(camera):
    return camera.return_value.capture.return_value


@pytest.fixture(autouse=True)
def logger(monkeypatch):
    monkeypatch.setattr(robot, 'Logger', MagicMock(name='logger'))
    return robot.Logger


@pytest.fixture
def target(udp_server, gpio, camera):
    return Robot()


@pytest.fixture(autouse=True)
def operation(monkeypatch):
    monkeypatch.setattr(robot, 'Operation', MagicMock(name='Operation'))
    robot.Operation.restore.return_value.return_value = [12.0, 16.0]
    return robot.Operation


@pytest.fixture(autouse=True)
def to_gray(monkeypatch):
    monkeypatch.setattr(robot, 'to_gray', MagicMock(name='to_gray'))
    robot.to_gray.side_effect = lambda image: image.gray
    return robot.to_gray


@pytest.fixture(autouse=True)
def down_sample(monkeypatch):
    monkeypatch.setattr(robot, 'down_sample', MagicMock(name='down_sample'))
    robot.down_sample.side_effect = lambda image, rate: image.down_sample
    return robot.down_sample


class TestRobot:
    def test_start_udp_server(self, target, udp_server):
        assert udp_server.called

    def test_start_drives(self, target, gpio):
        assert gpio.called

    def test_initialises_camera(self, target, camera):
        assert camera.called

    def test_initialises_logging(self, target, logger):
        assert logger.called


class TestRobotUpdate:
    def test_reads_udp_data(self, target, udp_server):
        target.update()
        assert udp_server.return_value.read.called

    def test_update_drives(self, target, gpio):
        target.update()
        gpio.return_value.update.assert_called_with(25.0, 0.0, 65.0, 0.0)

    def test_update_drives_when_reversing(self, target, gpio, udp_server):
        udp_server.return_value.read.return_value = "-25.0,-65.0,0"
        target.update()
        gpio.return_value.update.assert_called_with(0.0, 25.0, 0.0, 65.0)

    def test_return_true(self, target):
        assert target.update()

    def test_ignore_none(self, target, gpio, udp_server):
        udp_server.return_value.read.return_value = None
        target.update()
        gpio.return_value.update.assert_called_with(0.0, 0.0, 0.0, 0.0)

    def test_dont_return_true_if_no_message_received(self, target, udp_server):
        udp_server.return_value.read.return_value = None
        assert not target.update()

    def test_capture_image(self, target, camera):
        target.update()
        assert camera.return_value.capture.called

    def test_record_image_and_control(self, target, camera, logger, image):
        target.update()
        logger.return_value.log.assert_called_with(image, 25.0, 65.0)

    def test_record_nothing_initially(self, target, camera, logger, udp_server):
        udp_server.return_value.read.return_value = None
        target.update()
        assert not logger.return_value.log.called

    def test_record_previous_control_setting_if_no_message_received(self, target, camera, logger, udp_server, image):
        target.update()
        udp_server.return_value.read.return_value = None
        target.update()
        assert logger.return_value.log.call_args_list == [call(image, 25.0, 65.0), call(image, 25.0, 65.0)]

    def test_no_recording_if_drives_are_zero(self, target, udp_server, logger):
        udp_server.return_value.read.return_value = "0,0,0"
        target.update()
        assert not logger.return_value.log.called

    def test_auto_drive_loads_model(self, target, operation, udp_server):
        udp_server.return_value.read.return_value = "0,0,1"
        target.update()
        operation.restore.assert_called_with('./model')

    def test_only_load_model_in_auto_mode(self, target, operation):
        target.update()
        assert not operation.restore.called

    def test_only_load_model_once(self, target, operation, udp_server):
        udp_server.return_value.read.return_value = "0,0,1"
        target.update()
        target.update()
        assert operation.restore.call_count == 1

    def test_get_control_values(self, target, operation, udp_server, image):
        udp_server.return_value.read.return_value = "0,0,1"
        target.update()
        operation.restore.return_value.assert_called_with(image.gray.down_sample)

    def test_no_logging_in_auto_mode(self, target, udp_server, logger):
        udp_server.return_value.read.return_value = "25.0,65.0,1"
        target.update()
        assert not logger.return_value.log.called

    def test_use_auto_control_values(self, target, udp_server, gpio):
        udp_server.return_value.read.return_value = "0,0,1"
        target.update()
        gpio.return_value.update.assert_called_with(12.0, 0.0, 16.0, 0.0)
