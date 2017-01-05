#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2016 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

"""
This python script can be used to read a data stream from the "Pettersson M500 
USB Ultrasound Microphone", http://batsound.com, and pipe the stream to another 
tool.
The M500 microphone is developed for the Microsoft platform, but the python script 
pettersson_m500_batmic.py makes it possible to call it from Linux. 
(The Pettersson microphone "M500" is for Windows only, and "M500-384" is developed 
as a generic sound card and can be accessed from most systems, including Linux.)

This example shows how SoX can be used to read the stream and create short wave files 
when sound above 10 kHz are detected:
sudo python m500_stdout.py | sox -V -t raw -r 384k -e signed -c 1 -b 16 - output384_part_.wav sinc 10k silence 1 0.1 1% trim 0 5 : newfile : restart

Thanks to the author of this site for providing the SoX example: 
http://pibat.afraidofsunlight.co.uk/sound-activated-recording
"""

import sys
import pettersson_m500_batmic as m500

try:
    batmic = m500.PetterssonM500BatMic()
    batmic.start_stream()
    batmic.led_on()
    while True:
        data = batmic.read_stream()
        sys.stdout.write(data.tostring())
finally:
    batmic.stop_stream()
