# -*- coding: utf-8 -*-
import types
from io import IOBase
from SmartFramework.tools.objects import (
    isInstance,
    isQWidget,
    isModule,
    isClass,
    isFunction,
)

from SmartFramework.serialize.tools import (
    tuple_from_instance,
    class_str_from_class,
    # moduleStrFromClass,
    # _get_all_setters,
)
from SmartFramework.serialize import serializeRepr
from SmartFramework.serialize import serialize_parameters
from SmartFramework.serialize import ExceptionPyQt
from SmartFramework.serialize.serializePython import pyObject, importStr
from SmartFramework.files import write, read


createComment = "\t# line for create object (don't touch comment!)"

# ---- SERIALISATION D'UN SEUL OBJETS (qui peut être un container comme module ) ---------------------------


def dumps(
    obj,
    make_imports=True,
    attributes_filter="_",
    call_setters=True,
    space=False,
    tabulation="\t",
    round_float=None,
    numpy_array_dumped_base64=True,
    numpy_array_readable_max_size={"int32": -1},
    use_numpyB64_bytearrayB64=True,
    numpy_types_to_python_types=True,
    create_QWidget=True,
):
    serialize_parameters.attributes_filter = attributes_filter
    serialize_parameters.all_setters = _get_all_setters(call_setters)
    serialize_parameters.space = space
    serialize_parameters.tabulation = tabulation
    serialize_parameters.round_float = round_float
    serialize_parameters.numpy_array_dumped_base64 = numpy_array_dumped_base64
    serialize_parameters.numpy_array_readable_max_size = numpy_array_readable_max_size
    serialize_parameters.use_numpyB64_bytearrayB64 = use_numpyB64_bytearrayB64
    serialize_parameters.numpy_types_to_python_types = numpy_types_to_python_types
    serialize_parameters.create_QWidget = create_QWidget
    modules = set()
    objectStr = tinyObject(obj, modules=modules)
    if make_imports:
        return importStr(modules) + objectStr
    else:
        return objectStr


def loads(string, existingObject=None):
    (
        importLines,
        classeLine,
        initArgsLine,
        stateLine,
        otherLines,
        commentLines,
    ) = parseString(string)
    if existingObject:
        exec("\n".join(importLines))  # effectue les imports
        # ne recréer pas l'objet
        for i, otherLine in enumerate(otherLines):
            if otherLine[0] not in " }":
                otherLines[i] = "existingObject." + otherLine
        stringToExec = "\n".join(otherLines)
        exec(stringToExec)  # restaure les attributs
        return existingObject
    else:
        # on doit créer l'objet un peu plus galère

        if classeLine:  # on a sauvé une instance sous forme de module
            exec("\n".join(importLines))  # effectue les imports
            obj = eval(classeLine)  # créer l'objet
            if otherLines:  # restaure les attributs
                exec("obj." + "\nobj.".join(otherLines))
            return obj
        else:
            # on n'a pas sauvé une instance sous forme de module ? ou on ne souhaite pas la creer (pyqt)? ou peut être une valeure , une liste ou dictionnaire
            if len(otherLines) == 1:
                try:  # essaye de restaurer une valeure , une liste ou dictionnaire
                    return eval(otherLines[0])
                except:
                    # on a sauvé un module avec qu'un seul objet
                    pass

            # on va considere qu'on a serialize un module
            # Crée un nouveau module vide (avec un nom bidon)
            m = types.ModuleType("module_name")
            # from StringIO import  StringIO
            # emulateFile = StringIO(string)
            # execfile(emulateFile ,m.__dict__,m.__dict__)      # ne marche pas ! execute le code du fichier avec m.__dict__ comme dictionnaire de variables locales et globales
            exec(
                "\n".join(importLines)
            )  # effectue les imports                                                                         # ne recréer pas l'objet
            if otherLines:
                prefixedOtherLines = []
                for line in otherLines:
                    if line[0] in " ]}":
                        prefixedOtherLines.append(line)
                    else:
                        prefixedOtherLines.append("m." + line)
                exec("\n".join(prefixedOtherLines))  # restaure les attributs
            return m


# --- dans fichier ---


def dump(
    obj,
    f,
    make_imports=True,
    attributes_filter="_",
    call_setters=True,
    space=False,
    tabulation="\t",
    round_float=None,
    numpy_array_dumped_base64=True,
    numpy_array_readable_max_size={"int32": -1},
    use_numpyB64_bytearrayB64=True,
    numpy_types_to_python_types=True,
    create_QWidget=True,
):
    """
    sauve un module ou un object dans un fichier .
    il faut préciser le nom de fichier ou qu'il ai un attribut '__file__' (le cas pour module et shelveObjet)
    """

    # serialise l'objet
    string = dumps(
        obj,
        make_imports=make_imports,
        attributes_filter=attributes_filter,
        call_setters=call_setters,
        space=space,
        tabulation=tabulation,
        round_float=round_float,
        numpy_array_dumped_base64=numpy_array_dumped_base64,
        numpy_array_readable_max_size=numpy_array_readable_max_size,
        use_numpyB64_bytearrayB64=use_numpyB64_bytearrayB64,
        numpy_types_to_python_types=numpy_types_to_python_types,
        create_QWidget=create_QWidget,
    )
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
        write(f, string)
    elif isinstance(f, IOBase):
        f.write(string)
    else:
        raise Exception(
            "fichier incorrect (file ou str) pour sauver l'objet" + str(obj)
        )


def load(f, existingObject=None):
    if isinstance(f, str):
        return loads(read(f), existingObject)
    elif isinstance(f, IOBase):
        return loads(f.read(), existingObject)
    else:
        raise Exception("l'arg de picklePyton.load() doit être un file ou str")


# ---------------------------------------------------------------------------------------


# -----------------------------------------------------
def parseString(string):
    # approche separation des instruction :
    Lines = string.replace(",\n", ",").split("\n")

    importLines = []
    classeLine = None
    initArgsLine = None
    otherLines = []
    commentLines = []
    stateLine = None
    for line in Lines:
        if line.startswith("#"):
            commentLines.append(line)
        elif line.startswith("import ") or line.startswith("from "):
            importLines.append(line)
        elif line.endswith(createComment):
            classeLine = line
        elif line != "":
            otherLines.append(line)
    return importLines, classeLine, initArgsLine, stateLine, otherLines, commentLines


# ----------------------------------------------------------------------------------------------------------------------------
# --- FONCTIONS INTERNES -----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------


def tinyObject(obj, name="obj", indent=0, modules=None):
    """
    retourne un objet sous la forme de script executable python avec une affectattion à un nom de variable
    """
    if isInstance(obj):
        return tinyInstance(obj, name, indent, modules)
    elif isFunction(obj) or isClass(obj):
        raise Exception(
            "fonctions et classes ne sont pour l'instant pas pickable en code python"
        )
    elif isModule(obj):
        return tinyModule(obj, modules)
    else:
        try:
            return serializeRepr.reprObject(obj, indent, modules)
        except ExceptionPyQt:
            if type(obj) is dict:
                raise Exception(
                    "les dictionaire contenant des objects PyQt ne sont pour l'instant pas serializable directemetn en code de module python"
                )
            elif type(obj) in (list, set):
                raise Exception(
                    "les listes contenant des objects PyQt ne sont pour l'instant pas serializable directemetn en code de module python"
                )


def tinyModule(obj, modules=None):
    stringAll = []
    modules = set()

    state = obj.__dict__
    for key in sorted(state.keys()):
        if not (key.startswith("__") and key.endswith("__")):
            value = state[key]
            if type(value) not in (types.FunctionType, type, types.ModuleType):
                stringAll.append(pyObject(value, key, indent=0, modules=modules))
            elif type(value) is types.ModuleType:
                modules.add(value.__name__)
    return importStr(modules) + "\n".join(stringAll)


def tinyInstance(obj, name="obj", indent=0, modules=None):
    classe, initArgs, state = tuple_from_instance(obj)
    classStr = class_str_from_class(classe)

    elts = []

    if serialize_parameters.create_QWidget or not isQWidget(
        obj
    ):  #  si objet PyQt a priori l'objet à été crée par l'init pas besoin de le recréer... dans l'idéal il faudrait à la fin du __init__ sauvegader liste d'attribut existant pour savoir lesquels creer.....
        if modules != None:
            modules.add(moduleStrFromClass(classe))
        if initArgs != None:
            elts.append(
                classStr
                + serializeRepr.reprInitArgs(initArgs, indent, modules)
                + createComment
            )
        else:  # justNew , pas de iniarg ni state
            elts.append(classStr + ".__new__(" + classStr + ")" + createComment)
    if state:
        if hasattr(obj, "__setstate__"):
            elts.append(
                "__setstate__("
                + serializeRepr.reprObject(state, indent + 1, modules)
                + ")"
            )

        elif type(state) is dict:
            for key in sorted(state.keys()):
                value = state[key]
                no_setter = True
                all_setters = serialize_parameters.all_setters
                if all_setters is True or (
                    (all_setters is not False) and (classStr in all_setters)
                ):
                    # essaye setter avec la syntaxe set_attribut
                    attributSetMethode = "set_" + key

                    if hasattr(obj, attributSetMethode):
                        no_setter = False
                        elts.append(
                            attributSetMethode
                            + "("
                            + serializeRepr.reprObject(value, indent + 1, modules)
                            + ")"
                        )
                    else:
                        attributSetMethode = (
                            "set" + key[0].upper() + key[1:]
                        )  # essaye setter avec la syntaxe setAttribut
                        if hasattr(obj, attributSetMethode):
                            no_setter = False
                            elts.append(
                                attributSetMethode
                                + "("
                                + serializeRepr.reprObject(value, indent + 1, modules)
                                + ")"
                            )
                if no_setter:
                    s = pyObject(value, key, indent=indent, modules=modules)
                    if s:
                        elts.append(s)
        else:
            raise Exception(
                "Erreure:  getstate retourne autre chose qu'un dictionnaire , sans qu'il y ai un setstate()"
            )

    return "    " * indent + ("\n" + "    " * indent).join(elts)
