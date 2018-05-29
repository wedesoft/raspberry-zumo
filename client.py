from udp_client import UDPClient
from joystick import Joystick


class Client:
    deadzone = 4000

    def __init__(self):
        self.udp_client = UDPClient()
        self.joystick = Joystick()

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
        self.udp_client.write("%.2f,%.2f" % (left_drive, right_drive))
