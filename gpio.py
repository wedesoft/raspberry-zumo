import RPi.GPIO


class GPIO:
    PINS = [7, 11, 13, 15]
    FREQ = 800

    def __init__(self):
        RPi.GPIO.setmode(RPi.GPIO.BOARD)
        for pin in self.PINS:
            RPi.GPIO.setup(pin, RPi.GPIO.OUT)
        self.pwms = [RPi.GPIO.PWM(pin, self.FREQ) for pin in self.PINS]
        for pwm in self.pwms:
            pwm.start(0)

    def update(*values):
        for pwm, value in self.pwms.zip(values):
            pwm.ChangeDutyCycle(value)
