from SmartFramework.files import dragAndDrop, name
from SmartFramework.serialize import serializejsonlab

# sys.argv = ["", "C:/Users/Baptiste/powercfg.txt"]
def compileJsons(paths):
    print(paths)
    compiled = dict()
    for path in paths:
        jsonName = name(path)
        compiled[jsonName] = serializejsonlab.load(path, remove_comments=True)
    serializejsonlab.dump(compiled, "compiled.json")


dragAndDrop(callback=compileJsons, extension="json", group=True)
