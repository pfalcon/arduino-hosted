#!/usr/bin/env python
import sys
import os
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
    cmd = "pinmode p%d %s" % (pin, ["in", "out"][mode])
    bus.command(cmd)

def digitalWrite(pin, val):
#    cmd = "p%s.%s=%s" % (pin / 8 + 1, pin % 8, val)
    cmd = "p%d=%d" % (pin, val)
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

def get_port():
    global port
    return port

def detect_port(**kwargs):
    return "/dev/ttyUSB0:115200"
#    raise NotImplementedError("Port detection not implemented, please set BUSNINJA_PORT")

def init(**kwargs):
    global port, bus, SPI, dev_type, LED
    port = kwargs.get('port')

    if port is None:
        port_spec = os.environ.get("BUSNINJA_PORT")
        if not port_spec:
            port_spec = detect_port(**kwargs)
        arr = port_spec.split(":")
        dev_type = None
        baud = 9600
        if len(arr) == 1:
            port_str = arr[0]
        elif len(arr) == 2:
            try:
                baud = int(arr[1])
                port_str = arr[0]
            except ValueError:
                dev_type = arr[0]
                port_str = arr[1]
        elif len(arr) == 3:
                dev_type = arr[0]
                port_str = arr[1]
                baud = int(arr[2])
        else:
            raise ValueError("Invalid syntax for BUSNINJA_PORT: expected [<device_type>:]/dev/<serial>[:<baud>]")
        port = serial.Serial(port_str, baud, timeout=0.3)
        if not dev_type:
            dev_type = "arduino"

        if dev_type == "arduino":
            LED = 13

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
