#!/usr/bin/env python
from gpio import GPIO
from udp_server import UDPServer


class Robot:
    def __init__(self):
        self.udp_server = UDPServer()
        self.gpio = GPIO()

    def update(self):
        message = self.udp_server.read()
        if message:
            left_drive, right_drive = (float(number) for number in message.split(','))
            self.gpio.update(max(left_drive, 0), max(-left_drive, 0), max(right_drive, 0), max(-right_drive, 0))
            return True


if __name__ == "__main__":
    server = Robot()
    while True:
        server.update()
