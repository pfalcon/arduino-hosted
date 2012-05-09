#!/usr/bin/env python
import arduino
from arduino import *


a = arduino.Arduino(debug=True)

class App:
    def setup(self):
        a.pinMode(a.LED, OUTPUT)

    def loop(self):
        a.digitalWrite(a.LED, HIGH)
        a.delay(1000)
        a.digitalWrite(a.LED, LOW)
        a.delay(1000)


a.run(App())
