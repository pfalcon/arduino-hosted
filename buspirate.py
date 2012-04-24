#!/usr/bin/env python
import time
import re


class BusPirate:

    def __init__(self, serial_port, debug=False, soft_uart=False):
        self.port = serial_port
        self.debug = debug
        self.soft_uart = soft_uart
        self.current_prompt = None

    def set_mode(self, mode):
        self.command(mode)
        self.current_prompt = {"hiz": "HiZ", "spi": "SPI"}[mode]

    def wait_for_connect(self):
        # Arduino is reset on each serial device open, and it may take
        # some time for it to init
        for i in xrange(400):
            self.write("\r")
            l = self.port.read(1)
#            print "1:", `l`
            if l and l != "\0":
                return l
            time.sleep(0.05)
        raise ValueError("Device doesn't respond")

    def connect(self):
      try:
        l = self.wait_for_connect()
        if l == "\0":
            l = self.port.read(2)
        else:
            l = l + self.port.read(1)
#        print "2:", `l`
        if l == "\r\n":
            print "Echo detected, turning off"
            print "> echo 0"
            self.write("echo 0\r")
            l = self.port.readline()
#            print "3:", `l`
#            assert l == "echo 0\r\n"
            l = self.port.read(5)
#            print "4:", `l`
        else:
            l = l + self.port.read(3)
        assert re.match(r"[A-Za-z]{3}> ", l), "Expected command prompt, got:" + `l`
        self.current_prompt = l[0:3]
        self.write("\r")
        self.set_mode("hiz")
      except:
        self.port.read(100)
        raise

    def write(self, s):
        if self.soft_uart:
            # Workaround for software uart like in TI Launchpad for example:
            # send data byte by byte, with delay on our side
            for c in s:
                self.port.write(c)
                time.sleep(0.0015)
        else:
            self.port.write(s)

    def command(self, s):
        l = self.port.read(5)
        assert l == self.current_prompt + "> ", `l`
        #print "+" + `l`

        if self.debug:
            print ">" + `s`
        self.write(s + "\r")

    def get_response(self):
        resp = self.port.readline()
        assert resp[-2:] == "\r\n"
        resp = resp[:-2]
        if self.debug:
            print "<" + `resp`
        return resp

    def expect_response(self, expected):
        r = self.get_response()
        assert r == expected, "Expected: %s, got: %s" % (expected, r)
