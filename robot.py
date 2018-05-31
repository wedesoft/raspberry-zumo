#!/usr/bin/env python
from gpio import GPIO
from udp_server import UDPServer
from camera import Camera


class Logger:
    pass


class Robot:
    def __init__(self):
        self.udp_server = UDPServer()
        self.gpio = GPIO()
        self.camera = Camera()
        self.logger = Logger()
        self.drives = None

    def update(self):
        message = self.udp_server.read()
        if message:
            self.drives = tuple(float(number) for number in message.split(','))
            self.gpio.update(max( self.drives[0], 0),
                             max(-self.drives[0], 0),
                             max( self.drives[1], 0),
                             max(-self.drives[1], 0))
        if self.drives:
            image = self.camera.capture()
            self.logger.log(image, *self.drives)
        return message


if __name__ == "__main__":
    robot = Robot()
    while True:
        robot.update()
