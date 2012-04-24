#!/usr/bin/env python
import arduino


arduino.init(debug=True)
from arduino import *

def setup():
    pinMode(LED, OUTPUT)

def loop():
    digitalWrite(LED, HIGH)
    delay(1000)
    digitalWrite(LED, LOW)
    delay(1000)

arduino.run(globals())
