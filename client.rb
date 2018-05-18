#!/usr/bin/env ruby
require_relative 'udp_client'
require_relative 'joystick'


class Client
  def initialize
    @client = UDPClient.new
    @joystick = Joystick.new
  end

  def update
    @joystick.update
    @client.write "#{@joystick.axis[1] or 0},#{@joystick.axis[4] or 0}"
  end
end


if __FILE__ == $0
  main = Client.new
  while true
    main.update
    sleep 0.01
  end
end
