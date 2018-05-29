import socket


class UDPServer:
    def __init__(self, host = 'raspberrypi.local', port = 2200):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))

    def read(self):
        reply, addr = self.socket.recvfrom(64)
        return reply


if __name__ == "__main__":
    server = UDPServer('', 2200)
    while True:
        print(server.read())
