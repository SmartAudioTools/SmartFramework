import subprocess
import unicodedata
from SmartFramework.files import directory

info = subprocess.STARTUPINFO()
info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
info.wShowWindow = subprocess.SW_HIDE

devconPath = directory(__file__) + "/devcon/x64/devcon.exe"


def toAsciiLower(s):
    # rajouté  .replace(u"\u2018", "'").replace(u"\u2019", "'") pour gerer title de http://www.france24.com/fr/20150109-charlie-hebdo-je-ne-suis-pas-charlie-contestation-emotion-france-attentat-journlaistes-liberte-expression/
    return (
        unicodedata.normalize("NFKD", s)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )


def list2cmdline(seq):
    """Adaptation of supbprocess.list2cmdline in order to add quotes if & is in a argument."""
    result = []
    needquote = False
    for arg in seq:
        bs_buf = []
        # Add a space to separate this argument from the others
        if result:
            result.append(" ")
        needquote = (
            (" " in arg) or ("\t" in arg) or ("&" in arg and arg != "&") or not arg
        )
        if needquote:
            result.append('"')
        for c in arg:
            if c == "\\":
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append("\\" * len(bs_buf) * 2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)
        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)
        if needquote:
            result.extend(bs_buf)
            result.append('"')
    return "".join(result)


subprocess.list2cmdline = list2cmdline


class Device:
    def __init__(self, ID, name=None):
        self.name = name
        self.ID = ID
        self.newID = "@" + ID.replace("?", "*")

    def getState(self):
        string = (
            subprocess.Popen(
                [devconPath, "status", self.newID],
                stdout=subprocess.PIPE,
                startupinfo=info,
            )
            .communicate()[0]
            .decode("cp1252")
        )
        lines = string.split("\r\n")
        for line in lines:
            if line.endswith("Driver is running.") or line.endswith(
                "Device is currently stopped."
            ):
                return True
            elif line.endswith("Device is disabled."):
                return False
        else:
            print(self.name)
            print(self.newID)
            print(string)
            return False

    def setState(self, state):
        if state in (True, "enable"):
            self.enable()
        if state in (False, "disable"):
            self.disable()

    state = property(getState, setState)

    def disable(self):
        subprocess.call(
            [devconPath, "disable", self.newID], startupinfo=info
        )  # , stdout=subprocess.PIPE,startupinfo=info).communicate()[0].decode("cp1252")

    def enable(self):
        subprocess.call([devconPath, "enable", self.newID], startupinfo=info)


class Devices:
    def __init__(self):
        self.makeDevicesDict()
        # self.devicesListe = self.devicesDict.keys()
        self.toReactive = []

    def makeDevicesDict(self):
        # classes
        string = (
            subprocess.Popen(
                [devconPath, "classes"], stdout=subprocess.PIPE, startupinfo=info
            )
            .communicate()[0]
            .decode("cp1252")
            .replace("\xa0", " ")
        )
        lines = string.split("\r\n")
        classeNameAndID = []
        for line in lines[1:-1]:
            firstDot = line.find(":")
            if firstDot != -1:
                classeID = line[:firstDot].strip()
                classeName = line[firstDot + 1 :].strip()
            if (
                classeName == "Files dattente à limpression :"
            ):  # hack pour corriger bug de devcon qui n'a pas l'air d'aimer le fait qu'il y ai deux apostrophes
                classeName = "Files d'attente à l'impression"
            if (
                classeName == "Périphérique dacquisition dimages"
            ):  # hack pour corriger bug de devcon qui n'a pas l'air d'aimer le fait qu'il y ai deux apostrophes
                classeName = "Périphérique d'acquisition d'images"
            classeNameAndID.append((classeName, classeID))
        classeNameAndID = sorted(
            classeNameAndID, key=lambda s: (toAsciiLower(s[0]), toAsciiLower(s[1]))
        )
        # devices :
        devices = dict()
        classeNameToDevices = dict()
        for classeName, classeID in classeNameAndID:
            # j'ai utilisé find , car y'avait des problème avec listclass pour la categorie "Image"
            string = (
                subprocess.Popen(
                    [devconPath, "find", "=" + classeID],
                    stdout=subprocess.PIPE,
                    startupinfo=info,
                )
                .communicate()[0]
                .decode("cp1252")
            )
            lines = string.split("\r\n")
            deviceNameAndID = []
            for line in lines:
                firstDot = line.find(":")
                if firstDot != -1:
                    deviceID = line[:firstDot].strip()
                    deviceName = line[firstDot + 1 :].strip()
                    deviceNameAndID.append((deviceName, deviceID))
            deviceNameAndID = sorted(
                deviceNameAndID, key=lambda s: (toAsciiLower(s[0]), toAsciiLower(s[1]))
            )
            for deviceName, deviceID in deviceNameAndID:
                device = Device(deviceID, deviceName)
                devices[deviceID] = device
                if classeName not in classeNameToDevices:
                    classeNameToDevices[classeName] = [device]
                else:
                    classeNameToDevices[classeName].append(device)
        self.classeNameToDevices = classeNameToDevices
        self.devices = devices

    def disable(self, deviceNameOrID):
        if isinstance(deviceNameOrID, (list, tuple)):
            for elt in deviceNameOrID:
                self.disable(elt)
        else:
            if deviceNameOrID in self.devices:
                deviceID = deviceNameOrID
                self.devices[deviceID].disable()
                self.toReactive.append(deviceID)
            else:
                for device in self.devices.values():
                    if device.name == deviceNameOrID:
                        device.disable()
                        self.toReactive.append(device.ID)

    def enable(self, deviceName):
        if deviceName in self.devices:
            self.devices[deviceName].enable()
        else:
            for device in self.devices.values():
                if device.name == deviceName:
                    device.enable()

    def reactiveAll(self):
        for deviceName in self.toReactive:
            self.enable(deviceName)
