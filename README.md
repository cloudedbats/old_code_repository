# BackyardBats - Raspberry Pi for bat monitoring.

BackyardBats is a part of the software project CloudedBats. 

[CloudedBats] (http://cloudedbats.org) is about developing open and free software for bat monitoring. The name was chosen to remember me that I shall always try to put as much as possible of the data flow in the cloud. 

[BackyardBats] (http://backyardbats.org) is about using Raspberry Pi as an affordable and powerful unit for data capture. In this case it is mainly wave files with bat sounds. The name was chosen because I think an interesting target group for this is people interesting in both technical stuff and nature. When you have a perfect camera kit for bird photography, and a Raspberry Pi driven weather station, then it's time to start to study bats. 

You just have to buy a good ultrasonic microphone and another Raspberry Pi. Everything else is standard peripherals for smart phones and computers. The ultrasonic microphone is a little bit expensive compared to other parts in the set up, but below the price of a medium quality camera lens. 

The recording unit can be connected to your wireless network to record bats in your garden, but don't forget to bring it with you when visiting other places and countries. In the future I hope you are a part in a network where we can share data and records. Bats are an important group of mammals that earlier was hard to study, and this kind of collected recordings can be a good start for more advanced surveys in the future.   

## Planned development ##

During the bat season 2016 I focused on the recording unit. The first version contained a web server (Django) and was configured and controlled from a computer or smart phone. This was not practical when recording in the field and I decided to replace it with the cloudedbats_mini version. During 2017 focus will be on the cloud part and the recording unit that integrates with the cloud will be called cloudedbats_wurb.  

## Software alternatives ##

#### cloudedbats_micro ####

This is the best starting point if you want to test if it is possible to record sound on a Raspberry Pi. Contains a test file for the Pettersson M500-384 microphone. The code can easily be modified for other types of microphones. There is also some experimental code for the M500 microphone. M500 is for the Microsoft platform, but it is possible to connect to it from a Linux system by using communication at a lower level.

More information is available in each python file.

#### cloudedbats_mini ####

This is the version I use myself at the moment. It is controlled by a settings file and two three-way switches. It has support for GPS and contains a scheduler that knows when sunset/sunrise/dawn/dusk occurs. Contains no web server, but can be accessed via SSH or FileZilla. 

Supports full speed recordings only which means that you need about 30 GB for one full night. Post processing to remove empty parts will be developed later. 

#### cloudedbats_wurb ####

Will be developed during the bat season 2017.

#### old_rpi_versions ####

Old versions will be stored here since they may contain useful code to copy-and-paste from.

## TODO-list ##

On my TODO-list for the 2016 versions are:

- Installation instructions for cloudedbats_mini. 
The old installation is partly valid: [Wiki: Raspberry Pi installation] (https://github.com/cloudedbats/backyardbats/wiki/Raspberry-Pi-installation)

## Contact

info@cloudedbats.org
