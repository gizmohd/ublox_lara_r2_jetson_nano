#!/usr/bin/python3

import os, sys
import thread
import serial
import time
import Jetson.GPIO as GPIO

class Ublox_lara_r2():
    def __init__(self, port = "/dev/ttyACM2", baudrate = 115200):
        self.cmd_done = False
        self.power_pin = 29
        self.reset_pin = 31
        self.gpio17_pin = 11
        self.gpio16_pin = 36
        self.keep_receive_alive = True        
        self.debug = True
        self.response = ""
        print("Opening Serial Port: "+ port)
        self.comm = serial.Serial(port, baudrate)
   
    def __del__(self):
        self.disabel_rtscts()
        self.cmd_done = True
        self.keep_receive_alive = False

       
    def initialize(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.power_pin, GPIO.OUT) # Setup module power pin
        GPIO.setup(self.reset_pin, GPIO.OUT) # Setup module reset pin 
        GPIO.output(self.power_pin, False)
        GPIO.output(self.reset_pin, False)
       
        self.enable_rtscts()
  
    
    def enable_rtscts(self):
        #os.system("rpirtscts on")
        if self.debug:
            print("rts cts on")


    def disabel_rtscts(self):
        #os.system("rpirtscts off")
        if self.debug:
            print("rts cts off")

    def pwr_key_trigger(self):
        GPIO.output(self.power_pin, True)
        time.sleep(5.0)
        GPIO.output(self.power_pin, False)

    def send(self, cmd, timeout=2):
        # flush all output data
        self.comm.flushOutput()

        # initialize the timer for timeout
        t0 = time.time()
        dt = 0

        # send the command to the serial port
        self.comm.write(cmd+'\r')

        # wait until answer within the alotted time
        while self.comm.inWaiting()==0 and time.time()-t0<timeout:
            pass

        if self.debug:        
            print("\r\n>" + cmd)

        n = self.comm.inWaiting()
        if n>0:
            return self.comm.read(n)
        else:
            return None


    def sendAT(self, cmd, response = None, timeout=1):        
        self.cmd_done=False
        self.response = ""
        attempts = timeout 
        while not self.cmd_done and attempts >= 0:            
            self.response = self.send(cmd)
            if self.debug:
                print('\r\n>'+cmd,)
            time.sleep(0.5)
            if None != response:            
                if self.response.find(response)>=0:
                    self.cmd_done = True
            elif None == response:
                self.cmd_done = True
            attempts = attempts - 1 
            time.sleep(0.5)       

        return (attempts >= 0)

    def getRSSI(self):
        rssi = ""
        self.sendAT("AT+CSQ", 'OK\r\n')
        if self.response != "":
            parts = self.response.split('\r\n')
            # print parts
            for part in parts:
                parse_index = part.find('+CSQ: ')
                if parse_index is not -1:
                    rssi = part[6:].split(',')[0]
                    break
        return rssi

    def reset_power(self):
        #self.debug = False
        print "waking up...",
        sys.stdout.flush()
        if not self.sendAT("AT", "OK\r\n"):
            self.pwr_key_trigger()            
            while not self.sendAT("AT", 'OK\r\n'):
                print '...',
                sys.stdout.flush()
            print('\r\n')
        self.debug = True

