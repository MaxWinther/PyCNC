import RPi.GPIO as GPIO
import time
import logging


class GPIONoneDMA(object):
    MODE_OUTPUT = 1
    MODE_INPUT_NOPULL = 2
    MODE_INPUT_PULLUP = 3
    MODE_INPUT_PULLDOWN = 4

    def __init__(self):
        logging.info("GPIO(non-dma)")

    def init(pin, mode):
        if mode == GPIONoneDMA.MOD_OUTPUT:
            GPIO.setup(pin, GPIO.OUT)

        elif mode == GPIONoneDMA.MODE_INPUT_PULLUP:
            GPIO.setup(pin, GPIO.IN)

    @staticmethod
    def set(self, pin):
        GPIO.output(pin, GPIO.HIGH)

    @staticmethod
    def clear(self, pin):
        GPIO.output(pin, GPIO.LOW)

    @staticmethod
    def pulse(self, pins, pulselength):
        GPIO.output(pins, GPIO.HIGH)
        time.sleep(pulselength)
        GPIO.output(pins, GPIO.LOW)


class PWMNoneDMA(object):
    def __init__(self):
        logging.info("NoneDMAPWM")

    def add_pin(self, pin, duty_cycle):
        logging.info("add_pin()")

    def remove_pin(self, pin):
        logging.info("remove_pin()")

    def remove_all(self):
        logging.info("remove_all()")
