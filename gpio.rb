begin
  require 'rpi_gpio'
rescue LoadError
end


class GPIO
  PINS = [7, 11, 13, 15]
  FREQ = 400

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
    pwms.collect { |pwm| pwm.stop }
    RPi::GPIO.reset
  end
end




#pins = [7, 13]  # forward
#pins = [11, 15] # backward
#pins = [7, 15]  # left
#pins = [11, 13] # right
