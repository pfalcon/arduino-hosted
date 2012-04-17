#!/usr/bin/env python
import serial
import arduino


port = serial.Serial('/dev/ttyACM0', 9600, timeout=0.3)
arduino.init(port, debug=1)
from arduino import *

def setup():
    pinMode(LED, OUTPUT)

def loop():
    digitalWrite(0, HIGH)
    delay(1000)
    digitalWrite(0, LOW)
    delay(1000)

arduino.run(globals())
