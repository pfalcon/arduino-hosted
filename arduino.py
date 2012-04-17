#!/usr/bin/env python
import sys
import serial

from buspirate import BusPirate

HIGH = 1
LOW = 0

LED = 0
BUTTON = 3

def digitalWrite(pin, val):
    cmd = "p%s.%s=%s" % (pin / 8 + 1, pin % 8, val)
    bus.command(cmd)

def digitalRead(pin):
    cmd = "p%s.%s?" % (pin / 8 + 1, pin % 8)
    bus.command(cmd)
    resp = bus.get_response()
    assert resp.startswith("READ: "), resp
    return int(resp[-1])

class SPIClass:

    def __init__(self, bus):
        self.bus = bus

    def begin(self):
        self.bus.command("spi")
        # First read byte is hosed, read it up now
        self.bus.command("[r]")
        self.bus.get_response()
        self.bus.get_response()
        self.bus.get_response()

    def csn(self, val):
        if val == LOW:
            self.bus.command("{")
            self.bus.expect_response("CS ENABLED")
        else:
            self.bus.command("}")
            self.bus.expect_response("CS DISABLED")

    def transfer(self, byte):
        self.bus.command(hex(byte))
        self.bus.get_response()
        read = self.bus.get_response()
        assert read.startswith("READ: ")
        return int(read[len("READ: "):], 16)

bus = None
SPI = None

def arduino_init(port, **kwargs):
    global bus, SPI
    bus = BusPirate(port, **kwargs)
    bus.connect()
    SPI = SPIClass(bus)
