begin
  require 'rpi_gpio'
rescue RuntimeError
end


class GPIO
  #  7 and 13: forward
  # 11 and 15: backward
  #  7 and 15: left
  # 11 and 13: right
  PINS = [7, 11, 13, 15]
  FREQ = 800

  def initialize
    RPi::GPIO.set_numbering :board
    for pin in PINS
      RPi::GPIO.setup pin, as: :output, initialize: :low
    end
    @pwms = PINS.collect do |pin|
      pwm = RPi::GPIO::PWM.new pin, FREQ
      pwm.start 0
    end
  end

  def update *values
    @pwms.zip(values).each do |pwm, value|
      pwm.duty_cycle = value
    end
  end

  def stop
    @pwms.collect { |pwm| pwm.stop }
    RPi::GPIO.reset
  end
end
