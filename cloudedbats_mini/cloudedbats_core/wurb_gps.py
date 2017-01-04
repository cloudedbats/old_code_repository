#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2016 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import gps
import pytz
import time
import dateutil.parser
import threading
import logging
import cloudedbats_core

@cloudedbats_core.singleton
class GpsReader(object):
    """ Singleton class for GPS time and position. 
        Usage:
            GpsReader().start_gps() # Activates the class.
            time = GpsReader().get_time_utc() 
            latitude = GpsReader().get_latitude() 
            longitude = GpsReader().get_longitude() 
            latlong = GpsReader().get_latlong_string() 
            GpsReader().gps_stop()
    """
    def __init__(self):
        """ """
        self._logger = logging.getLogger('CloudedBats')
        # Use clear to initiate class members.
        self._clear()
        # Default port for GPSD.
        self._gpsd_port = 2947
        # Default timezone.
        self._timezone = pytz.timezone('UTC')
        # 
        self._debug = False

    def start_gps(self):
        """ """
        # Start reading GPS stream.
        self._gps_start()

    def stop_gps(self):
        """ """
        self._active = False

    def get_time_utc(self):
        """ """
        if self.gps_time == None:
            return None
        #
        return dateutil.parser.parse(self.gps_time)

    def get_time_utc_string(self):
        """ """
        if self.gps_time == None:
            return None
        #
        return self.gps_time

    def set_timezone(self, timezone = 'UTC'):
        """ """
        self._timezone = pytz.timezone(timezone)

    def get_time_local(self):
        """ """
        if self.gps_time == None:
            return None
        #
        return dateutil.parser.parse(self.gps_time).astimezone(self._timezone)

    def get_time_local_string(self):
        """ """
        if self.gps_time == None:
            return None
        #
        datetime_utc = dateutil.parser.parse(self.gps_time)
        datetimestring = unicode(datetime_utc.astimezone(self._timezone).strftime("%Y%m%dT%H%M%S%z"))
        return datetimestring

    def get_latitude(self):
        """ """
        return self.gps_latitude
        
    def get_longitude(self):
        """ """
        return self.gps_longitude
        
    def get_latlong_string(self):
        """ """
        if self.gps_latitude and self.gps_longitude:
            if self.gps_latitude >= 0: lat_prefix = 'N'
            else: lat_prefix = 'S'
            if self.gps_longitude >= 0: long_prefix = 'E'
            else: long_prefix = 'W'
            #    
            latlong_string = lat_prefix + format(abs(self.gps_latitude), '.4f') + \
                             long_prefix + format(abs(self.gps_longitude), '.4f')
            #
            return latlong_string
        else:
            return None
        
    def _clear(self):
        """ """
        self._gps = None
        self._active = False
        #
        self.gps_time = None
        self.gps_latitude = None
        self.gps_longitude = None

    def _gps_start(self):
        """ """
        try:
            # GPSD on port 2947.
            self._gps = gps.gps("localhost", self._gpsd_port)
            self._gps.stream(gps.WATCH_ENABLE)
            # Loop.
            self._active = True
            self._gps_thread = threading.Thread(target = self._gps_loop, args = [])
            self._gps_thread.start()
        except Exception as e:
            self._logger.error('GPS reader: Failed to connect to GPSD. ' + unicode(e))

    def _gps_loop(self):
        """ Note: Running in thread. """
        try:
            while self._gps and self._active:
                try:
                    gps_data = self._gps.next()
                    if gps_data['class'] == 'TPV':
                        self.gps_time = getattr(gps_data, 'time', None)
                        self.gps_latitude = getattr(gps_data, 'lat', None)
                        self.gps_longitude = getattr(gps_data, 'lon', None)
                        #
                        # Example from class=TPV:
                        # u'epx': 12.529, 
                        # u'epy': 47.937, 
                        # u'track': 217.0802, 
                        # u'ept': 0.005, 
                        # u'lon': 12.638941473, 
                        # u'eps': 95.87, 
                        # u'lat': 57.662048996, 
                        # u'tag': u'MID2', 
                        # u'mode': 2, 
                        # u'time': u'2016-08-02T21:50:06.000Z', 
                        # u'device': u'/dev/ttyUSB0', 
                        # u'speed': 0.045, 
                        # u'class': u'TPV'
                        if self._debug:
                            if self.gps_time: print(unicode(self.gps_time))
                            if self.gps_latitude: print(unicode(self.gps_latitude)) 
                            if self.gps_longitude: print(unicode(self.gps_longitude))
                #
                except StopIteration: # Raised in gps.next()
                    self._gps = None
                    self._clear()
        #
        finally:
            if self._gps:
                self._gps.stream(gps.WATCH_DISABLE)
                self._gps.close()
                self._clear()



### Test. ###
if __name__ == "__main__":
    """ """
    gps_reader = GpsReader()
    gps_reader.start_gps()
    gps_reader._debug = True
    #
    time.sleep(5)
    print('')
    print('TIME: ' + unicode(gps_reader.get_time_utc()))
    print('LATLONG-STRING: ' + unicode(gps_reader.get_latlong_string()))
    print('')
    time.sleep(5)
    #
    gps_reader.stop_gps()
