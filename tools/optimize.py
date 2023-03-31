import os
import gc
from SmartFramework.files import directory, joinPath
from SmartFramework.serialize import serializejson
from SmartFramework.tools.process import kill, suspend
from SmartFramework.tools.devices import Devices
from SmartFramework.tools.power import setActive, getActive


class Optimize:
    def __init__(self):
        optimizePath = joinPath(
            directory(__file__), "optimize" + "_" + os.environ["COMPUTERNAME"], "json"
        )
        self.processSupended = []
        if os.path.exists(optimizePath):
            optimizeDict = serializejson.load(optimizePath)
            kill(optimizeDict["process_to_kill"])
            self.processSupended = suspend(optimizeDict["process_to_suspend"])
            self.devices = Devices()
            self.devices.disable(optimizeDict["devices_to_desactive"])
            self.oldPowerProfil = getActive()
            setActive(optimizeDict["power_profile"])
            if not optimizeDict["garbage_collector"]:
                gc.disable()

    def __del__(self):
        setActive(self.oldPowerProfil)
        for process in self.processSupended:
            process.resume()
        self.devices.reactiveAll()
        gc.enable()


optimize = Optimize()
