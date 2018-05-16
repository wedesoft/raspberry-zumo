require_relative 'udp_client'
require_relative 'joystick'


class Main
  def initialize
    @client = UDPClient.new
    @joystick = Joystick.new
  end

  def update
    @joystick.update
    @client.write "#{@joystick.axis[0] or 0},#{@joystick.axis[1] or 0}"
  end
end
