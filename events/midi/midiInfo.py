# -*- coding: utf-8 -*-
"""
Created on Fri Jul 01 16:10:08 2011

@author: guilbut
"""

from pygame import pypm


countDevices = pypm.CountDevices()  # nombre d'entree + sorties MIDI
# GetDefaultInputDeviceID() 	# The default device can be specified using a small application named pmdefaults that is part of the PortMidi distribution.
# GetDefaultOutputDeviceID()


# (interf,name,input,output,opened) = pypm.GetDeviceInfo(numDevice) 	# 	MMSystem,nom,1/0,1/0,1/0
# interf		underlying MIDI API, e.g. MMSystem or DirectX
# name 		device name, e.g. USB MidiSport 1x1
# input		true if input is available
# output		true if output is available
# opened 	used by generic PortMidi code to do error checking on arguments


for deviceNum in range(countDevices):
    print("Device " + str(deviceNum) + " : " + str(pypm.GetDeviceInfo(deviceNum)))
