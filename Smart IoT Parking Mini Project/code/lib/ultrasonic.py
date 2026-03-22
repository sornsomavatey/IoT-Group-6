from machine import Pin
import time


class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)

    def read_cm(self):
        self.trig.off()
        time.sleep_us(2)
        self.trig.on()
        time.sleep_us(10)
        self.trig.off()

        timeout = time.ticks_add(time.ticks_us(), 30000)
        while self.echo.value() == 0:
            if time.ticks_diff(timeout, time.ticks_us()) <= 0:
                return -1

        start = time.ticks_us()
        timeout = time.ticks_add(start, 30000)
        while self.echo.value() == 1:
            if time.ticks_diff(timeout, time.ticks_us()) <= 0:
                return -1

        end = time.ticks_us()
        duration = time.ticks_diff(end, start)
        distance = (duration * 0.0343) / 2
        if distance < 2 or distance > 400:
            return -1
        return round(distance, 1)
