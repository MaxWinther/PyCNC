import RPi.GPIO as GPIORASPB
import time


class GPIO(object):
    MODE_OUTPUT = 1
    MODE_INPUT_NOPULL = 2
    MODE_INPUT_PULLUP = 3
    MODE_INPUT_PULLDOWN = 4

    @staticmethod
    def init(pin, mode):
        if mode == GPIO.MOD_OUTPUT:
            GPIORASPB.setup(pin, GPIORASPB.OUT)

        elif mode == GPIO.MODE_INPUT_PULLUP:
            GPIORASPB.setup(pin, GPIORASPB.IN)

    @staticmethod
    def set(self, pin):
        GPIORASPB.output(pin, GPIORASPB.HIGH)

    @staticmethod
    def clear(self, pin):
        GPIORASPB.output(pin, GPIORASPB.LOW)

    @staticmethod
    def pulse(self, pins, pulselength):
        GPIO.output(pins, GPIO.HIGH)
        time.sleep(pulselength)
        GPIO.output(pins, GPIO.LOW)
