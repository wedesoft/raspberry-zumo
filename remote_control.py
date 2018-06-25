#!/usr/bin/env python
import time
from udp_client import UDPClient
from joystick import Joystick


class RemoteControl:
    deadzone = 4000

    def __init__(self):
        self.udp_client = UDPClient()
        self.joystick = Joystick()
        self.auto = False

    @classmethod
    def adapt(cls, value):
        if value > cls.deadzone:
            return (value - cls.deadzone) * 100.0 / (32768 - cls.deadzone)
        elif value < -cls.deadzone:
            return (value + cls.deadzone) * 100.0 / (32768 - cls.deadzone)
        else:
            return 0.0

    def update(self):
        self.joystick.update()
        left_drive  = self.adapt(self.joystick.axis.get(1, 0))
        right_drive = self.adapt(self.joystick.axis.get(4, 0))
        self.auto = (self.auto or self.joystick.button.get(0, False)) and not self.joystick.button.get(1, False)
        self.udp_client.write("%.2f,%.2f,%d" % (left_drive, right_drive, self.auto))


if __name__ == "__main__":
    remote_control = RemoteControl()
    while True:
        remote_control.update()
        time.sleep(0.1)
