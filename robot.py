#!/usr/bin/env python
from gpio import GPIO
from udp_server import UDPServer
from camera import Camera
from logger import Logger


class Robot:
    def __init__(self):
        self.udp_server = UDPServer()
        self.gpio = GPIO()
        self.camera = Camera()
        self.logger = Logger()
        self.drives = [0, 0]

    def update(self):
        message = self.udp_server.read()
        if message:
            left_drive, right_drive, button = message.split(',')
            self.drives = (float(left_drive), float(right_drive))
            self.gpio.update(max( self.drives[0], 0),
                             max(-self.drives[0], 0),
                             max( self.drives[1], 0),
                             max(-self.drives[1], 0))
        image = self.camera.capture()
        if self.drives[0] or self.drives[1]:
            self.logger.log(image, *self.drives)
        return message


if __name__ == "__main__":
    robot = Robot()
    while True:
        robot.update()
