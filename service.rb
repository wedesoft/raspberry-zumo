require_relative 'gpio'
require_relative 'udp_server'


class Service
  def initialize
    GPIO.new
    @socket = UDPServer.new
  end

  def update
    @socket.read
  end
end


if __FILE__ == $0
  Service = Service.new
  while true
    service.update
  end
end
