from SmartFramework.designer.uiToPython import uiToPython
from SmartFramework.files import dragAndDrop, read


def uiToPythonAndExecute(path):
    pythonPath = uiToPython(path)
    exec(compile(read(pythonPath), pythonPath, "exec"))


dragAndDrop(callback=uiToPythonAndExecute, extension="ui")
