from io import IOBase
from SmartFramework.files import read, write
import simplejson


MaxObjectNameTranslate = {"int": "maxInt", "toggle": "maxtoggle"}


class MaxPatcher:
    def __init__(self):
        self.fileversion = 1
        self.rect = [29.0, 75.0, 640.0, 480.0]  # dimension du patch
        self.bglocked = 0
        self.defrect = [29.0, 75.0, 640.0, 480.0]
        self.openrect = [
            0.0,
            0.0,
            0.0,
            0.0,
        ]  # (float)  Sets the fixed initial window position (vertical offset/horizontal offset/height/width) for the patcher window.
        # (int)    Toggles opening the patcher in Presentation mode automatically.:
        self.openinpresentation = 0
        self.default_fontsize = 12.0  # (float)  Sets the default font size (in points).
        # (int)    Sets the default type style. 0 is plain (regular), 1 is bold, 2 is italic, and 3 is bold italic.:
        self.default_fontface = 0
        self.default_fontname = "Arial"  # (symbol) Sets the default font name.
        # (int)    Toggles displaying the grid in the patcher window when unlocked.:
        self.gridonopen = 0
        self.gridsize = [15.0, 15.0]  # (float)  Sets the grid size in pixels.
        # (int)    Toggles automatically setting the "Snap To Grid" option when the patcher is unlocked.
        self.gridsnaponopen = 0
        # (int)    Toggles showing the toolbar when the patcher is opened.
        self.toolbarvisible = 1
        # (int)    Sets the rate, in milliseconds, used for animation of object behavior in the patcher window.
        self.boxanimatetime = 200
        # (int)    Toggles saving default-valued object attributes.
        self.imprint = 0
        # (int)    Toggles horizontal scrollbar display in a patcher window.
        self.enablehscroll = 1
        # (int)    Toggles vertical scrollbar display in a patcher window.
        self.enablevscroll = 1
        self.devicewidth = 0.0
        self.boxes = []  # liste d'objet (sous fomre de 2 dictionnaire imbriqués)
        self.lines = []  # liste de connexion ?
        self.parameters = {}


class MaxObject:
    def __init__(self):
        # si objet non-graphique

        maxclass = "newobj"
        text = "objet arg1 arg2"

        # si objet avec texte
        self.fontname = "Arial"
        self.fontsize = 12.0

        # si objet non-graphique
        # classe de l'objet, corresond à __class__ dans ma notatio
        self.maxclass = "toggle"

        # dans tout les cas
        self.patching_rect = [
            286.0,
            353.0,
            20.0,
            20.0,
        ]  # position de l'objet dans le patch (x, y , delta_x, delta_y) , x=0 y=0 en haut à gauche
        self.numinlets = 1  # nombre d'entrées
        self.numoutlets = 1  # nombre de sorties
        self.id = "obj-3"  # identifiant de l'objet (obj-numéro de creation)

        # si sorties
        self.outlettype = [
            "int",
            "signal",
        ]  # liste de type de sortie : "bang" ,"int","float","signal", "" (pour les listes ou message avec selecteur non standard ? )

    def __save__(self):
        pass


def dictMaxFromInstance(inst):
    classe, initArgs, state = tuple_from_instance(inst)
    # dictionnaire  = {'__class__' : classe }
    # dictionnaire  = {'__class__' : classe.__module__ + '.' + classe.__name__ }
    dictionnaire = dict()
    if classe in listeMaxObjects:
        dictionnaire["maxclass"] = classe
    else:
        if initArgs != None:
            dictionnaire["__init__"] = initArgs
            # tente de creer arguments
            initArgsStr = " ".join(initArgs)
            for elt in initArgStr:
                reprObjet(elt)

            dictionnaire["text"] = classe + initArgsStr
        if state:
            if type(state) == dict:
                dictionnaire.update(state)
            else:
                dictionnaire["__state__"] = state

    return dictionnaire


# ---- JSON ------------------------------------


def dumps(obj):
    """on utilise la bibliotheque JSON
    problemes :  tuple-> listes"""
    return simplejson.dumps(
        obj, default=dictMaxMspFromInstance, sort_keys=True, indent=4
    )


def loads(string):
    """on utilise la bibliotheque simpleJSON,    qui sait reconnaitre les string qui n'ont pas besoin d'être unicode
        str -> unicode -> str
    avec JSON on avait le probleme :
        str -> unicode -> unicode"""
    return simplejson.loads(string, object_hook=simplejsonLoadDict)


def dump(obj, f):
    if isinstance(f, str):
        write(f, dumps(obj))
    elif isinstance(f, IOBase):
        f.write(dumps(obj))
    else:
        raise Exception("le 2eme arg de pickleJson.dump() doit être un file ou str")


def load(f):
    if isinstance(f, str):
        return loads(read(f))
    elif isinstance(f, IOBase):
        return loads(f.read)
    else:
        raise Exception("l'arg de pickleJson.load() doit être un file ou str")


# ---- version FILTRE (on va filtrer les variables commencant par '_' si pas de getstate(), ATTENTION pas compatible pickle)---------------------------------


def dumpsFiltre(obj):
    """ATTENTION : non compatible PICKLE
    on va filtrer (ne pas sauver) les variables commencant par la chaine filtre ('_' par defaut)
    on utilise la bibliotheque JSON
    problemes :  tuple-> listes"""
    return simplejson.dumps(
        obj, default=dictFromInstanceFiltre, sort_keys=True, indent=4
    )


# --- MODELISATION DE SHELVE --------------------


def close(filename):
    path = filname


def open(filename):
    if os.path.exists(f):
        obj = load(f)
    else:
        obj = shelveObject(f)
    return obj


# --- FONCTIONS INTERNES -------------------


class shelveObject:
    def __init__(self, filename):
        self.__shelveFile__ = filename

    def sync(self):
        dump(self, self.__shelveFile__)

    def close(self):
        self.sync()


def simplejsonLoadDict(inst):
    """recopie instance en replacant les dictionnaires par des objets  si possible"""
    if inst.has_key("__class__"):
        return instance(**inst)
    else:
        return inst
