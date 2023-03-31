"""
PyAudio Example:

Query and print(PortAudio HostAPIs, Devices, and their)
support rates.
"""

import pyaudio
import os

# from SmartFramework.serialize.serializejson import dumps


standard_sample_rates = [
    8000.0,
    9600.0,
    11025.0,
    12000.0,
    16000.0,
    22050.0,
    24000.0,
    32000.0,
    44100.0,
    48000.0,
    88200.0,
    96000.0,
    192000.0,
]

p = pyaudio.PyAudio()
print("----------------------")
max_devs = p.get_device_count()
bitperfectDevices = {}
for i in range(max_devs):
    # print(i)
    devinfo = p.get_device_info_by_index(i)
    # print(dumps(devinfo))
    # print(devinfo["name"],devinfo["hostApi"])
    # filtre devices asio
    if os.name == "nt":
        if devinfo["hostApi"] != 2:
            continue
    elif os.name == "posix":
        if devinfo["hostApi"] != 0:
            continue

    bitperfectDevices[devinfo["name"]] = i
p.terminate()


def printAllInfos():

    p = pyaudio.PyAudio()
    print("----------------------")
    max_devs = p.get_device_count()

    print("Number of Devices  : %d" % max_devs)

    try:
        def_index = p.get_default_input_device_info()["index"]
        print("Default Input Device :", def_index)
    except IOError as e:
        print("No Default Input devices")

    try:
        def_index = p.get_default_output_device_info()["index"]
        print("Default Output Device:", def_index)
    except IOError as e:
        print("No Default Output devices")

    print("\nDevices: ===================")

    for i in range(max_devs):
        print(i)

        devinfo = p.get_device_info_by_index(i)

        # filtre devices asio
        # if devinfo["hostApi"] != 2:
        #    continue

        # print(out device parameters)
        for k in devinfo.items():
            name, value = k

            # if host API, then get friendly name

            if name == "hostApi":
                value = (
                    str(value) + " (%s)" % p.get_host_api_info_by_index(k[1])["name"]
                )
            print("%s: %s" % (name, value))

        # print(out supported format rates)

        input_supported_rates = []
        output_supported_rates = []
        full_duplex_rates = []

        for f in standard_sample_rates:

            if devinfo["maxInputChannels"] > 0:
                try:
                    if p.is_format_supported(
                        f,
                        input_device=devinfo["index"],
                        input_channels=devinfo["maxInputChannels"],
                        input_format=pyaudio.paInt16,
                    ):
                        input_supported_rates.append(f)
                except ValueError:
                    pass

            if devinfo["maxOutputChannels"] > 0:
                try:
                    if p.is_format_supported(
                        f,
                        output_device=devinfo["index"],
                        output_channels=devinfo["maxOutputChannels"],
                        output_format=pyaudio.paInt16,
                    ):
                        output_supported_rates.append(f)
                except ValueError:
                    pass

            if (devinfo["maxInputChannels"] > 0) and (devinfo["maxOutputChannels"] > 0):
                try:
                    if p.is_format_supported(
                        f,
                        input_device=devinfo["index"],
                        input_channels=devinfo["maxInputChannels"],
                        input_format=pyaudio.paInt16,
                        output_device=devinfo["index"],
                        output_channels=devinfo["maxOutputChannels"],
                        output_format=pyaudio.paInt16,
                    ):
                        full_duplex_rates.append(f)
                except ValueError:
                    pass

        if len(input_supported_rates):
            print("Input rates:", input_supported_rates)
        if len(output_supported_rates):
            print("Output rates:", output_supported_rates)
        if len(full_duplex_rates):
            print("Full duplex: ", full_duplex_rates)

        print("--------------------------------")

    p.terminate()


if __name__ == "__main__":
    printAllInfos()
