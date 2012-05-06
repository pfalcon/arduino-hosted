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


class SerialMockClass:

    def __init__(self):
        pass

    def begin(self, baud):
        pass

    def print_(self, data, format=None):
        if not format:
            sys.stdout.write(data)
        elif format == HEX:
            sys.stdout.write(hex(data))

    def println(self, data, format=None):
        self.print_(data, format)
        print


class Arduino:

    def __init__(self, port=None, board=None, debug=False):
        self.board_config = None
        self.port = port
        self.board_type = None
        if self.port is None:
            if board:
                port_spec = self.get_board_config(board)
            elif "BUSNINJA_PORT" in os.environ:
                port_spec  = os.environ["BUSNINJA_PORT"]
            else:
                port_spec = self.detect_board()

            self.board_type, serial_dev, baud = self.parse_port_spec(port_spec)
            self.port = serial.Serial(serial_dev, baud, timeout=0.3)

        if self.board_type is None:
            self.board_type = "arduino"

        soft_uart = False
        if self.board_type == "arduino":
            self.LED = 13
        else:
            soft_uart = True
            self.LED = 0

        self.bus = BusPirate(self.port, soft_uart=soft_uart, debug=debug)
        self.bus.connect()
        self.SPI = SPIClass(self.bus)
        self.Serial = SerialMockClass()


    def detect_board(self):
        return "arduino:/dev/ttyUSB0:115200"


    def parse_port_spec(self, port_spec):
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
                board_type = arr[0]
                port_str = arr[1]
        elif len(arr) == 3:
                board_type = arr[0]
                port_str = arr[1]
                baud = int(arr[2])
        else:
            raise ValueError("Invalid syntax for BUSNINJA_PORT: expected [<device_type>:]/dev/<serial>[:<baud>]")
        return board_type, port_str, baud

    def get_board_config(self, board):
        if self.board_config is None:
            self.board_config = {}
            f = open("board.cfg")
            for l in f:
                k, v = [s.strip() for s in l.split("=", 1)]
                self.board_config[k] = v
        return self.board_config.get(board)

    def get_board_type(self):
        return self.board_type

    def run(self, app):
        try:
            app.setup()
            while True:
                app.loop()
        except:
            self.port.read(100)
            raise

    def run_func(self, func):
        try:
            func()
        except:
            self.port.read(100)
            raise


    def delay(self, miliseconds):
        time.sleep(float(miliseconds) / 1000)

    def pinMode(self, pin, mode):
        cmd = "pinmode p%d %s" % (pin, ["in", "out"][mode])
        self.bus.command(cmd)

    def digitalWrite(self, pin, val):
    #    cmd = "p%s.%s=%s" % (pin / 8 + 1, pin % 8, val)
        cmd = "p%d=%d" % (pin, val)
        self.bus.command(cmd)

    def digitalRead(self, pin):
        cmd = "p%s.%s?" % (pin / 8 + 1, pin % 8)
        self.bus.command(cmd)
        resp = self.bus.get_response()
        assert resp.startswith("READ: "), resp
        return int(resp[-1])

    def digitalPulse_us(self, pin, val, delay_us):
        cmd = "p%d=%d &:%d p%d=%d" % (pin, val, delay_us, pin, not val)
        self.bus.command(cmd)


def run(globals):
    try:
        globals["setup"]()
        while True:
            globals["loop"]()
    except:
        port.read(100)
        raise
