from gpio import GPIO
from udp_server import UDPServer


class Server:
    def __init__(self):
        self.udp_server = UDPServer()
        self.gpio = GPIO()

    def update(self):
        message = self.udp_server.read()
        left_drive, right_drive = (float(number) for number in message.split(','))
        self.gpio.update(max(left_drive, 0), max(-left_drive, 0), max(right_drive, 0), max(-right_drive, 0))


if __name__ == "__main__":
    server = Server()
    while True:
        server.update()
