import sys
import socket


class UDPClient:
    def __init__(self, host = 'raspberrypi.local', port = 2200):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port

    def write(self, text):
        self.socket.sendto(text, (self.host, self.port))


if __name__ == "__main__":
    client = UDPClient()
    while True:
        text = sys.stdin.readline().rstrip()
        if not text:
            break
        client.write(text)
