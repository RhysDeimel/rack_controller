from machine import Pin, PWM

FAN_PIN = PWM(Pin(15))
FAN_PIN.freq(25000)  # 25kHz


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class PWMFan:
    def __init__(self, pin=FAN_PIN):
        self.pin = pin
        self._speed = 0

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, val):
        self._speed = max(min(val, 100), 0)

        self.pin.duty_u16(self._as_duty(self._speed))

    def _as_duty(self, val):
        if val == 0:
            return 1

        max_duty = 65535
        duty = max_duty // (100 // val)

        return int(duty)
