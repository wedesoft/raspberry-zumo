require_relative 'udp_client'
require_relative 'joystick'


class Main
  def initialize
    UDPClient.new
    Joystick.new
  end
end
