import pytest
from mock import MagicMock, call
import remote_control
from remote_control import *


@pytest.fixture(autouse=True)
def udp_client(monkeypatch):
    monkeypatch.setattr(remote_control, 'UDPClient', MagicMock(name='udp_client'))
    return remote_control.UDPClient


@pytest.fixture(autouse=True)
def joystick(monkeypatch):
    monkeypatch.setattr(remote_control, 'Joystick', MagicMock(name='joystick'))
    return remote_control.Joystick


@pytest.fixture
def target(udp_client, joystick):
    return RemoteControl()


class TestRemoteControl:
    def test_connect_to_robot(self, target, udp_client):
        assert udp_client.called

    def test_initialize_joystick(self, target, joystick):
        assert joystick.called


class TestRemoteControlAdapt:
    def test_zero(self):
        assert RemoteControl.adapt(0) == 0.0

    def test_scale(self):
        assert RemoteControl.adapt(32768) == 100.0

    def test_deadzone(self):
        assert RemoteControl.adapt(RemoteControl.deadzone) == 0.0

    def test_scale_from_deadzone(self):
        assert RemoteControl.adapt(RemoteControl.deadzone + 1) < 1.0

    def test_negative_scale(self):
        assert RemoteControl.adapt(-32768) == -100.0

    def test_negative_deadzone(self):
        assert RemoteControl.adapt(-RemoteControl.deadzone) == 0.0

    def test_scale_from_negative_deadzone(self):
        assert RemoteControl.adapt(-RemoteControl.deadzone - 1) > -1.0


class TestRemoteControlUpdate:
    @pytest.fixture(autouse=True)
    def adapt(self, target, monkeypatch):
        monkeypatch.setattr(target, 'adapt', MagicMock(name='adapt'))
        return target.adapt

    def test_should_update_the_joystick(self, target, joystick):
        target.update()
        assert joystick.return_value.update.called

    def test_invokes_axis_conversion(self, target, joystick, adapt):
        joystick.return_value.axis = {1: "left-axis", 4: "right-axis"}
        target.update()
        assert adapt.call_args_list == [call("left-axis"), call("right-axis")]

    def test_uses_zero_until_axis_defined(self, target, adapt, joystick):
        joystick.return_value.axis = {}
        target.update()
        assert adapt.call_args_list == [call(0), call(0)]

    def test_sends_converted_values(self, target, adapt, udp_client, joystick):
        adapt.side_effect = [12.5, 22.5]
        joystick.return_value.button = {}
        target.update()
        udp_client.return_value.write.assert_called_with("12.50,22.50,0")

    def test_sends_first_button_pressed(self, target, adapt, udp_client, joystick):
        adapt.side_effect = [12.5, 22.5]
        joystick.return_value.button = {0: True}
        target.update()
        udp_client.return_value.write.assert_called_with("12.50,22.50,1")
