# BackyardBats - Raspberry Pi for bat monitoring.

BackyardBats is a part of the software project CloudedBats. 

[CloudedBats] (http://cloudedbats.org) is about developing open and free software for bat monitoring. The name was chosen to remember me that I shall always try to put as much as possible of the data flow in the cloud. 

[BackyardBats] (http://backyardbats.org) is about using Raspberry Pi as an affordable and powerful unit for data capture. In this case, mainly wave files with bat sounds. The name was chosen because I think an interesting target group for this is people interested in both technical stuff and nature. When you have a perfect camera kit for bird photography, and a Raspberry Pi driven weather station in your backyard, then it's time to start to study bats. 

You just have to buy a good ultrasonic microphone and another Raspberry Pi. Everything else is standard peripherals for smart phones and computers. The recording unit can be connected to your wireless network to record bats in your garden, but don't forget to bring it with you when visiting other places and countries. In the future I hope you are a part in a network where we can share data and records. Bats are an important group of mammals that earlier was expensive and hard to study, but now it is much more easy, affordable and fun.

**Note: This code repository was earlier used for all Raspberry Pi related code. Now there is a new repository called cloudedbats_wurb for the new recording unit that should be and integrated part in the CloudedBats data flow. Therefore the need for this repository right now is not clear. It should be fun to set up the RPi as a hotspot and stream live data via Flask and Bokeh after some DSP, but at the moment there is no time for that...** 


## Planned development

During the bat season 2016 I focused on the recording unit. The first version contained a web server (Django) for configuration and control. This was not practical when recording in the field and I decided to replace it with the *cloudedbats_mini* version. During 2017 focus will be on the web application, and the recording unit that integrates with the web application will be called *cloudedbats_wurb*.  
## Software alternatives

#### - cloudedbats_micro

This is the best starting point if you want to test if it is possible to record sound on a Raspberry Pi. Contains some test files for the Pettersson M500-384 microphone. The code can easily be modified for other types of microphones and they don't have to be ultrasonic. During early development I used Griffin iMic and Samson Go Mic.  
There is also some experimental code for the M500 microphone. M500 is for the Microsoft platform, but it is possible to connect to it from a Linux system by using communication at a lower level. 
More information is available in each python file.

#### - cloudedbats_mini

This is the version I use myself at the moment. It is controlled by a settings file and two three-way switches. It has support for GPS and contains a scheduler that knows when sunset/sunrise/dawn/dusk occurs. Contains no web server, but can be accessed via SSH or FileZilla. 

Supports full speed recordings only, which means that you need about 30 GB for one full night. Post processing to remove empty parts will be developed in 2017. 

There is no updated installation guide available yet, but the old one is partly valid: [Wiki: Raspberry Pi installation] (https://github.com/cloudedbats/backyardbats/wiki/Raspberry-Pi-installation)
Please contact me if that's a problem.

#### - cloudedbats_wurb

The new version will be developed during the bat season 2017. Source code is available here: https://github.com/cloudedbats/cloudedbats_wurb 

## Contact

info@cloudedbats.org
