#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2016-2017 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import wave
import pyaudio

class Test():
    """ """
    def __init__(self):
        """ """
        in_device_name = 'Pettersson'
        in_device_index = 2
        if in_device_name:
            self._in_device_index = self.get_device_index(in_device_name)
        else:    
            self._in_device_index = in_device_index
        #
        self._active = False
        
    def start(self):
        """ """
        # Open wave file for writing.
        self._wave_file = wave.open('m500_384_test.wav', 'wb')
        self._wave_file.setnchannels(1)
        self._wave_file.setsampwidth(2)
        self._wave_file.setframerate(38400)
        
        buffer_size = 1024 * 64 # 2**16
        self._pyaudio = pyaudio.PyAudio()
        #
        self._stream = self._pyaudio.open(
            format = self._pyaudio.get_format_from_width(2),
            channels = 1,
            rate = 384000,
            frames_per_buffer = buffer_size,
            input = True,
            output = False,
            input_device_index = self._in_device_index,
            start = True,
        )
#         #
#         self._active = True
#         data_list = []
#         data = self._stream.read(buffer_size)
#         while self._active and data:
#             
#             data_list.append(data)
# #             self._wave_file.writeframes(data)
#             data = self._stream.read(buffer_size)
#             
#             if len(data_list) > 50:
#                 self._active = False
#         #
#         
#         concat_data = b''.join(data_list)
#         
#         self._wave_file.writeframes(concat_data)
        
        #
        self._active = True
        data = self._stream.read(buffer_size)
        counter = 0
        while self._active and data:
            self._wave_file.writeframes(data)
            data = self._stream.read(buffer_size)
            #
            counter += 1
            if counter > 50:
                self._active = False
        #
        self._stream.stop_stream()
        self._stream.close()
        self._wave_file.close()
        
    def get_device_index(self, part_of_device_name):
        """ """
        py_audio = pyaudio.PyAudio()
        device_count = py_audio.get_device_count()
        for index in range(device_count):
            info_dict = py_audio.get_device_info_by_index(index)
            if part_of_device_name in info_dict['name']:
                return index
        #
        return None
    


# === MAIN ===    
if __name__ == "__main__":
    """ """
    test = Test()
    test.start()

