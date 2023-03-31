# -*- coding: utf-8 -##

# imports ----

from SmartFramework.sync.syncObjectUI import SyncObjectUI
from SmartFramework.tools.objects import addArgs, add_Args
from qtpy import QtCore, QtGui, QtWidgets


# la classe doit avoir le meme nom que le fichier avec la première lettre capitalisée (en Majuscule) (Obligatoire pour compilation)
# class Monobject(QtCore.QObject):## les modulse non graphique doivent: heriter de QtCore.objects (pour changment simple d'heritage lors de la compilation),avoir l'extension .pyw
# class MonobjectUI(QtWidgets.QWidget):## les modules graphique doivent : ne pas heriter de QtCore.objects, avoir leur nom finissant par UI, avoir l'extension .pyw
class MonobjectSyncableUI(SyncObjectUI):
    # heritage de SyncObjectUI (facultatif) -----
    ## permet de rendre l'objet synchronisable avec une syncData (via slot et signal)
    ## permet d'heriter des propriétés
    ## permet d'herite d'un attribut sync  :

    # constructor ------------

    def __init__(self, parent=None, value=0):
        # arguments : seront transformés en propriété lors de ma compilation -> QtDesigner
        ## doit avoir un argument parent (pas forcement en première position)
        ## doit avoir tout ces argument par défaut pour  permetre instanciation dans QtDesigner ? pour permetre compilation ?
        ## D'une facon générale , je veux peut être trop en mettre dans les InitArgs au lieu d'exploiter les propriétés ?

        # appel constructeur de la Classe de base  --------
        SyncObjectUI.__init__(self, parent) / QtCore.objects.__init__(
            self, parent
        ) / QtWidgets.QWidget.__init__(
            self, parent
        )  ## appel constructeur de la Classe de base

        # synchronisation  --------------
        self.output.connect(
            self.sync.input
        )  ## connection à l'attribut sync herité de SyncOBject  => permet de rendre l'objet synchronisable
        self.sync.output[object].connect(
            self.input
        )  ## connection à l'attribut sync herité de SyncOBject  => permet de rendre l'objet synchronisable

        # création des attributs  -------
        ## si posible  les argument du __init__ doivent tous (sauf self et parent) intialiser des attribut avec le le meme nom (eventuellement précedé de '_')
        ##  => pour permetre accés et affichage de leur valeures par defaut via propriétés (codés ou generés pas mon compilateur) dans qtdesigner
        ## (mais pas obligatoire car , remis sous forme d'argument à init aprés compilation)

        self.__dict__.update(
            locals()
        )  ## recopie tous les argument du __init__ dans des attributs . ATTENTION : on va éviter pour les object PyQt avec parent pour ne pas avoir de références circulaire à la serialisaion !
        addArgs(
            locals()
        )  ## recopie les argument du __init__ dans des attributs  (sauf self)
        add_Args(
            locals()
        )  ## recopie les argument du __init__ PRECEDES DE "_" dans des attributs (sauf self)
        ## si on redefini pas __getstate__ pour retourner sans '_':
        ## => ne sera pas serializé si utilise le filtre '_' (que j'ai mis par defaut)
        ## sans le filtre (je supose à la relecture)
        ## => ne poura pas reconaitre les setter lors de la serialisation
        ## => ne poura pas faire appel au propriétés lors de la serialisation  (?)
        ## si on ne souhaite pas "cacher une attribut" => sera serializé par defaut:
        self.value = value
        ## si on souhaite "cacher une attribut" => ne sera pas serializé si utilise le filtre '_' (que j'ai mis par defaut):
        self._value = value

        # initialisation ----------------
        self.resize(50, 22)

        # création des connexions  ------
        self.monSignal.connect(
            slot / methode / fonction
        )  ## connect monSignal à slot/methode/fonction (connecte la surcharge par defaut , si signal surcharg?)
        self.monSignal[float].connect(slot)  ## connect la surcharge "float" du signal
        self.monSignal.connect(
            slot, type=qtpy.QtCore.Qt.AutoConnection
        )  ## avec un certain type de connection :
        ##Auto Connection(défaut)/Direct Connection/Queued Connection/Blocking Queued Connection/Unique Connection
        # déconnexion ?
        self.monSignal.disconnect(slot)  ## deconnecte le slot reliées au signal
        self.monSignal.disconnect()  ## deconnecte tous les slots reli?es au signal

    # signaux  --------------------------                 ## New signals should only be defined in sub-classes of QObject
    ## signature Python (conversion automatique et systematique ?)
    outValue = QtCore.Signal(float)  ## le prefixe "out" permet d'eviter conflit de noms
    ##(avec atribut , methode , propriété ou argument qui sera transformé en propriete)
    ## (a verifier , à priori solution  "propriete as value"
    ## dans TODO - InitArgs vs Attributs vs Properties vs Slot vs Sync vs Serialize vs Decorators.rtf)
    monSignal1 = (
        QtCore.Signal()
    )  ## définit un signal appelé monSignal qui ne prend aucun argument.
    monSignal2 = QtCore.Signal(
        bool
    )  ## définit un signal qui prend un argument objet python
    monSignal3 = QtCore.Signal(
        int
    )  ## définit un signal qui prend un argument objet python
    monSignal4 = QtCore.Signal(
        float
    )  ## définit un signal qui prend un argument objet python
    monSignal5 = QtCore.Signal(
        str
    )  ## définit un signal qui prend un argument objet python
    monSignal6 = QtCore.Signal(
        object
    )  ## définit un signal qui prend un argument tout autre objet python (dict, liste , autres..)
    monsignal7 = QtCore.Signal(
        int, int
    )  ## définit un signal qui prend deux arguments entiers.
    monSignal8 = QtCore.Signal(
        [int], [float]
    )  ## définit un signal "monSignal" qui a deux surcharges,une qui prend un argument entier,et une un float

    monSignal = QtCore.Signal(
        name="trueSignal"
    )  ## définit un signal appelé "trueSignal" (dans Qt Designer), qui ne prend aucun argument.

    # slots -----------------------------    ## (methodes rendues visible sous forme de slots dans Qt Designer )

    # sans renomage

    ## définit slot du même nom que la methode ("monSlot1"),qui ne prend aucun argument.:
    @QtCore.Slot()
    def monSlot1(
        self,
    ):  ## Rem : accepte toutes les données avec ma compilation , mais pas dans preview designer !!!
        """C++: void foo()"""

    @QtCore.Slot(bool)
    @QtCore.Slot(
        int
    )  ## définit slots du même nom que la methode ("monSlot"),qui accepte un argument avec differentes signatures
    @QtCore.Slot(float)
    def monSlot2(self, value):
        """Two slots will be defined in the QMetaObject."""

    @QtCore.Slot(
        str
    )  ## définit slot du même nom que la methode ("monSlot3"),qui ne prend  un unicode/QString  (EVITER Slot (srt))
    def monSlot3(self, objt):
        """C++: void monSlot(QString)"""
        pass

    @QtCore.Slot(
        object
    )  ## définit slot du même nom que la methode ("monSlot4"),qui ne prend  un objet python (dict , liste , autres...)
    def monSlot4(self, objt):
        """C++: void monSlot(PyQt_PyObject)"""
        pass

    @QtCore.Slot(
        int, int
    )  ## définit slot du même nom que la methode ("monSlot5"),qui ne prend  deux entiers en argument.
    def monSlot5(self, int1, int2):
        """C++: void monSlot(int, int)"""

    # avec renomage                          ## on peut avoir plusieurs methode de nom differents mais avec meme nom de slot

    @QtCore.Slot(
        name="trueSlot"
    )  ## définit un slot appelé "trueSlot", qui ne prend aucun argument.
    def maMethode(self):
        """C++: void trueSlot()"""

    @QtCore.Slot(
        int, name="trueSlot"
    )  ## redeinit pour meme slot "trueSlot", version qui accepte un argument int
    def maMethodeInt(self):
        """C++: void trueSlot()"""

    @QtCore.Slot(QObject)
    def monSlot(self, obj):
        """C++: int foo(QObject *)"""
        pass

    ## @QtCore.Slot(str)                  ## A EVITER : marche mais en fait la fonction recuperera un unicode
    ## @QtCore.Slot(monObjet)             ## A EVITER : marche mais ne fera pas distinction lors du choix du slot a utiliser ?

    ## @Slot (int, result=int)
    ## def foo(self, arg1):
    ##    """ C++: int foo(int) """

    # slots/ (futur) properties ------
    ## avec ma convention de nommage ?      (a verifier , à priori solution  "propriete as value"
    ## dans TODO - InitArgs vs Attributs vs Properties vs Slot vs Sync vs Serialize vs Decorators.rtf)
    ## les prefixe "in" et "set" permetent d'eviter conflit de noms                                               ## (avec attribut ou signal )

    @QtCore.Slot(float)
    def setValue(
        self, value
    ):  ## si le slot / methode n'emet pas de signal (entrée froide)
        ##self.value =  value                  ## A EVITER CAR POSERA PROBLEME SI TRANSFORME EN PROPRIETE  => BOUCLE INFINIE
        self.__dict__[
            "value"
        ] = value  ## prévient pb liés à l'eventuelle creation futur de propriété de meme nom que attribut
        ## (le cas si on a fait un self.__dict__.update(locals())?)
        ## par exemple lors de ma compilation  -> QtDesigner , propriétés qui seront generée pour arguments du __init__
        ## si on a rendu privé les attribut avec prefixe '_' (par ex en utilisant add_Args(locals())):
        self._value = value

    @QtCore.Slot(float)
    def inValue(self, value):  ## si le slot / methode emet un signal (entrée chaude)
        ##self.value =  value                ## A EVITER CAR POSERA PROBLEME SI TRANSFORME EN PROPRIETE  => BOUCLE INFINIE
        self.__dict__[
            "value"
        ] = value  ## prévient pb liés à l'eventuelle creation futur de propriété de meme nom que attribut
        ## (le cas si on a fait un self.__dict__.update(locals())?)
        ## par exemple lors de ma compilation  -> QtDesigner , propriétés qui seront generée pour arguments du __init__
        ## si on a rendu privé les attribut avec prefixe '_' (par ex en utilisant add_Args(locals())):
        self._value = value
        self.outValue.emit(value)  ## on emet un signal

    @QtCore.Slot()  ## si on souhaite pouvoir recuperer une valeure avec un "bang"
    def getValue(
        self,
    ):  ## a voir , rajouté en novembre 2012 , un peu à l'arrache sans voir anciennes reflexions
        self.outValue.emit(self.__dict__["value"])
        self.outValue.emit(self._value)
        return self.__dict__["value"]
        return self._value

    # properties ------------------------
    ## on evitera en général de créer le getter et la propriété ? et se contentera de coder methode setter si dessus .
    ## laissant le soin à mon compilateur de les créer à partir des init arguments uniqument pour Qt Designer ?
    ## permetra de limiter leur utilisation (notament de getValue(), quand fera juste appel à self.value dans le code )
    value = QtCore.Property(
        int, QBaseClasse.value, QBaseClasse.setValue
    )  ## redefinition d'un propriété herité d'une basse classe
    ## pour support suppresion de 'set' lors de la compilation ui -> python (dans tinySetProperty())
    def setValue(self, value):
        self.__dict__[
            "value"
        ] = value  ## si propriété meme nom que attribut (le cas si on a fait un self.__dict__.update(locals())?)
        ## si on a rendu privé les attribut avec prefixe '_' (par ex en utilisant add_Args(locals())):
        self._value = value
        ##self.value =  value               ## A EVITER CAR POSERA PROBLEME SI TRANSFORME EN PROPRIETE => BOUCLE INFINIE

    def getValue(self):
        return self.__dict__["value"]
        return self._value
        ##return self.value                  ## A EVITER CAR POSERA PROBLEME SI TRANSFORME EN PROPRIETE => BOUCLE INFINIE

    value = QtCore.Property(int, getValue, setValue)

    # serialization ---------------------

    def __getstate__(
        self,
    ):  ## retourne l'etat de la classe, si on souhaite avoir autre comportement que celui par defaut qui est de serialize self.__dict__
        if self.serialize:
            return {
                "value": self.value
            }  ## retourne l'etat de la classe sous forme d'un objet qui sera lui meme serialise (dictionnaire ou autre)
            ## Si __setstate__() n'est pas disponible , l'objet retourne devra etre un dictionnaire
            ##(les elements seront restaures comme etant des attributs), sinon l'objet peut etre n'importe quel objet serialisable
        else:
            pass  ## permet de ne pas restaure l'etat de l'objet apres l'__init__()

    def __setstate__(
        self, state
    ):  ## si on souhaite avoir autre comportement que celui par defaut qui conssite a restauration des attribut
        ## prend en parametre l'objet decrivant l'etat de la classe et replace l'instance dans l'etat dans lequel elle etait avant la serialisation.
        ## peut eventuellement executer du code d'initialisation (notament si __reduce__ n'a pas ete definit  et qu'il n'y a donc pas eu d'appelle du __init__
        ## (Rem : Si __getstate__() n'est pas disponible, c'est __dict__ qui aura ete directement serialise)
        self.__dict__.update(state)  ## comportement par defaut
        ## pass                              ## si on veut eviter de restaurer etat , meme si on l'a enregistré

    # methodes --------------------------

    def outputObject(
        self, obj
    ):  ## (peut servir directemnet de slots, mais invisible dans Qt Designer )
        # code
        ## .....
        # emition de signaux

        self.monSignal.emit()  ## emet avec la surcharge par defaut (selon moi)
        self.monSignal.emit(arg1, arg2)
        self.monSignal[float].emit(
            f
        )  ## emet avec la surcharge float du signal (selon moi)
        self.monSignal[object].emit(obj)

    # methodes pour size ---------------

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(100, 100)

    # Events ----------------------------

    def closeEvent(
        self, QCloseEvent
    ):  ## si on préfère utiliser evenent plutot que le signal lastWindowClosed
        ## ....
        ## QCloseEven.ignore() ## si on veut empecher fermeture fenetre:
        QCloseEvent.accept()

    def paintEvent(self, event):
        painter = QtUI.QPainter()
        painter.begin(self)
        painter.end()

    def mousePressEvent(self, event):
        print("mouse pressed !!!")
        if event.button() == QtCore.Qt.RightButton:
            pass
        else:
            pass
        ## informe Qt  que l'evenement à été traité .sinon il est propagé au widgets parents de l’objet cible initial. jusqu’à être géré ou que l’objet QApplication soit atteint.:
        event.accept()

    def mouseReleaseEvent(self, event):
        event.accept()

    def mouseMoveEvent(self, event):
        X = QtGui.QCursor.pos().x()
        Y = QtGui.QCursor.pos().y()
        event.accept()

    def keyPressEvent(self, event):
        print("key pressed !!!!")
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        event.accept()

    def keyReleaseEvent(self, event):
        pass


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = MonobjetUI()
    widget.show()  ## si objet avec Interface graphique (UI)
    app.exec_()
