#!/usr/bin/env python
from gpio import GPIO
from udp_server import UDPServer
from camera import Camera
from logger import Logger
from data import Operation, to_gray, down_sample
import config


class Robot:
    def __init__(self):
        self.udp_server = UDPServer()
        self.gpio = GPIO()
        self.camera = Camera()
        self.logger = Logger()
        self.drives = [0, 0]
        self.model = None
        self.auto = False

    def update(self):
        message = self.udp_server.read()
        image = self.camera.capture()
        if message:
            left_drive, right_drive, auto = message.split(',')
            self.auto = auto != '0'
            self.drives = (float(left_drive), float(right_drive))
        if self.auto:
            if not self.model:
                self.model = Operation.restore('./model')
            self.drives = self.model(down_sample(to_gray(image), config.sampling))[0]
        else:
            if self.drives[0] or self.drives[1]:
                self.logger.log(image, *self.drives)
        self.gpio.update(max( self.drives[0], 0),
                         max(-self.drives[0], 0),
                         max( self.drives[1], 0),
                         max(-self.drives[1], 0))
        return message


if __name__ == "__main__":
    robot = Robot()
    while True:
        robot.update()
