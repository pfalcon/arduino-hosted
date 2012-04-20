#!/usr/bin/env python
import time
import re


class BusPirate:

    def __init__(self, serial_port, debug=False):
        self.port = serial_port
        self.debug = debug
        self.current_prompt = None

    def set_mode(self, mode):
        self.command(mode)
        self.current_prompt = {"hiz": "HiZ", "spi": "SPI"}[mode]

    def connect(self):
        self.port.write("\r")
        l = self.port.read(1)
        if l == "\0":
            l = self.port.read(2)
        else:
            l = l + self.port.read(1)
        if l == "\r\n":
            print "Echo detected, turning off"
            self.write("echo off\r")
            l = self.port.readline()
            print `l`
#            assert l == "echo off\r\n"
            l = self.port.read(5)
        else:
            l = l + self.port.read(3)
        assert re.match(r"[A-Za-z]{3}> ", l), "Expected command prompt, got:" + `l`
        self.current_prompt = l[0:3]
        self.port.write("\r")
        self.set_mode("hiz")

    def write(self, s):
        for c in s:
            self.port.write(c)
            time.sleep(0.0015)

    def command(self, s):
        l = self.port.read(5)
        assert l == self.current_prompt + "> ", `l`
        #print "+" + `l`

        if self.debug:
            print ">" + `s`
        #self.port.write(s + "\r")
        for c in s + "\r":
            self.port.write(c)
            time.sleep(0.0015)

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
