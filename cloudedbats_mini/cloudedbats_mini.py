#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2016 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import os
import time
import logging.handlers
import cloudedbats_core
import cloudedbats_raspberry

class CloudedBatsMini(object):
    """ """
    def __init__(self):
        """ """
        # Set up logging.
        self._logger = logging.getLogger('CloudedBats')
        self._logging_setup()
        #
        self._logger.info('')
        self._logger.info('Welcome to CloudedBats-mini')
        self._logger.info('=========== ^ö^ ===========')
        self._logger.info('')
        # Load config file.
        self.cloudedbats_config = {}
        self._load_config()
        #
        self._sound_recorder = None
        self._scheduler = None
        self._current_state = None # Valid: rec_on, rec_auto, rec_off.
    
    def start_cloudedbats_mini(self):
        """ """
        self._gpio_control = None
        self._mouse_control = None
        #
        try:
            # Wait for sound cards, etc.
            time.sleep(5)
            # Check available sound cards/sources.
            self._logger.info('Mini: Available input sound cards/sources are:')
            sound_device_list = cloudedbats_core.AudioSource().get_device_list()
            for sound_device in sound_device_list:
                self._logger.info('- ' + sound_device)        
            # Activate GPS. Set timezone.
            self._logger.info('Mini: Initiate GPS.')
            cloudedbats_core.GpsReader().start_gps()
            timezone = self.cloudedbats_config.get('timezone', 'UTC')
            cloudedbats_core.GpsReader().set_timezone(timezone)
            # Timezone for sunset, sunrise.
            cloudedbats_core.SunsetSunrise().set_timezone(timezone)
            # Initiate scheduler.
            if self.cloudedbats_config.get('use_scheduler', 'False') == 'True':
                self._logger.info('Mini: Initiate scheduler (used for auto mode).')
                self._scheduler = cloudedbats_core.WurbScheduler(cloudedbats_mini_object = self)
                self.auto_on()
                time.sleep(1)
            # Initiate Raspberry Pi GPIO for control. 
            if self.cloudedbats_config.get('use_raspberry_pi_gpio', 'False') == 'True':
                self._logger.info('Mini: Initiate control via Raspberry Pi GPIO.')
                self._gpio_control = cloudedbats_raspberry.GpioForControl(cloudedbats_mini_object = self)
            # Initiate mouse for control.
            if self.cloudedbats_config.get('use_mouse_for_remote_control', 'False') == 'True':
                self._logger.info('Mini: Initiate control via computer mouse.')
                self._mouse_control = cloudedbats_raspberry.MouseForRemoteControl(cloudedbats_mini_object = self)
            # Check available disk space for wave files.
            time.sleep(15)
            wave_file_dir_path = self.cloudedbats_config.get('wave_file_dir_path', '/')
            old_free_disk = 0
                        
            while True:
                if not os.path.exists(wave_file_dir_path):
                    # No records done yet.
                    time.sleep(60)
                    continue
                #    
                file_system_stat = os.statvfs(wave_file_dir_path)
                free_disk = file_system_stat.f_bavail * file_system_stat.f_frsize / 1024 / 1024 # MB.
                total_disk = file_system_stat.f_blocks * file_system_stat.f_frsize / 1024 / 1024 # MB.
                # Log disk space each minute if changed from last check. 
                if old_free_disk != free_disk:
                    self._logger.info('Mini: Total disk space: ' + unicode(total_disk) + ' MB. '
                                      'Free space: ' +  unicode(free_disk) + ' MB. '
                                      'Path: ' +  wave_file_dir_path
                                      )
                old_free_disk = free_disk
                # Check disk space.
                if free_disk < 10: # < 10 MB.
                    self._logger.error('Mini: Not enough disk space available. Path: ' + wave_file_dir_path)
                    self.rec_off()
                    # Shutdown when disk is full or not avaliable. Only valid in rec and
                    # auto mode. Automatically shutdown should be stated in config file. 
                    if self._current_state and (self._current_state in ['rec_on', 'auto_on']):
                        if self.cloudedbats_config.get('rpi_shutdown_when_no_space', 'False') == 'True':
                            self._logger.info('Mini: Raspberry Pi shutdown. Wait 60 sec. before shutdown.')
                            #
                            self.stop_cloudedbats_mini() 
                            os.system('sudo shutdown')
#                             os.system('sudo shutdown -h now')
                # Wait.
                time.sleep(60)
        #
        except Exception as e:
            self.rec_off()
            self._logger.error('Mini: Failed to start CloudeBats_mini. Exception: ' + unicode(e))
            self._logger.error('Mini: CloudeBats_mini terminated.')
            self.stop_cloudedbats_mini()
            #
    
    def stop_cloudedbats_mini(self):
        """ """
        if self._gpio_control:
            self._gpio_control.stop()
        if self._mouse_control:
            self._mouse_control.stop()
        cloudedbats_core.SoundRecorder().stop()
        cloudedbats_core.AudioTarget().close()
        cloudedbats_core.GpsReader().stop_gps()
        if self._scheduler:
            self._scheduler.stop()
        
    def rec_on(self):
        """ """
        self._current_state = 'rec_on'
        self._logger.info('Mini: Start recording.')
        self.auto_off()
        self.start_recording()
    
    def rec_off(self):
        """ """
        self._current_state = 'rec_off'
        self._logger.info('Mini: Stop recording.')
        self.auto_off()
        self.stop_recording()
    
    def auto_on(self):
        """ """
        self._current_state = 'auto_on'
        self._logger.info('Mini: Activate auto.')
        self.stop_recording()
        if self._scheduler:
            self._scheduler.activate()
    
    def auto_off(self):
        """ """
        self._logger.info('Mini: Deactivate auto.')
#         self.stop_recording()
        if self._scheduler:
            self._scheduler.deactivate()
    
    def start_recording(self):
        """ Start recording. """
        if not self._sound_recorder:
            # Activate once only.
            try:
                settings_dict = self.cloudedbats_config
                #
                channels = 1 # 1 = Mono.
                if settings_dict['channels'] == 'STEREO': channels = 2 # 2 = Stereo.
                #
                sampling_rate = 44100
                recording_type = settings_dict['recording_type'] 
                if recording_type in ['TE192', 'FS192']: sampling_rate = 192000 # Hz.
                elif recording_type in ['TE250', 'FS250']: sampling_rate = 250000 # Hz.
                elif recording_type in ['TE300', 'FS300']: sampling_rate = 300000 # Hz.
                elif recording_type in ['TE384', 'FS384']: sampling_rate = 384000 # Hz.
                elif recording_type in ['TE500', 'FS500']: sampling_rate = 500000 # Hz.
                #
                # Use TE, time expansion, for high rates.
                sampling_rate_out = sampling_rate
                if recording_type in ['TE192', 'TE250', 'TE300', 'TE384', 'TE500']:
                    sampling_rate_out = sampling_rate / 10
                #
                latitude_longitude = 'No-position'
                try:
                    latitude = float(settings_dict.get('default_latitude', '0.0'))
                    longitude = float(settings_dict.get('default_longitude', '0.0'))
                    if latitude and longitude:
                        if latitude >= 0: lat_prefix = 'N'
                        else: lat_prefix = 'S'
                        if longitude >= 0: long_prefix = 'E'
                        else: long_prefix = 'W'
                        #
                        latitude_longitude = lat_prefix + unicode(abs(latitude)) + long_prefix + unicode(abs(longitude))
                except:
                    pass
                #
                target = cloudedbats_core.AudioTarget(
                            sampling_rate_hz = sampling_rate_out, 
                            adc_resolution_bits = int(settings_dict['adc_resolution']), 
                            channels = channels, 
                            dir_path = settings_dict['wave_file_dir_path'], 
                            filename_prefix = settings_dict['wave_file_prefix'], 
                            filename_lat_long = latitude_longitude,
                            filename_rec_type = recording_type,
                            each_record_length_s = int(settings_dict['record_length_s']),
                            timezone = settings_dict['timezone'],
                            )
                #
                self._sound_recorder = cloudedbats_core.SoundRecorder()
                self._sound_recorder.setup(
                            in_sampling_rate_hz = sampling_rate, 
                            in_adc_resolution_bits = int(settings_dict['adc_resolution']), 
                            in_channels = channels, 
                            in_device_name = settings_dict['sound_card_name'], 
                            audio_target = target
                            )
            except Exception as e:
                self._logger.info('Mini: Failed to setup sound recorder: ' + unicode(e))
                return
        # Start rec.
        try:
            if self._sound_recorder.is_running():
                self._sound_recorder.stop()
                time.sleep(1)
            self._sound_recorder.start()    
        except Exception as e:
            self._logger.info('Mini: Failed to start sound recorder: ' + unicode(e))
    
    def stop_recording(self):
        """ Stop recording. """
        if self._sound_recorder:
            if self._sound_recorder.is_running():
                self._sound_recorder.stop()
    
    def wifi_off(self):
        """ """
        self._logger.info('Mini: WiFi off.')
        try:
            os.system('sudo ifconfig wlan0 down')
        except:
            self._logger.error('Mini: WiFi off failed.')
    
    def wifi_on(self):
        """ """
        self._logger.info('Mini: WiFi on.')
        try:
            os.system('sudo ifconfig wlan0 up')
        except:
            self._logger.error('Mini: WiFi on failed.')
    
    def _logging_setup(self):
        """ """
        log = logging.getLogger('CloudedBats')
        log.setLevel(logging.INFO)
        # Define rotation log files.
        log_file_name = 'cloudedbats_log.txt'
        dir_path = os.path.dirname(os.path.abspath(__file__))
        log_handler = logging.handlers.RotatingFileHandler(os.path.join(dir_path, log_file_name),
                                                           maxBytes = 128*1024,
                                                           backupCount = 10)
        log_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-10s : %(message)s '))
        log_handler.setLevel(logging.DEBUG)
        log.addHandler(log_handler)
    
    def _load_config(self):
        """ """
        config_file_name = 'cloudedbats_config.txt'
        self._logger.info('Mini: Loading configuration file: ' + config_file_name)
        dir_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(dir_path, config_file_name), 'r') as infile:
            for row in infile:
                key_value = row.strip()
                key = ''
                value = ''
                # Remove comments.
                if '#' in key_value:
                    key_value = key_value.split('#')[0].strip() # Use left part.
                # Split key/value.
                if key_value:
                    if ':' in key_value:
                        key_value_list = key_value.split(':', 1) # Split on first occurrence.
                        key = key_value_list[0].strip()
                        value = key_value_list[1].strip()
                        if key and value:
                            self.cloudedbats_config[key] = value
        # 
        self._logger.info('Mini: Configuration file loaded. Values: ' + unicode(self.cloudedbats_config))


### Main. ###
if __name__ == "__main__":
    """ """
    cloudedbatsmini = CloudedBatsMini()
    cloudedbatsmini.start_cloudedbats_mini()
    
    