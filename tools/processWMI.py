# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 18:15:22 2018

@author: Baptiste
"""

import wmi

c = wmi.WMI()

for process in c.Win32_Process():
    print(process.ProcessId, process.Description)
