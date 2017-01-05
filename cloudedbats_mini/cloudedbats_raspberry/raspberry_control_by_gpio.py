#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2016 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import os
import time
import logging.handlers
# Check if GPIO is available.
gpio_available = True
try: import RPi.GPIO as GPIO
except: gpio_available = False

class RaspberryPiGpioForControl(object):
    """ For Raspberry Pi. Use GPIO to control shutdown and low power mode. """

    def __init__(self):
        """ """
        # Set up logging.
        self._logger = logging.getLogger('RaspberryControl')
        self._logging_setup()
        #
        self._logger.info('')
        self._logger.info('=== Raspberry Pi GPIO for control. ===')
        self._logger.info('')
        #
        if not gpio_available:
            self._logger.error('GPIO control: GPIO not available.')
            self._logger.error('GPIO control: Terminated.')
            return
        #
        self._setup_gpio()
        #
        self.low_power_state = False
        # Start the loop.
        self._active = True
        self._run_gpio_check()
        
    def stop(self):
        """ """
        self._active = False
        
    def low_power_mode_on(self):
        """ """
        # Turn WiFi off.
        self._logger.info('GPIO control: RPi GPIO control. WiFi off.')
        try:
            os.system('sudo ifconfig wlan0 down')
            #          sudo ifdown wlan0
        except:
            self._logger.error('GPIO control: WiFi off failed.')
            
        # Turn HDMI off.
        self._logger.info('GPIO control: RPi GPIO control. HDMI off.')
        try:
            os.system('/usr/bin/tvservice -o')
        except:
            self._logger.error('GPIO control: HDMI off failed.')  
                  
        
    def low_power_mode_off(self):
        """ """
        # Turn WiFi on.
        self._logger.info('GPIO control: RPi GPIO control. WiFi on.')
        try:
            os.system('sudo ifconfig wlan0 up')
            #          sudo ifup wlan0
        except:
            self._logger.error('GPIO control: WiFi on failed.')  
            
        # Turn HDMI on.
        self._logger.info('GPIO control: RPi GPIO control. HDMI on.')
        try:
            os.system('/usr/bin/tvservice -p')
        except:
            self._logger.error('GPIO control: HDMI on failed.')
        
    def _setup_gpio(self):
        """ """
        GPIO.setmode(GPIO.BOARD) # Use pin numbers, 1-40. 
        self._gpio_pin_low_power = 36 # GPIO 16
        self._gpio_pin_shutdown = 40 # GPIO 21
        # Use the built in pull-up resistors. 
        GPIO.setup(self._gpio_pin_low_power, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._gpio_pin_shutdown, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
    def _run_gpio_check(self):
        """ """
        while self._active:
            # Check each sec.
            time.sleep(1.0)
            try:
                # Raspberry Pi shutdown.
                if GPIO.input(self._gpio_pin_shutdown):
                    # High = inactive.
                    pass
                else:
                    # Low = active.
                    time.sleep(0.1) # Check if stable.
                    if not GPIO.input(self._gpio_pin_shutdown):                        
                        # Perform action.
                        try:
                            self._logger.info('GPIO control: Raspberry Pi shutdown.')
                            os.system('sudo shutdown -h now')
                        except:
                            self._logger.error('GPIO control: Shutdown failed.')
                
                # Raspberry low power.
                if GPIO.input(self._gpio_pin_low_power):
                    # High = inactive.
                    time.sleep(0.1) # Check if stable.
                    if GPIO.input(self._gpio_pin_low_power):                        
                        if self.low_power_state == True:
                            # Perform action.
                            self.low_power_mode_off()
                            self.low_power_state = False
                else:
                    # Low = active.
                    time.sleep(0.1) # Check if stable.
                    if not GPIO.input(self._gpio_pin_low_power):                        
                        if self.low_power_state == False:
                            # Perform action.
                            self.low_power_mode_on()
                            self.low_power_state = True
                    else:
                        self.low_power_count += 1
            except:
                pass

    
    def _logging_setup(self):
        """ """
        log = logging.getLogger('RaspberryControl')
        log.setLevel(logging.INFO)
        # Define rotation log files.
        log_file_name = 'raspberry_log.txt'
        dir_path = os.path.dirname(os.path.abspath(__file__))
        log_handler = logging.handlers.RotatingFileHandler(os.path.join(dir_path, log_file_name),
                                                           maxBytes = 128*1024,
                                                           backupCount = 10)
        log_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-10s : %(message)s '))
        log_handler.setLevel(logging.DEBUG)
        log.addHandler(log_handler)


### Main. ###
if __name__ == "__main__":
    """ """
    RaspberryPiGpioForControl()
    
