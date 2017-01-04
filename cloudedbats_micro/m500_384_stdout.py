#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2016 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

"""
This python script can be used to read a data stream from the "Pettersson M500-384 
USB Ultrasound Microphone", http://batsound.com, and pipe the stream to another 
tool. By changing device name, channels, rate, etc. the script can be used for 
other types of sound cards.  
(The Pettersson microphone "M500" is for Windows only, and "M500-384" is developed 
as a generic sound card and can be accessed from most systems, including Linux.)

This example shows how SoX can be used to read the stream and create short wave files 
when sound above 10 kHz are detected:
sudo python m500_384_stdout.py | sox -V -t raw -r 384k -e signed -c 1 -b 16 - output384_part_.wav sinc 10k silence 1 0.1 1% trim 0 5 : newfile : restart

Thanks to the author of this site for providing the SoX example: 
http://pibat.afraidofsunlight.co.uk/sound-activated-recording
"""

import sys
import pyaudio

py_audio = pyaudio.PyAudio()
# Search for the M500-384 device.
part_of_device_name = 'Pettersson M500-384kHz USB'
device_index = None
device_count = py_audio.get_device_count()
for index in range(device_count):
    info_dict = py_audio.get_device_info_by_index(index)
    if part_of_device_name in info_dict['name']:
        device_index = index
        break
# Continue if device was found.
if device_index:
    buffer_size = 0x10000 # Size: 65536.
    pyaudio_stream = None
    try:
        pyaudio_stream = py_audio.open(
            format = py_audio.get_format_from_width(2), # 16 bits.
            channels = 1, # Mono.
            rate = 384000, # Sample rate.
            frames_per_buffer = buffer_size,
            input = True, # Sound in.
            output = False, # Don't use sound out.
            input_device_index = device_index,
            start = True, # Start stream directly.
        )
        # Read stream and write to standard output.
        while True:
            data = pyaudio_stream.read(buffer_size, exception_on_overflow = False)
            sys.stdout.write(data)
    #
    finally:
        if pyaudio_stream:
            pyaudio_stream.stop_stream()
            pyaudio_stream.close()
else:
    print('The device "Pettersson M500-384kHz USB" can not be detected. Stream not started. ')

