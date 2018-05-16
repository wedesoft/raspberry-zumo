require 'socket'


class Client
  def initialize host = 'raspberrypi.local', port = 2200
    @socket = UDPSocket.new
    @socket.connect host, port
  end

  def write str
    @socket.print str
  end
end


client = Client.new
while true
  str = STDIN.readline.chomp
  break if str.empty?
  client.write str
end
