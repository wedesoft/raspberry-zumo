require 'socket'


class UDPServer
  def initialize host = 'raspberrypi.local', port = 2200
    @socket = UDPSocket.new
    @socket.bind host, port
  end

  def read
    reply, from = @socket.recvfrom 20
    reply
  end
end


if __FILE__ == $0
  server = UDPServer.new
  while true
    puts server.read
  end
end
