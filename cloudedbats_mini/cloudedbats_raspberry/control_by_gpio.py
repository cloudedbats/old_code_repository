#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2016 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import os
import time
import logging
import threading
# Check if GPIO is available.
gpio_available = True
try: import RPi.GPIO as GPIO
except: gpio_available = False

class GpioForControl(object):
    """ Use GPIO for control when running without a graphical user interface. """

    def __init__(self, cloudedbats_mini_object):
        """ """
        self._cloudedbats_mini = cloudedbats_mini_object
        self._logger = logging.getLogger('CloudedBats')
        # Recording control.
        self.rec_on_count = 0
        self.rec_off_count = 0
        self.rec_on_state = False
        self.rec_off_state = False
        self.auto_state = False
        # GPIO
        if not gpio_available:
            self._logger.error('GPIO control: RaspberryPi-GPIO not available.')
            return
        #
        self._setup_gpio()
        self._active = True
        self._start_gpio_check()
        
    def stop(self):
        """ """
        self._active = False
    
    def is_rec_on(self):
        """ """
        self.rec_on_state = False
    
    def is_rec_off(self):
        """ """
        self.rec_off_state = False
    
    def _setup_gpio(self):
        """ """
        GPIO.setmode(GPIO.BOARD) # Use pin numbers (1-40). 
        self._gpio_pin_rec_on = 37 # GPIO 26
        self._gpio_pin_rec_off = 38 # GPIO 20
        
        # Use the built in pull-up resistors. 
        GPIO.setup(self._gpio_pin_rec_on, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._gpio_pin_rec_off, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
    def _start_gpio_check(self):
        """ """
        # Check GPIO activity in a separate thread.
        self._check_gpio_thread = threading.Thread(target = self._check_gpio, args = [])
        self._check_gpio_thread.start()
         
    def _check_gpio(self):
        """ """
        while self._active:
            time.sleep(0.1)
            try:
                # Recording on.
                if GPIO.input(self._gpio_pin_rec_on):
                    self.rec_on_count = 0
                    if self.rec_on_state == True:
                        # Perform action.
                        try:
                            self._logger.info('GPIO control: Auto on.')
                            self._cloudedbats_mini.auto_on()
                        except: pass
                        self.rec_on_state = False
                else:
                    if self.rec_on_count >= 5: # After 0.5 sec.
                        if self.rec_on_state == False:
                            # Perform action.
                            try:
                                self._logger.info('GPIO control: Start rec.')
                                self._cloudedbats_mini.rec_on()
                            except: pass
                            self.rec_on_state = True
                    else:
                        self.rec_on_count += 1
                
                # Use auto mode for recording control.
                if GPIO.input(self._gpio_pin_rec_off):
                    self.rec_off_count = 0
                    if self.rec_off_state == True:
                        # Perform action.
                        if self.rec_on_state == False:
                            try:
                                self._logger.info('GPIO control: Auto on.')
                                self._cloudedbats_mini.auto_on()
                            except: pass
                        self.rec_off_state = False
                else:
                    if self.rec_off_count >= 5: # After 0.5 sec.
                        if self.rec_off_state == False:
                            # Perform action.
                            try:
                                self._logger.info('GPIO control: Rec off.')
                                self._cloudedbats_mini.rec_off()
                            except: pass
                            self.rec_off_state = True
                    else:
                        self.rec_off_count += 1
            except:
                pass

