#!/usr/bin/env python
"""
Version of Blink.py using object-oriented board API.
"""
import arduino
from arduino import *


class App:
    def __init__(self, board):
        self.b = board

    def setup(self):
        self.b.pinMode(self.b.LED, OUTPUT)

    def loop(self):
        self.b.digitalWrite(self.b.LED, HIGH)
        self.b.delay(1000)
        self.b.digitalWrite(self.b.LED, LOW)
        self.b.delay(1000)


board = arduino.Arduino(debug=True)
board.run(App(board))
