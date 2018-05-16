require_relative 'gpio'


class Service
  def initialize
    GPIO.new
  end
end
