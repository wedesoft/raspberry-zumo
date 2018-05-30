import socket


class UDPServer:
    def __init__(self, host = '', port = 2200, timeout = 0.0):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        self.socket.settimeout(timeout)

    def read(self):
        try:
            reply, addr = self.socket.recvfrom(64)
            return reply
        except socket.error:
            pass


if __name__ == "__main__":
    server = UDPServer('', 2200)
    while True:
        print(server.read())
