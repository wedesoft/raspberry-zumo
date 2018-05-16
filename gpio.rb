begin
  require 'rpi_gpio'
rescue LoadError
end


PINS = [7, 11, 13, 15]
FREQ = 500
RPi::GPIO.set_numbering :board


for pin in PINS
  RPi::GPIO.setup pin, as: :output, initialize: :low
end

pwms = PINS.collect do |pin|
  pwm = RPi::GPIO::PWM.new pin, FREQ
  pwm.start 0
end

#pins = [7, 13]  # forward
#pins = [11, 15] # backward
#pins = [7, 15]  # left
#pins = [11, 13] # right
a, b = 0, 2
percent = 100
pwms[a].duty_cycle = percent * 0.7
pwms[b].duty_cycle = percent
#sleep 2

pwms[a].duty_cycle = 0.0
pwms[b].duty_cycle = 0.0

pwms.collect { |pwm| pwm.stop }

RPi::GPIO.reset
