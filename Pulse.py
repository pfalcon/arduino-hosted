#!/usr/bin/env python
import serial
import arduino
arduino.init(debug=1)
from arduino import *


def setup():
    pinMode(LED, OUTPUT)


def loop():
    # Produce "1 microsend" pulse of LED
    # In quotes because a board running on few-MHz clock doesn't have enough
    # speed to produce such short pulse, so it will be few times longer likely.
    # A LED also has own inertion, so pulse will be pretty visible.
    digitalPulse_us(LED, HIGH, 1)
    delay(1000)


arduino.run(globals())
