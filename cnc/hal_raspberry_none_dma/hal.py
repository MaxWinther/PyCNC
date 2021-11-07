import time

from cnc.hal_raspberry_none_dma import rpgpio
from cnc.pulses import *
from cnc.config import *
from cnc.sensors import thermistor

US_IN_SECONDS = 1000000

gpio = rpgpio.GPIO()
pwm = rpgpio.DMAPWM()
running = False

STEP_PIN_MASK_X = 1 << STEPPER_STEP_PIN_X
STEP_PIN_MASK_Y = 1 << STEPPER_STEP_PIN_Y
STEP_PIN_MASK_Z = 1 << STEPPER_STEP_PIN_Z
STEP_PIN_MASK_E = 1 << STEPPER_STEP_PIN_E


def init():
    """ Initialize GPIO pins and machine itself.
    """
    logging.info("hal init()")
    gpio.init(STEPPER_STEP_PIN_X, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_STEP_PIN_Y, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_STEP_PIN_Z, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_STEP_PIN_E, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_DIR_PIN_X, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_DIR_PIN_Y, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_DIR_PIN_Z, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_DIR_PIN_E, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(ENDSTOP_PIN_X, rpgpio.GPIO.MODE_INPUT_PULLUP)
    gpio.init(ENDSTOP_PIN_Y, rpgpio.GPIO.MODE_INPUT_PULLUP)
    gpio.init(ENDSTOP_PIN_Z, rpgpio.GPIO.MODE_INPUT_PULLUP)
    gpio.init(SPINDLE_PWM_PIN, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(FAN_PIN, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(EXTRUDER_HEATER_PIN, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(BED_HEATER_PIN, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPERS_ENABLE_PIN, rpgpio.GPIO.MODE_OUTPUT)
    gpio.clear(SPINDLE_PWM_PIN)
    gpio.clear(FAN_PIN)
    gpio.clear(EXTRUDER_HEATER_PIN)
    gpio.clear(BED_HEATER_PIN)
    gpio.clear(STEPPERS_ENABLE_PIN)

def spindle_control(percent):
    """ Spindle control implementation.
    :param percent: spindle speed in percent 0..100. If 0, stop the spindle.
    """
    logging.info("spindle control: {}%".format(percent))
    if percent > 0:
        pwm.add_pin(SPINDLE_PWM_PIN, percent)
    else:
        pwm.remove_pin(SPINDLE_PWM_PIN)


def fan_control(on_off):
    """
    Cooling fan control.
    :param on_off: boolean value if fan is enabled.
    """
    if on_off:
        logging.info("Fan is on")
        gpio.set(FAN_PIN)
    else:
        logging.info("Fan is off")
        gpio.clear(FAN_PIN)


def extruder_heater_control(percent):
    """ Extruder heater control.
    :param percent: heater power in percent 0..100. 0 turns heater off.
    """
    if percent > 0:
        pwm.add_pin(EXTRUDER_HEATER_PIN, percent)
    else:
        pwm.remove_pin(EXTRUDER_HEATER_PIN)


def bed_heater_control(percent):
    """ Hot bed heater control.
    :param percent: heater power in percent 0..100. 0 turns heater off.
    """
    if percent > 0:
        pwm.add_pin(BED_HEATER_PIN, percent)
    else:
        pwm.remove_pin(BED_HEATER_PIN)


def get_extruder_temperature():
    """ Measure extruder temperature.
    :return: temperature in Celsius.
    """
    return thermistor.get_temperature(EXTRUDER_TEMPERATURE_SENSOR_CHANNEL)


def get_bed_temperature():
    """ Measure bed temperature.
    :return: temperature in Celsius.
    """
    return thermistor.get_temperature(BED_TEMPERATURE_SENSOR_CHANNEL)


def disable_steppers():
    """ Disable all steppers until any movement occurs.
    """
    logging.info("disable steppers")
    gpio.set(STEPPERS_ENABLE_PIN)


def __calibrate_private(x, y, z, invert):
    """ Copy from org hal
    """
    return False


def calibrate(x, y, z):
    """ Move head to home position till end stop switch will be triggered.
    Do not return till all procedures are completed.
    :param x: boolean, True to calibrate X axis.
    :param y: boolean, True to calibrate Y axis.
    :param z: boolean, True to calibrate Z axis.
    :return: boolean, True if all specified end stops were triggered.
    """
    # enable steppers
    gpio.clear(STEPPERS_ENABLE_PIN)
    logging.info("hal calibrate, x={}, y={}, z={}".format(x, y, z))
    if not __calibrate_private(x, y, z, True):  # move from endstop switch
        return False
    return __calibrate_private(x, y, z, False)  # move to endstop switch


def move(generator):
    """ Move head to specified position
    :param generator: PulseGenerator object.
    """

    running = True

    logging.debug("hal::move() generator={}".format(generator))

    # enable steppers
    gpio.clear(STEPPERS_ENABLE_PIN)

    # generator implements iterator-interface
    for direction, tx, ty, tz, te in generator:

        # set up directions
        if direction:
            pins_to_set = ()
            pins_to_clear = ()

            if tx > 0:
                pins_to_clear.append(STEPPER_DIR_PIN_X)
            elif tx < 0:
                pins_to_set.append(STEPPER_DIR_PIN_X)

            if ty > 0:
                pins_to_clear.append(STEPPER_DIR_PIN_Y)
            elif ty < 0:
                pins_to_set.append(STEPPER_DIR_PIN_Y)

            if tz > 0:
                pins_to_clear.append(STEPPER_DIR_PIN_Z)
            elif tz < 0:
                pins_to_set.append(STEPPER_DIR_PIN_Z)

            if te > 0:
                pins_to_clear.append(STEPPER_DIR_PIN_E)
            elif te < 0:
                pins_to_set.append(STEPPER_DIR_PIN_E)

            gpio.set(pins_to_set)
            gpio.clear(pins_to_clear)
            continue

        pins = ()

        if tx is not None:
            pins.append(STEPPER_STEP_PIN_X)
        if ty is not None:
            pins.append(STEPPER_STEP_PIN_Y)
        if tz is not None:
            pins.append(STEPPER_STEP_PIN_Z)
        if te is not None:
            pins.append(STEPPER_STEP_PIN_E)

        gpio.pulse(pins, STEPPER_PULSE_LENGTH_US)

    running = False

def join():
    """ Wait till motors work.
    """
    logging.debug("hal join()")
    i = 0
    while running:
        time.sleep(0.01)
        i += 1
        if i > 500:
            i = 0
            logging.info("hal join() waited for active dma for another 5s")


def deinit():
    """ De-initialize hardware.
    """
    join()
    disable_steppers()
    pwm.remove_all()
    gpio.clear(SPINDLE_PWM_PIN)
    gpio.clear(FAN_PIN)
    gpio.clear(EXTRUDER_HEATER_PIN)
    gpio.clear(BED_HEATER_PIN)


def watchdog_feed():
    """ Feed hardware watchdog.
    """
    # logging.info("hal::watchdog_feed()")
