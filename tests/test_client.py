import pytest
from mock import MagicMock, call
import client
from client import *


@pytest.fixture(autouse=True)
def udp_client(monkeypatch):
    monkeypatch.setattr(client, 'UDPClient', MagicMock(name='udp_client'))
    return client.UDPClient


@pytest.fixture(autouse=True)
def joystick(monkeypatch):
    monkeypatch.setattr(client, 'Joystick', MagicMock(name='joystick'))
    result = client.Joystick
    return result


@pytest.fixture
def target(udp_client, joystick):
    return Client()


class TestClient:
    def test_connect_to_robot(self, target, udp_client):
        assert udp_client.called

    def test_initialize_joystick(self, target, joystick):
        assert joystick.called


class TestClientUpdate:
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

    def test_sends_converted_values(self, target, adapt, udp_client):
        adapt.side_effect = [12.5, 22.5]
        target.update()
        udp_client.return_value.write.assert_called_with("12.50,22.50")
