#!/usr/bin/env python
import sys
import time

import serial

from buspirate import BusPirate


HIGH = 1
LOW = 0

INPUT = 0
OUTPUT = 1

LED = 0
BUTTON = 3


def delay(miliseconds):
    time.sleep(float(miliseconds) / 1000)

def pinMode(pin, mode):
    # Not implemented so far
    pass

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
        self.bus.set_mode("spi")
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


port = None
bus = None
SPI = None

def init(_port, **kwargs):
    global port, bus, SPI
    port = _port
    bus = BusPirate(port, **kwargs)
    bus.connect()
    SPI = SPIClass(bus)

def run(globals):
    try:
        globals["setup"]()
        while True:
            globals["loop"]()
    except:
        port.read(100)
        raise
