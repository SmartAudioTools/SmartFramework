import pypm
import array
import time


# IN -----------
# filtre les entrée MIDI.  By default, only active sensing messages are filtered. (FILT_NOTE
# lit le buffer d'entrée -> [ [[status, data1,data2,data3],date]  [[status,data1,data2,data3],date] ]
print("Date : ", MidiData[0][1])
print(
    "Donnés : ",
    MidiData[0][0][0],
    " ",
    MidiData[0][0][1],
    " ",
    MidiData[0][0][2],
    MidiData[0][0][3],
)  # Rem : 4 bytes pour les  SysEx
del MidiIn

# OUT --------
MidiOut = pypm.Output(num_device, latence)  # Latence en millisecondes
# si la latence est de <= 0 , le timestamps (date de sortie) est ignoré et les outputs sortent immédiatement
# si la lentece est > 0 , le message sortira quand time_proc() >  timestamps (date de sortie)+ latence (calculé pour coller à la latence des buffeurs audios)
MidiOut.WriteShort(
    0x90, 60, 0
)  # Envoit la donnée 0xCodeHexa  immediatement ( avec une latence definie par pypm.Output())  . (Rem : les Datas 1 et 2 sont facultatives)
Date = pypm.Time()  # returns the current time in ms of the PortMidi timer
MidiOut.Write(
    [[[0xC0, 0, 0], Date], ...]
)  # envoit un liste de message MIDI (max 1024) avec des dates de sortie (Rem : les Datas 1 et 2 sont facultatives)
# si la lentece definie par pypm.Input() est > 0 , le message sortira quand time_proc() >  timestamps (date de sortie)+ latence (calculé pour coller à la latence des buffeurs audios)
MidiOut.WriteSysEx(0, "\xF0\x7D\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A\xF7")
MidiOut.WriteSysEx(pypm.Time(), [0xF0, 0x7D, 0x10, 0x11, 0x12, 0x13, 0xF7])
del MidiOut

# Errors -------
GetErrorText(err)  # returns human-readable error messages translated from error numbers
