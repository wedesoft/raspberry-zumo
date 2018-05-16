require_relative 'udp_client'
require_relative 'joystick'


class Main
  def initialize
    @client = UDPClient.new
    @joystick = Joystick.new
  end

  def update
    @joystick.update
    @client.write '0,0'
  end
end
