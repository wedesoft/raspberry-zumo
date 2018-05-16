require 'socket'


class Server
  def initialize host = 'raspberrypi.local', port = 2200
    @socket = UDPSocket.new
    @socket.bind host, port
  end

  def read
    reply, from = @socket.recvfrom 20
    reply
  end
end


puts Server.new.read
