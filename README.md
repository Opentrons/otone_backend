# Backend Python Component of the OpenTrons OT.One

This is the minimum viable product backend component of the OpenTrons OT.One. It runs the business logic on python3 and Crossbar.io (python2).

# The OT.One Components

The three components of the OpenTrons OT.One software are:
* [Frontend](http://github.com/OpenTrons/otone_frontend) (/home/pi/otone_frontend)
* [Backend](http://github.com/OpenTrons/otone_backend) (/home/pi/otone_backend)
* [Scripts](http://github.com/OpenTrons/otone_scripts) (/home/pi/otone_scripts)

Additionally, [SmoothiewareOT](https://github.com/Opentrons/SmoothiewareOT) is OpenTrons' version of the Smoothieware firmware running on the Smoothieboard microcontroller board.

All three components run together and are started with the script *start.sh* in otone_scripts. The *start.sh* script is called on startup.

