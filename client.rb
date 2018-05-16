require 'socket'


class Client
  def initialize host = 'raspberrypi.local', port = 2200
    @socket = UDPSocket.new
    @socket.connect host, port
  end

  def write str
    @socket.puts str
  end
end


Client.new.write 'hello'
