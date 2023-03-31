import os.path
import numpy
import math
import blosc
from collections import OrderedDict
from io import IOBase
from math import log10, floor
from rapidjson import RawBytesToPutInQuotes, RawBytes, RawString
from SmartFramework.files import read, write
from SmartFramework.string.encodings import b64, b64_blosc
from SmartFramework.serialize import serialize_parameters
from SmartFramework.serialize.plugins.serializejson_numpy import numpyB64
from SmartFramework.serialize.tools import (
    tuple_from_instance,
    class_str_from_class,
    instance,
    const,
    _get_setters,
    _get_getters,
    _get_properties,
    encoder_parameters,
    blosc_compressions,
    Reference,
    not_memorized_types,
    import_str_from_class_str,
)


b64, b64_blosc, instance, numpyB64, const  # pour evier warnings et besoin
NoneType = type(None)
numpyIntTypes = set(
    (
        numpy.int64,
        numpy.int32,
        numpy.int16,
        numpy.int8,
        numpy.uint64,
        numpy.uint32,
        numpy.uint16,
        numpy.uint8,
    )
)

# ---- MODELISATION PICKLE ------------------------------------


def dumps(
    obj,
    modules=None,
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
    serialize_parameters.remove_default_values = remove_default_values
    # serialize_parameters.set_attributs = _get_set_attributs_classes_strings(set_attributs)
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
    # slower but for determinist behaviour in order to be able to versining jsons
    blosc.set_nthreads(1)
    # serialize_parameters.create_QWidget = create_QWidget
    return reprObject(obj, modules=modules)


def loads(string, modules=[], setters=True, properties=True):
    serialize_parameters.setters = _get_setters(setters)
    serialize_parameters.properties = _get_properties(properties)
    blosc.set_nthreads(blosc.ncores)
    for module in modules:
        if not module.startswith("from "):
            # exec("import "+module) # marche mais pas tres securisé..
            dot_index = module.find(".")
            if dot_index != -1:
                __import__(module)
                package = module[:dot_index]
                globals()[package] = __import__(package)
            else:
                # try:
                #    # seul ne marche pas si "." dans le nom du module ..
                globals()[module] = __import__(module)
                # except:
                #    print("bug")
        else:
            exec(module)
    return eval(string)


def dump(obj, f, **argsDict):
    """serialise obj dans fichier f, qui peut etre un objet  file ou le nom de fichier"""
    string = dumps(obj, **argsDict)
    if type(f) is str or type(f) == str:
        write(f, string)
    elif isinstance(f, IOBase):
        f.write(string)
    else:
        raise Exception(
            "le 2eme arg de pickleRepr.dump() doit être un file ou nom de fichier"
        )


def load(f, modules=[], setters=True, properties=True):
    """de-serialise obj à partir de fichier f, qui peut etre un objet  file ou le nom de fichier"""
    if isinstance(f, str):
        return loads(read(f), modules, setters=setters, properties=properties)
    elif isinstance(f, IOBase):
        return loads(f.read, modules, setters=setters, properties=properties)
    else:
        raise Exception(
            "l'argument de serializeRepr.load() doit être un file ou nom de fichier"
        )


# --- FONCTIONS INTERNES -------------------

# OBJECT -> CODE PYTHON en UNE INSTRUCTION  (réimplementation de repr() pour supporter objects et enregistre liste de module à importer à la déserialisation) ------------------------------------

_id_name = {}
_already_serialized = {}


def reprObject(obj, indent=0, modules=None, splitLines=False):
    """
    retourne un objet sous la forme d'une seul instruction (pour pouvoir être mis dans une liste par ex) :
    Classe(parametres_init)         # juste init avec parametres d'initialisation
    new.instance(Classe,{.....})    # juste restauration dictionnaire
    instance(Classe,parametres_init,state)# init et restauration dictionnaire ?
    ???                                   # avec __setstate__
    """

    typeObj = type(obj)
    if typeObj in repr_set:
        return repr(obj)
    elif typeObj in repr_fonctions:
        return repr_fonctions[typeObj](obj, indent, modules, splitLines)
    elif (
        serialize_parameters.numpy_types_to_python_types
        and typeObj in repr_fonctions_numpy_types_to_python_types
    ):
        return repr_fonctions_numpy_types_to_python_types[typeObj](
            obj, indent, modules, splitLines
        )
    elif isinstance(obj, IOBase):
        return reprFile(obj, indent, modules)
    else:
        return reprInstance(obj, indent, modules, splitLines=splitLines)


def reprFile(f, indent=0, modules=None, splitLines=False):
    name = f.name
    if serialize_parameters.forceRelativePath:
        name = os.path.abspath(name)
    elif serialize_parameters.forceAbsolutPath:
        name = os.path.abspath(name).replace("\\", "/").replace("//", "\\\\")
    return "open('%s','%s',encoding = '%s')" % (f.name, f.mode, f.encoding)


def reprIterable(obj, indent=0, modules=None, splitLines=False):
    tabulation = serialize_parameters.tabulation
    elts = []
    oneline = 1
    for value in obj:
        valueStr = reprObject(value, indent + 1, modules)
        elts.append(valueStr)
        # if type(value) not in [int,float,str] :
        #      oneline = 0
        if valueStr.find("\n") != -1:
            oneline = 0
    if type(obj) is tuple:
        startStr, endStr = "(", ")"
        if len(obj) == 1:
            elts.append("")
    elif type(obj) is list:
        startStr, endStr = "[", "]"
    elif type(obj) is set:
        if len(obj):
            startStr, endStr = "{", "}"
        else:
            return "set()"
    if oneline:
        joinStr = "," + " " * serialize_parameters.space
        return startStr + joinStr.join(elts) + endStr
    else:
        if splitLines:
            joinStr = (indent + 1) * tabulation
            lines = [startStr]
            for elt in elts[:-1]:
                lines.append(joinStr + elt + ",")
            lines.append(joinStr + elts[-1])
            lines.append(joinStr + endStr)
            return lines
        else:
            joinStr = ",\n" + (indent + 1) * tabulation
            return (
                startStr
                + "\n"
                + (indent + 1) * tabulation
                + joinStr.join(elts)
                + "\n"
                + indent * tabulation
                + endStr
            )


def reprDict(Dict, indent=0, modules=None, splitLines=False, ordered_dict=False):
    if serialize_parameters.space:
        dot = " : "
        comma = ", "
    else:
        dot = ":"
        comma = ","
    elts = []
    oneline = 1
    if not ordered_dict and serialize_parameters.sort_keys:
        for key in sorted(Dict.keys()):
            value = Dict[key]
            elts.append(repr(key) + dot + reprObject(value, indent + 1, modules))
            if type(value) not in [int, float, str]:
                oneline = 0
    else:
        for key, value in Dict.items():
            elts.append(repr(key) + dot + reprObject(value, indent + 1, modules))
            if type(value) not in [int, float, str]:
                oneline = 0
    if oneline:
        return "{" + comma.join(elts) + "}"
    else:
        tabulation = serialize_parameters.tabulation
        joinStr = ",\n" + (indent + 1) * tabulation
        return (
            "{"
            + "\n"
            + (indent + 1) * tabulation
            + joinStr.join(elts)
            + "\n"
            + indent * tabulation
            + "}"
        )


def reprType(obj, indent=0, modules=None, splitLines=False):
    if modules != None:
        module = obj.__module__
        if module != "builtins":
            modules.add(module)
    if obj is NoneType:
        return "type(None)"
    else:
        return class_str_from_class(obj)


def reprBytes(obj, indent=0, modules=None, splitLines=False):
    if obj.isascii():
        try:
            obj.decode("cp1252_printables")
            return repr(obj)
        except:
            pass
    return reprInstance(obj, indent, modules)


def repr_(obj, indent=0, modules=None, splitLines=False):
    return repr(obj)


def reprReference(obj, indent=0, modules=None, splitLines=False):
    return _id_name[id(obj.obj)] + obj.sup_str


def reprFloat(obj, indent=0, modules=None, splitLines=False):
    if math.isnan(obj):
        modules.add("math")
        return "math.nan"
    elif math.isinf(obj):
        modules.add("math")
        if obj > 0:
            return "math.inf"
        else:
            return "-math.inf"
    elif obj != 0.0 and serialize_parameters.round_float is not None:
        if abs(obj) < 1.0:
            roundDigit = (
                max(-int(floor(log10(abs(obj)))), 0) + serialize_parameters.round_float
            )  # permet de garder un round_float+1 chiffdres significatif si obj < 1.
        else:
            roundDigit = serialize_parameters.round_float
        return repr(round(obj, roundDigit))
    else:
        return repr(obj)


def reprOrderedDict(obj, indent=0, modules=None, splitLines=False):
    if modules is not None:
        modules.add("collections")
    return "collections.OrderedDict(%s)" % reprDict(obj, ordered_dict=True)


def reprRawBytesToPutInQuotes(obj, indent=0, modules=None, splitLines=False):
    return f"'{obj.value.decode('UTF_8')}'"


def reprRawBytes(obj, indent=0, modules=None, splitLines=False):
    return obj.value.decode("UTF_8")


def reprRawString(obj, indent=0, modules=None, splitLines=False):
    return obj.value


repr_fonctions = {
    dict: reprDict,
    type: reprType,
    float: reprFloat,
    bytes: reprBytes,
    bytearray: reprBytes,
    list: reprIterable,
    tuple: reprIterable,
    set: reprIterable,
    Reference: reprReference,
    OrderedDict: reprOrderedDict,
    RawBytesToPutInQuotes: reprRawBytesToPutInQuotes,
    RawBytes: reprRawBytes,
    RawString: reprRawString,
}

repr_fonctions_numpy_types_to_python_types = {
    numpy.bool_: repr_,
    numpy.int8: repr_,
    numpy.int16: repr_,
    numpy.int32: repr_,
    numpy.int64: repr_,
    numpy.uint8: repr_,
    numpy.uint16: repr_,
    numpy.uint32: repr_,
    numpy.uint64: repr_,
    numpy.float16: reprFloat,
    numpy.float32: reprFloat,
    numpy.float64: reprFloat,
}

repr_set = set((type(None), bool, int, complex, str))

# @profile


def reprInitArgs(initArgs, indent=0, modules=None, start="("):
    if type(initArgs) is dict:
        return (
            start
            + ",".join(
                (
                    key + "=" + reprObject(value, indent, modules)
                    for key, value in initArgs.items()
                )
            )
            + ")"
        )
    else:  # tuple ou liste
        if len(initArgs) == 1:
            return (
                start + reprObject(initArgs[0], indent, modules) + ")"
            )  # sert à eviter la virgule avant la parenthèse fermante  repr((4,)) -> (4,)
        else:
            if start:
                return reprObject(initArgs, indent, modules)
            else:
                return reprObject(initArgs, indent, modules)[1:]


# @profile
def reprInstance(inst, indent=0, modules=None, splitLines=False):

    # if isQWidget(inst):
    #    raise ExceptionPyQt(str(type(inst)) +' est un objet PyQt non representable en une ligne '
    id_ = id(inst)
    if not isinstance(inst, not_memorized_types):
        if id_ in _already_serialized:
            qualified_name = _id_name.get(id_, None)
            if qualified_name:
                return qualified_name
            # else:
            #    return f'"{inst}" is already_serialized but not accessible with qualified name.'
            #    raise ValueError(f"{inst} is already_serialized but not accessible with qualified name.")
        else:
            _already_serialized[id_] = inst

    class_, initArgs, state, listitems, dictitems, newArgs = tuple_from_instance(inst)

    space = " " * serialize_parameters.space

    if isinstance(class_, str):
        if class_ == "const":
            const_ = initArgs[0]
            if modules is not None:
                module_str = import_str_from_class_str(const_)
                if module_str:
                    modules.add(module_str)
            return const_
        classStr = class_
        if modules is not None:
            module_str = import_str_from_class_str(class_)
            if module_str:
                modules.add(module_str)
    else:
        classStr = class_str_from_class(class_)
        if modules is not None:
            module = class_.__module__
            if module != "builtins":
                modules.add(module)

    if initArgs is not None:
        if listitems:
            initArgs += (listitems,)
            listitems = None
        if dictitems:
            initArgs += (dictitems,)
            dictitems = None

    if state or listitems or dictitems:
        if initArgs is not None:
            construct_str = classStr + reprInitArgs(initArgs, indent, modules)
        else:
            if not hasattr(inst, "__init__") or isinstance(inst, tuple):
                if newArgs is None:
                    construct_str = classStr + "()"
                elif isinstance(inst, dict) and type(newArgs) is dict:
                    construct_str = (
                        classStr + "(" + reprDict(newArgs, indent, modules) + ")"
                    )
                else:
                    construct_str = classStr + reprInitArgs(newArgs, indent, modules)
            else:
                if state or listitems or dictitems:
                    construct_str = classStr
                else:
                    newArgs_type = type(newArgs)
                    if newArgs_type in (list, tuple, dict) and newArgs:
                        args_tail = reprInitArgs(newArgs, indent, modules, start="")
                        construct_str = f"{classStr}.__new__({classStr},{args_tail}"
                    else:
                        construct_str = classStr + ".__new__(" + classStr + ")"

        elts = []
        elts.append(construct_str)
        if listitems:
            elts.append(
                "__items__"
                + space
                + "="
                + space
                + reprObject(listitems, indent + 1, modules)
            )
        elif dictitems:
            elts.append(
                "__items__"
                + space
                + "="
                + space
                + reprObject(dictitems, indent + 1, modules)
            )
        if state:
            if type(state) is dict:
                len_elts = len(elts)
                for key, value in state.items():
                    if type(key) is not str:
                        del elts[len_elts:]
                        elts.append(
                            "__state__"
                            + space
                            + "="
                            + space
                            + reprObject(state, indent + 1, modules)
                        )
                        break
                    elts.append(
                        key
                        + space
                        + "="
                        + space
                        + reprObject(value, indent + 1, modules)
                    )
            else:
                elts.append(
                    "__state__"
                    + space
                    + "="
                    + space
                    + reprObject(state, indent + 1, modules)
                )
        if modules is not None:
            modules.add("from SmartFramework.serialize.tools import instance")
        startStr = "instance("
        endStr = ")"
        if splitLines:
            joinStr = (indent + 1) * serialize_parameters.tabulation
            lines = [startStr]
            for elt in elts[:-1]:
                lines.append(joinStr + elt + ",")
            lines.append(joinStr + elts[-1])
            lines.append(joinStr + endStr)
            return lines
        else:
            tabulation = serialize_parameters.tabulation
            joinStr = ",\n" + (indent + 1) * tabulation
            return (
                startStr
                + "\n"
                + (indent + 1) * tabulation
                + joinStr.join(elts)
                + "\n"
                + indent * tabulation
                + endStr
            )
    elif newArgs is not None or initArgs is None:
        if not hasattr(inst, "__init__") or isinstance(inst, (tuple, bytes)):
            if newArgs is None:
                return classStr + "()"
            if isinstance(inst, dict) and type(newArgs) is dict:
                return classStr + "(" + reprDict(newArgs, indent, modules) + ")"
            return classStr + reprInitArgs(newArgs, indent, modules)
        newArgs_type = type(newArgs)
        if newArgs_type in (list, tuple, dict) and newArgs:
            args_tail = reprInitArgs(newArgs, indent, modules, start="")
            return f"{classStr}.__new__({classStr},{args_tail}"
        return classStr + ".__new__(" + classStr + ")"
    return classStr + reprInitArgs(initArgs, indent, modules)
