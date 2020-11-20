#!/usr/bin/env python
# coding: utf-8

# In[4]:


import sys
import logging
import serial
import serial.tools.list_ports
import serial.serialutil
import struct
import time



logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
)

def findUsbPort(hwid):

    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if hwid.upper() in p.hwid:
            logging.info("ERV found on %s", p)
            return p.device     
        else: 
            logging.error("ERV not found") 
            raise RuntimeError("232 adaptor with PID=1A86:7523 not found")
    return None

class ERV(serial.Serial):

    #commands
    #last two hex are little-endian sum checks
    pos_home = b'\xCC\x00\x45\x00\x00\xDD\xEE\x01' #move valve to home position
    pos_1 = b'\xCC\x00\x44\x01\x00\xDD\xEE\x01' #move valve to position 1
    pos_2 = b'\xCC\x00\x44\x02\x00\xDD\xEF\x01' #move valve to position 2
    req_valve = b'\xcc\x00\x3e\x00\x00\xDD\xE7\x01' #request valve status
    req_motor = b'\xCC\x00\x4A\x00\x00\xDD\xF3\x01' #request motor status
    
    def __init__(self):
        super().__init__(baudrate = 9600, timeout=1)
        self.port = findUsbPort("PID=1A86:7523")
        self.open()
        self.flushInput()
        self.flushOutput()

    def valveStatus(self): 
        while not self.motorReady(): 
            time.sleep(1)
        self.flushInput()
        self.flushOutput()
        self.write(self.req_valve)
        response = self.read(8)
        b3 = struct.unpack('BBBBBBBb',response)[3:5]  #B3 byte indicates position
        if (b3[0] == 0): logging.info('Valve is in Home Position')
        elif (b3[0] == 1): logging.info('Valve is in Position 1')
        elif (b3[0] == 2): logging.info('Valve is in Position 2')
        else:
            logging.error('%s is an unknown position', str(response))
            raise RuntimeError(str(response) + ' is an unknown position')
        return b3[0]

    def motorReady(self):
        self.write(self.req_motor)
        time.sleep(.1)
        response = self.read(8)
        b2 = struct.unpack('BBBBBBBb',response)[2] #B2 == 00 means that the motor is ready
        if (b2 == 0x00):
            return True
        else: 
            logging.info('Waiting for motor')
            return False


    def movePosition(self, position):
        while not self.motorReady(): 
            time.sleep(1)
        if (position == 0): 
            self.write(self.pos_home)
            self.read(8)
            logging.info('Moving to home position')
        elif (position == 1): 
            self.write(self.pos_1)
            self.read(8)
            logging.info('Moving to position 1')
        elif (position == 2): 
            self.write(self.pos_2)
            self.read(8)
            logging.info('Moving to position 2')
        pos = self.valveStatus()
        if not (position == pos): 
            logging.error('ERV movement failure')
            raise RuntimeError("ERV failed to move: {} != {}".format(position,pos))
        