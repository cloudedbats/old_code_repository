#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2016 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import os
import time
import datetime
import logging
import threading
import cloudedbats_core

class WurbScheduler(object):
    """ """
    def __init__(self, cloudedbats_mini_object):
        """ """
        self._cloudedbats_mini = cloudedbats_mini_object
        self.cloudedbats_config = self._cloudedbats_mini.cloudedbats_config
        self._logger = logging.getLogger('CloudedBats')
        #
        self._scheduler_active = False
        self._thread_active = False
        self._scheduler_thread = None
        self._start()

    def activate(self):
        """ """
        self._scheduler_active = True
    
    def deactivate(self):
        """ """
        self._scheduler_active = False
    
    def _scheduler_rec_active(self):
        """ Scheduler action. """
        if not cloudedbats_core.SoundRecorder().is_running():
            self._logger.info('Scheduler: Start recording.')
            self._cloudedbats_mini.start_recording()
            # WiFi.
            if self.cloudedbats_config.get('wifi_off_during_rec', 'False') == 'True':
                self._cloudedbats_mini.wifi_off()
    
    def _scheduler_rec_inactive(self):
        """ Scheduler action. """
        if cloudedbats_core.SoundRecorder().is_running():
            self._logger.info('Scheduler: Stop recording.')
            self._cloudedbats_mini.stop_recording()
            # WiFi.
            if self.cloudedbats_config.get('wifi_off_during_rec', 'False') == 'True':
                self._cloudedbats_mini.wifi_on()
    
    def _scheduler_rec_finished(self):
        """ Scheduler action. """
        if self.cloudedbats_config.get('rpi_shutdown_when_finished', 'False') == 'True':
            self._logger.info('Scheduler: Raspberry Pi shutdown. Wait 60 sec. before shutdown.')
            # For development (time to finish software bugs before shutdown).
            os.system('sudo shutdown') # Broadcast and 60 sec.
            # os.system('sudo shutdown -h now')
        else:
            if self.cloudedbats_config.get('wifi_off_during_rec', 'False') == 'True':
                self._cloudedbats_mini.wifi_on()
            

    def _start(self):
        """ Start loop. """
        try:
            self._thread_active = True
            self._scheduler_thread = threading.Thread(target = self._scheduler_loop, args = [])
            self._scheduler_thread.start()
        except Exception as e:
            self._logger.error('Scheduler: Failed to start the scheduler. ' + unicode(e))

    def stop(self):
        """ """
        self._thread_active = False
    
    def _calculate_start_and_stop_time(self):
        """ """
        try:
            # Read from config file.
            start_event_str = self.cloudedbats_config.get('record_start_event', 'sunset')
            start_adjust_int = int(self.cloudedbats_config.get('record_start_adjust', 0))
            stop_event_str = self.cloudedbats_config.get('record_stop_event', 'sunrise')
            stop_adjust_int = int(self.cloudedbats_config.get('record_stop_adjust', 0))
            # Get time and position from GPS. 
            local_time = cloudedbats_core.GpsReader().get_time_local()
            latitude = cloudedbats_core.GpsReader().get_latitude()
            longitude = cloudedbats_core.GpsReader().get_longitude()
            #
            if self.cloudedbats_config.get('only_use_gps_time_and_pos', 'False') == 'True':
                # Dont't start scheduler before GPS.
                if (not local_time) or (not latitude) or (not longitude):
                    return None, None
            # Use default/local values if GPS not available.
            if not local_time:
                local_time = datetime.datetime.now()
            if (not latitude) or (not longitude):
                    latitude = float(self.cloudedbats_config.get('default_latitude', '0.0'))
                    longitude = float(self.cloudedbats_config.get('default_longitude', '0.0'))
            # Get Sunset, sunrise, etc.
            sunrise_dict = cloudedbats_core.SunsetSunrise().get_solartime_dict(latitude, 
                                                                               longitude, 
                                                                               local_time.date())
            # 
            self._logger.info('Scheduler: Sunset: ' + sunrise_dict.get('sunset', '-') + 
                              ' dusk: ' + sunrise_dict.get('dusk', '-') + 
                              ' dawn: ' + sunrise_dict.get('dawn', '-') + 
                              ' sunrise: ' + sunrise_dict.get('sunrise', '-'))
            # Convert event strings.
            start_time_str = start_event_str # If event is time.
            stop_time_str = stop_event_str # If event is time.
            #
            if start_event_str == 'sunset':
                start_time_str = sunrise_dict.get('sunset', '18:00')
            elif start_event_str == 'dusk':
                start_time_str = sunrise_dict.get('dusk', '18.20')
            elif start_event_str == 'dawn':
                start_time_str = sunrise_dict.get('dawn', '05:40')
            elif start_event_str == 'sunrise':
                start_time_str = sunrise_dict.get('sunrise', '06:00')
            # Convert event strings.
            if stop_event_str == 'sunset':
                stop_time_str = sunrise_dict.get('sunset', '18:00')
            elif stop_event_str == 'dusk':
                stop_time_str = sunrise_dict.get('dusk', '18.20')
            elif stop_event_str == 'dawn':
                stop_time_str = sunrise_dict.get('dawn', '05:40')
            elif stop_event_str == 'sunrise':
                stop_time_str = sunrise_dict.get('sunrise', '06:00')
            # Calculate start and stop time.
            start = datetime.datetime.strptime(start_time_str, '%H:%M')
            start += datetime.timedelta(minutes = start_adjust_int)
            start = start.time()
            stop = datetime.datetime.strptime(stop_time_str, '%H:%M')
            stop += datetime.timedelta(minutes = stop_adjust_int)
            stop = stop.time()
            #
            self._logger.info('Scheduler: Start event: ' + start_event_str + 
                              ' adjust: ' + unicode(start_adjust_int))
            self._logger.info('Scheduler: Stop event: ' + stop_event_str + 
                              ' adjust: ' + unicode(stop_adjust_int))
            self._logger.info('Scheduler: Calculated start time: ' + unicode(start) + 
                              ' stop time: ' + unicode(stop))
            #
            return start, stop
        except Exception as e:
            self._logger.error('Scheduler: Failed to calculate start and stop time. ' + unicode(e))
            return None, None

    def _scheduler_loop(self):
        """ Note: Running in thread. """
        time.sleep(10)
        #
        start_time, stop_time = self._calculate_start_and_stop_time()
        #
        if self.cloudedbats_config.get('only_use_gps_time_and_pos', 'False') == 'True':
            # Wait for GPS.
            while (start_time is None) or (stop_time is None):
                # Wait for GPS.
                time.sleep(60)
                start_time, stop_time = self._calculate_start_and_stop_time()
        #
        while self._thread_active:
            if self._scheduler_active:
                try:
                    self.cloudedbats_config
                    # Prefere GPS time.
                    gps_time = cloudedbats_core.GpsReader().get_time_local()
                    if gps_time:
                        time_now = gps_time.time()
                    else:
                        time_now = datetime.datetime.now().time()
                    # Start and stop the same day.
                    if start_time < stop_time:
                        if (time_now >= start_time) and (time_now <= stop_time):
                            self._scheduler_rec_active()
                        else: 
                            self._scheduler_rec_inactive()
                    else: # Stop the day after.
                        if (time_now >= stop_time) and (time_now <= start_time):
                            self._scheduler_rec_inactive()
                        else: 
                            self._scheduler_rec_active()    
                #
                except Exception as e:
                    self._logger.error('Scheduler: Exception: ' + unicode(e))
                    break # Terminate loop.
            #
            time.sleep(10) 

