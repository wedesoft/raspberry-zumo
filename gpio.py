import signal
try:
    import RPi.GPIO
except RuntimeError:
    pass


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
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)

    def update(self, *values):
        for pwm, value in zip(self.pwms, values):
            pwm.ChangeDutyCycle(value)

    def stop(self):
        for pwm in self.pwms:
            pwm.stop()
        RPi.GPIO.cleanup()
