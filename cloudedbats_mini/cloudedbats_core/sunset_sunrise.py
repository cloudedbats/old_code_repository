#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2016 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

from datetime import date
import pytz
import logging
import cloudedbats_core

@cloudedbats_core.singleton
class SunsetSunrise(object):
    """ Singleton class. Usage, see test example below. """
    def __init__(self):
        """ """        
        self._logger = logging.getLogger('CloudedBats')
        # Default timezone.
        self._timezone = pytz.timezone('UTC')
        #
        self._solartime_cache = {} # Key: (lat,long, date), value: solartime_dict

    def set_timezone(self, timezone = 'UTC'):
        """ """
        self._timezone = pytz.timezone(timezone)

    def get_solartime_dict(self, latitude = 0.0, 
                                 longitude = 0.0, 
                                 selected_date = None):
        """ """
        try:
            if not selected_date:
                selected_date = date.today()
            if (latitude, longitude, selected_date) not in self._solartime_cache:
                self._add_to_solartime_cache(latitude, longitude, selected_date)
            #
            return self._solartime_cache.get((latitude, longitude, selected_date), {})
        #
        except Exception as e:
            self._logger('Sunset: Failed to calculate sunset/sunrise: ' + unicode(e))
        #
        return {}

    def _add_to_solartime_cache(self, latitude, longitude, selected_date):
        """ """
        sun = cloudedbats_core.solartime.SolarTime()
        schedule = sun.sun_utc(selected_date, float(latitude), float(longitude))
        #
        solartime_dict = {}
        solartime_dict['date'] = unicode(selected_date)
        solartime_dict['latitude'] = unicode(latitude)
        solartime_dict['longitude'] = unicode(longitude)
        solartime_dict['dawn'] = unicode(schedule['dawn'].astimezone(self._timezone).time().strftime("%H:%M"))
        solartime_dict['sunrise'] = unicode(schedule['sunrise'].astimezone(self._timezone).time().strftime("%H:%M"))
        solartime_dict['sunset'] = unicode(schedule['sunset'].astimezone(self._timezone).time().strftime("%H:%M"))
        solartime_dict['dusk'] = unicode(schedule['dusk'].astimezone(self._timezone).time().strftime("%H:%M"))
        #
        self._solartime_cache[(latitude, longitude, selected_date)] = solartime_dict


### Test. ###
if __name__ == "__main__":
    """ """
    solartime_dict = SunsetSunrise().get_solartime_dict(56.78, 12.34, date.today())
    print('SunsetSunrise dictionary: ' + unicode(solartime_dict))
    print('SunsetSunrise date:       ' + unicode(solartime_dict['date']))
    print('SunsetSunrise latitude:   ' + unicode(solartime_dict['latitude']))
    print('SunsetSunrise longitude:  ' + unicode(solartime_dict['longitude']))
    print('SunsetSunrise dawn:       ' + unicode(solartime_dict['dawn']))
    print('SunsetSunrise sunrise:    ' + unicode(solartime_dict['sunrise']))
    print('SunsetSunrise sunset:     ' + unicode(solartime_dict['sunset']))
    print('SunsetSunrise dusk:       ' + unicode(solartime_dict['dusk']))

