# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 11:55:20 2012

@author: guilbut
"""


HSTART = int("0x23", 0)
HSIZE = int("0xA0", 0)
VSTRT = int("0x07", 0)
VSIZE = int("0xF0", 0)
HREF = int("0x8B", 0)


def Horizontal_Frame_Start(HSTART, HREF):
    return HSTART << 2 | ((HREF >> 4) & 3)  # =>	140 (VGA) 	252 (QVGA)


def Horizontal_Sensor_Size(HSIZE, HREF):
    return HSIZE << 2 | ((HREF & 3))  # =>	640 (VGA)	320 (QVGA)


def Vertical_Frame_Start(VSTRT, HREF):
    return VSTRT << 1 | ((HREF >> 6) & 1)  # =>	14 (VGA)	6 (QVGA)


def Vertical_Sensor_Size(VSIZE, HREF):
    return VSIZE << 1 | ((HREF >> 2) & 1)  # =>	480(VGA)	240 (QVGA)


def HStart(Horizontal_Frame_Start):
    return Horizontal_Frame_Start >> 2


def HSize(Horizontal_Sensor_Size):
    return Horizontal_Sensor_Size >> 2


def VStrt(Vertical_Frame_Start):
    return Vertical_Frame_Start >> 1


def VSize(Vertical_Sensor_Size):
    return Vertical_Sensor_Size >> 1


def HRef(
    Horizontal_Frame_Start,
    Horizontal_Sensor_Size,
    Vertical_Frame_start,
    Vertical_Sensor_Size,
):
    return (
        (HREF & 0x88)
        | ((Horizontal_Frame_Start & 3) << 4)
        | (Horizontal_Sensor_Size & 3)
        | ((Vertical_Frame_start & 1) << 6)
        | ((Vertical_Sensor_Size & 1) << 2)
    )


print("Horizontal_Frame_Start = %i" % Horizontal_Frame_Start(HSTART, HREF))
print("Horizontal_Sensor_Size = %i" % Horizontal_Sensor_Size(HSIZE, HREF))
print("Vertical_Frame_start   = %i" % Vertical_Frame_Start(VSTRT, HREF))
print("Vertical_Sensor_Size   = %i" % Vertical_Sensor_Size(VSIZE, HREF))


print("HSTRAT = %X" % HStart(Horizontal_Frame_Start(HSTART, HREF)))
print("HSIZE = %X" % HSize(Horizontal_Sensor_Size(HSIZE, HREF)))
print("VSTRT   = %X" % VStrt(Vertical_Frame_Start(VSTRT, HREF)))
print("HSIZE = %X" % VSize(Vertical_Sensor_Size(VSIZE, HREF)))
print(
    "HREF   = %X"
    % HRef(
        Horizontal_Frame_Start(HSTART, HREF),
        Horizontal_Sensor_Size(HSIZE, HREF),
        Vertical_Frame_Start(VSTRT, HREF),
        Vertical_Sensor_Size(VSIZE, HREF),
    )
)
