import sys
import os
import numpy
from io import IOBase
from types import ModuleType, FunctionType
from SmartFramework.serialize.tools import (
    tuple_from_instance,
    class_str_from_class,
    instance,
    const,  # needed for eval of python code containing enum ,
    _get_setters,
    _get_getters,
    _get_properties,
    encoder_parameters,
    blosc_compressions,
    setters_names_from_class,
    class_from_class_str,
    not_memorized_types,
    constructors,
    import_str_from_class_str,
)
from SmartFramework.tools.objects import isInstance, isQWidget

# ne pas effacer instance , besoin dans  exec(string)
from SmartFramework.serialize.serializeRepr import (
    repr_fonctions_numpy_types_to_python_types,
    reprObject,
    reprInitArgs,
    _already_serialized,
    _id_name,
)
from SmartFramework.serialize import serialize_parameters, ExceptionPyQt
from SmartFramework.string import addNewlines
from SmartFramework.files import write, read
from SmartFramework.serialize.plugins.serializejson_numpy import numpyB64

import blosc


instance, numpyB64  # pour eviter warning

# SERIALISATION D'UN SEUL OBJETS (qui peut être un container comme module )
# OU DE PLUSIEURS OBJETS SI ON NE FERME PAS FICHIER (nommer les objets sous des noms differents)
# dans string
# --- API ----------------------


def dumps(
    obj,
    name="obj",
    splitLines=False,
    make_imports=True,
    strict_pickle=False,
    attributes_filter=True,
    properties=False,
    getters=False,
    setters=True,
    remove_default_values=False,
    space=False,
    tabulation="\t",
    round_float=None,
    sort_keys=False,
    bytes_compression=("blosc_zstd", 1),  #
    bytes_size_compression_threshold=512,
    bytes_use_bytesB64=True,  # le laisser ?
    bytearray_use_bytearrayB64=True,  # le laisser ?
    array_use_arrayB64=True,  # le laisser ?
    array_readable_max_size=0,  # 'int32':-1
    numpy_array_use_numpyB64=True,  # le laisser ?
    numpy_array_readable_max_size=0,  # 'int32':-1
    numpy_array_to_list=False,
    numpy_types_to_python_types=True,
    create_QWidget=True,
    **plugins_parameters,
):

    if strict_pickle:
        attributes_filter = False
        sort_keys = False
    _id_name.clear()
    _already_serialized.clear()
    unexpected_keywords_arguments = set(plugins_parameters) - set(encoder_parameters)
    if unexpected_keywords_arguments:
        raise TypeError(
            "serializejson.Encoder got unexpected keywords arguments '"
            + ", ".join(unexpected_keywords_arguments)
            + "'"
        )
    plugins_parameters_ = encoder_parameters.copy()
    plugins_parameters_.update(plugins_parameters)
    serialize_parameters.__dict__.update(plugins_parameters_)
    serialize_parameters.use_tuple_for_numpy_shape = True
    serialize_parameters.strict_pickle = strict_pickle
    serialize_parameters.attributes_filter = attributes_filter
    serialize_parameters.properties = _get_properties(properties)
    serialize_parameters.getters = _get_getters(getters)
    serialize_parameters.setters = _get_setters(setters)
    serialize_parameters.getters = getters
    serialize_parameters.remove_default_values = remove_default_values
    serialize_parameters.space = space
    serialize_parameters.tabulation = tabulation
    serialize_parameters.round_float = round_float
    serialize_parameters.sort_keys = sort_keys
    bytes_compression_level = 9
    if bytes_compression is not None:
        if isinstance(bytes_compression, (list, tuple)):
            bytes_compression, bytes_compression_level = bytes_compression
            if bytes_compression not in blosc_compressions:
                raise Exception(
                    f"{bytes_compression} compression unknown. Available values for bytes_compression are {', '.join(blosc_compressions)}"
                )
    serialize_parameters.bytes_compression = bytes_compression
    serialize_parameters.bytes_compression_level = bytes_compression_level
    serialize_parameters.bytes_size_compression_threshold = (
        bytes_size_compression_threshold
    )
    serialize_parameters.bytes_use_bytesB64 = bytes_use_bytesB64
    serialize_parameters.bytearray_use_bytearrayB64 = bytearray_use_bytearrayB64
    serialize_parameters.array_use_arrayB64 = array_use_arrayB64
    serialize_parameters.array_readable_max_size = array_readable_max_size
    serialize_parameters.numpy_array_use_numpyB64 = numpy_array_use_numpyB64
    serialize_parameters.numpy_array_readable_max_size = numpy_array_readable_max_size
    serialize_parameters.numpy_types_to_python_types = numpy_types_to_python_types
    serialize_parameters.create_QWidget = create_QWidget
    modules = set()
    # slower but for determinist behaviour in order to be able to versining jsons
    blosc.set_nthreads(1)
    objectStr = pyObject(obj, name, modules=modules, splitLines=splitLines)
    if objectStr:  # peut vouloir serialize module vide pour un SyncModule
        if make_imports:
            if splitLines and isinstance(objectStr, str):
                if objectStr:
                    objectStr = [objectStr]
            return importStr(modules, splitLines=splitLines) + objectStr
        else:
            return objectStr


def loads(string, name="obj", obj=None, setters=True, properties=True, tiny=False):
    serialize_parameters.setters = _get_setters(setters)
    serialize_parameters.properties = _get_properties(properties)
    blosc.set_nthreads(blosc.ncores)
    # if obj is not None :
    #    locals()[name] = obj
    # exec(string)
    # locals()[name] = exobj  # deconne si renome le paramètre exobj et obj ...https://bugs.python.org/issue4831
    ldict = {name: obj}
    exec(string, globals(), ldict)
    try:
        return ldict[name]
    except:
        raise Exception(
            "nom d'objet incunnu dans la string passe au picklePyhton.loads()"
        )


def dump(obj, f, **argsDict):
    """
    sauve un module ou un object dans un fichier .
    il faut préciser le nom de fichier ou qu'il ai un attribut '__file__' (le cas pour module et shelveObjet)
    """

    lines = dumps(obj, **argsDict)

    # si on n'a pas fournit de fichier regarde si l'objet à un attribut __file__ (le cas pour les module et shelveObject)
    if f == None:
        if hasattr(obj, "__file__"):
            f = obj.__file__
            if len(f) > 3 and f[-4:] == ".pyc":
                f = f[:-1]
        else:
            raise Exception(
                "fichier ni fournit ni dans attribut __file__ pour sauver l'objet"
                + str(obj)
            )

    # tente ecriture
    if isinstance(f, str):
        write(f, lines)
    elif isinstance(f, IOBase):
        f.writelines(addNewlines(lines, os.linesep))
    else:
        raise Exception(
            "fichier incorrect (file ou str) pour sauver l'objet" + str(obj)
        )


def load(f, name="obj", existingObject=None, setters=True, properties=True):
    if isinstance(f, str):
        string = read(f)
        return loads(
            string,
            name=name,
            existingObject=existingObject,
            setters=setters,
            properties=properties,
        )
    elif isinstance(f, IOBase):
        return loads(
            f.read(),
            name=name,
            existingObject=existingObject,
            setters=setters,
            properties=properties,
        )
    else:
        raise Exception("l'arg de picklePyton.load() doit être un file ou str")


# ----------------------------------------------------------------------------------------------------------------------------
# --- INTERNES -----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------

_numpy_types = set(
    (
        numpy.bool_,
        numpy.int8,
        numpy.int16,
        numpy.int32,
        numpy.int64,
        numpy.uint8,
        numpy.uint16,
        numpy.uint32,
        numpy.uint64,
        numpy.float16,
        numpy.float32,
        numpy.float64,
    )
)

_numpy_float_types = set(
    (
        numpy.float16,
        numpy.float32,
        numpy.float64,
    )
)

_numpy_int_types = set(
    (
        numpy.int8,
        numpy.int16,
        numpy.int32,
        numpy.int64,
        numpy.uint8,
        numpy.uint16,
        numpy.uint32,
        numpy.uint64,
    )
)


numpy_types_and_ModuleType = _numpy_types | set([ModuleType])


def importStr(modules, splitLines=False):
    importStrList = []
    fromStrList = []
    for module in modules:
        if module.startswith("from "):
            fromStrList.append(module)
        elif module.startswith("import "):
            importStrList.append(module)
        else:
            importStrList.append("import " + module)
    sorted_imports = sorted(importStrList, key=str.lower)
    sorted_from = sorted(fromStrList, key=str.lower)
    sorted_all = sorted_imports + sorted_from
    if splitLines:
        return sorted_all
    elif sorted_all:
        return "\n".join(sorted_all) + "\n"
    else:
        return ""


# OBJECT -> CODE PYTHON en PLUSIEURS INSTRUCTIONS (reconnaissance eventuelle des methode SetAttribut() des objects -------

# @profile
def pyObject(obj, name="obj", indent=0, modules=None, splitLines=False):
    """
    retourne un objet sous la forme de script executable python avec une affectattion à un nom de variable
    """

    type_obj = type(obj)
    if type_obj in numpy_types_and_ModuleType:
        if type_obj is ModuleType:
            return pyModuleAsObject(obj, name, indent, modules)
        elif serialize_parameters.numpy_types_to_python_types:
            # obligé de le mettre avant isInstance(obj) car isInstance(obj) est True
            representation = repr_fonctions_numpy_types_to_python_types[type_obj](
                obj, indent, modules, splitLines
            )
            if serialize_parameters.space:
                return name + " = " + representation
            else:
                return name + "=" + representation

    if isInstance(obj):
        return pyInstance(obj, name, indent, modules, splitLines=splitLines)
    # elif isFunction(obj) or isClass(obj):
    #    raise Exception('fonctions et classes ne sont pour l\'instant pas pickable en code python')
    #    raise Exception , 'Modules non pickable via pyObject , il faut utilser la fonctions pyModule'
    else:
        try:
            representation = reprObject(obj, indent, modules, splitLines)
            if serialize_parameters.space:
                egal = " = "
            else:
                egal = "="
            if type(representation) is list:
                representation[0] = name + egal + representation[0]
                return representation
            else:
                return name + egal + representation
        except ExceptionPyQt:
            if type(obj) is dict:
                return pyDict(obj, name, indent, modules)
            elif type(obj) in [list, set]:
                return pyList(obj, name, indent, modules)
            else:
                raise Exception("impossible de representer l'objet %s" % str(obj))


def pyList(obj, name="obj", indent=0, modules=None):
    elts = []
    for i, value in enumerate(obj):
        # print(name)
        # print('[' + str(i) + ']')
        valueStr = pyObject(value, name + "[" + str(i) + "]", indent, modules)
        if valueStr != "":
            elts.append(valueStr)
    return "    " * indent + ("\n" + "    " * indent).join(elts)


def pyDict(Dict, name="obj", indent=0, modules=None):
    elts = []
    if serialize_parameters.sort_keys:
        keys = sorted(Dict.keys())
    else:
        keys = Dict.keys()
    for key in keys:
        value = Dict[key]
        valueStr = pyObject(value, name + "[" + repr(key) + "]", indent, modules)
        if valueStr != "":
            elts.append(valueStr)
    return "    " * indent + ("\n" + "    " * indent).join(elts)


def pyModuleAsObject(obj, name="obj", indent=0, modules=None):
    elts = []
    if serialize_parameters.space:
        egal = " = "
    else:
        egal = "="
    if False:  # obj in sys.modules.values():
        modules.add("obj.__name__")
        elts.append(name + egal + obj.__name__)

    else:
        # A REVOIR !!!!!!!!!!!
        # le modules n'a pas été crée par un import ....
        # il faut soit le serialiser sous forme d'objet
        # soit le réouvrir à partir d'un fichier ?
        # il faudrait aussi eviter reserialiser plusieurs fois un module ...

        # elts.append(name + egal + "types.ModuleType(" + obj.__name__ + ")")
        # if modules != None:
        #    modules.add("new")
        modules.add("types")
        elts.append(f'obj=types.ModuleType("{obj.__name__}")')
        state = obj.__dict__
        for key in sorted(state.keys()):
            if not (key.startswith("__") and key.endswith("__")):
                value = state[key]
                if type(value) not in (FunctionType, type, ModuleType):
                    elts.append(
                        pyObject(
                            value, name + "." + key, indent=indent, modules=modules
                        )
                    )
                elif type(value) is ModuleType:
                    modules.add(value.__name__)
    return "    " * indent + ("\n" + "    " * indent).join(elts)


# @profile
def pyInstance(obj, name="obj", indent=0, modules=None, splitLines=False):
    """
    retourne un objet sous la forme de script executable python
    si __reduce__() et pas __setstate__(self,etat) :
        nom  = Classe(parametres_init)
        nom.attribut1  = ...
        nom.attribut2  = ...
    si pas __reduce__() et pas __setstate__(self,etat)
        nom  = new.instance(Classe) ou nom class.__new__(class)
        nom.attribut1  = ...
        nom.attribut2  = ...
    si __reduce__() et __setstate__(self,etat)
        nom  = Classe(parametres_init)
        nom.__setstate__(etat)
    si pas __reduce__() et __setstate__(self,etat)
        nom  = new.instance(Classe)
        nom.__setstate__(etat)
        //nom  = new.instance(Classe,{....})
    """

    id_ = id(obj)
    if not isinstance(obj, not_memorized_types):
        if id_ in _already_serialized:
            qualified_name = _id_name.get(id_)
            if qualified_name:
                return qualified_name
            else:
                raise ValueError(
                    f"{obj} is already_serialized but not accessible with qualified name."
                )
        else:
            _already_serialized[id_] = obj
            _id_name[id_] = name

    # print(name)

    # 97.5 %du temps sur obj = bytes(numpy.arange(2**18,dtype=numpy.float64).data)
    class_, initArgs, state, listitems, dictitems, newArgs = tuple_from_instance(obj)
    if initArgs is not None:
        if listitems:
            initArgs += (listitems,)
        if dictitems:
            initArgs += (dictitems,)

    module_str = None
    if isinstance(class_, str):
        classStr = class_
        if modules is not None:
            module_str = import_str_from_class_str(class_)
    else:
        classStr = class_str_from_class(class_)
        if modules is not None:
            module_test = class_.__module__
            if module_test != "builtins":
                module_str = module_test
    elts = []

    if serialize_parameters.create_QWidget or not isQWidget(obj):
        #  si objet PyQt a priori l'objet à été crée par l'init pas besoin de le recréer... dans l'idéal il faudrait à la fin du __init__ sauvegader liste d'attribut existant pour savoir lesquels creer.....

        if module_str:
            modules.add(module_str)
        if serialize_parameters.space:
            egal = " = "
        else:
            egal = "="
        if initArgs is not None:
            # elts.append(name + ' = ' + classStr + serializeRepr.reprInitArgs(initArgs,indent,modules))
            reprInit = reprInitArgs(initArgs, indent, modules)
            elts.append(f"{name}{egal}{classStr}{reprInit}")
        else:  # justNew , pas de iniarg ni state
            elts.append(name + egal + classStr + ".__new__(" + classStr + ")")

    if state:
        if hasattr(obj, "__setstate__"):
            elts.append(
                name + ".__setstate__(" + reprObject(state, indent + 1, modules) + ")"
            )

        elif type(state) is dict:
            setters = serialize_parameters.setters
            if type(setters) is dict:
                if isinstance(class_, str):
                    class_ = class_from_class_str(class_)
                setters = setters.get(class_, False)
            if setters is True:
                setters = setters_names_from_class(type(obj))

            for key, value in state.items():
                if setters and key in setters:
                    elts.append(
                        name
                        + "."
                        + setters[key]
                        + "("
                        + reprObject(value, indent + 1, modules)
                        + ")"
                    )
                elif key == "~connections":
                    for connection in value:
                        signal_name_sig = "." + connection.signal_name
                        if connection.signature is not None:
                            signal_name_sig += "[" + connection.signature + "]"
                        elts.append(
                            _id_name[id(connection.signal_object)]
                            + signal_name_sig
                            + ".connect("
                            + _id_name[id(connection.slot_object)]
                            + "."
                            + connection.slot_name
                            + ")"
                        )
                else:
                    s = pyObject(
                        value,
                        name + "." + key,
                        indent=indent,
                        modules=modules,
                        splitLines=splitLines,
                    )
                    if s:
                        if type(s) is list:
                            elts.extend(s)
                        else:
                            elts.append(s)
        else:
            raise Exception(
                "Erreure:  getstate retourne autre chose qu'un dictionnaire , sans qu'il y ai un setstate()"
            )
    # print(elts)
    if splitLines:
        if indent == 0:
            return elts
        else:
            return ["    " * indent + elt for elt in elts]
    else:
        return "    " * indent + ("\n" + "    " * indent).join(elts)
