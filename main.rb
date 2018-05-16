require_relative 'udp_client'
require_relative 'joystick'


class Main
  def initialize
    UDPClient.new
    JoyStick.new
  end
end
