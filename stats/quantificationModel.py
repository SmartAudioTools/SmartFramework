# -*- coding: utf-8 -*-
"""
Created on Tue Dec 06 13:56:19 2011

@author: guilbut
"""
from .lastSquare import *


class QuantificationModelFiltreAndLastSquare:
    def __init__(
        self,
        aTheorique,
        drifMesured=0.0,
        driftMaxDeviation=float("inf"),
        T=100,
        debug=False,
    ):

        self.aTheorique = aTheorique
        self.aMesured = self.aTheorique * (drifMesured + 1.0)
        self.aMax = self.aMesured * (1.0 + driftMaxDeviation)
        self.aMin = self.aMesured / (1.0 + driftMaxDeviation)

        self.C = []  # [0,0]]  # liste de points convexes

        self.a = self.aMesured
        self.b = 0
        self.lastSquareRecursive = LastSquareRecursiveExp(self.aTheorique, T=T)

        self.debug = debug
        if self.debug:
            self.points = []  # listes pour debugage
            self.computedPoints = []  # listes pour debugage

    def printAB(self):
        print("a : %f , b : %f , xi ref : %f" % (self.a, self.b, self.C[-1][0]))

    def getDrift(self):
        return (self.a / self.aTheorique) - 1.0

    def appendToCAndCumpute(self, xi, yi, pente):
        self.C.append([xi, yi])
        if len(self.C) > 5:
            self.lastSquareRecursive.addPoint(xi, yi)
            self.a = self.lastSquareRecursive.a
            self.b = self.lastSquareRecursive.b
            # self.printAB()

    def compareToC(self, xi, yi):

        if len(self.C) == 0:
            # test si la liste C est non vide....
            # on devrait pouvoir s'en passer
            self.C.append([xi, yi])
            self.a = self.aMesured
            self.b = yi - self.a * xi
            # self.printAB()
        else:

            # filtrage (supresion - des points tel que pente % dernier point de C > aMax
            pente = (yi - self.C[-1][1]) / (xi - self.C[-1][0])
            if pente > self.aMax:
                pass
                # print("point ignore")

            else:
                if self.debug:
                    self.computedPoints.append([xi, yi])  #  pour debugage
                self.appendToCAndCumpute(xi, yi, pente)

    def addPoint(self, xi, yi, wi=1.0):
        self.compareToC(xi, yi)
        if self.debug:
            self.points.append([xi, yi, wi, self.a, self.b])


# AUTRES MODELS -----------------------------------------------------------


class QuantificationModelConvexeandLastSquare:
    def __init__(
        self,
        aTheorique,
        drifMesured=0.0,
        driftMaxDeviation=float("inf"),
        xMax=400,
        T=10,
        debug=False,
    ):

        self.xMax = xMax
        self.aTheorique = aTheorique
        self.aMesured = self.aTheorique * (drifMesured + 1.0)
        self.aMax = self.aMesured * (1.0 + driftMaxDeviation)
        self.aMin = self.aMesured / (1.0 + driftMaxDeviation)

        self.C = []  # [0,0]]  # liste de points convexes

        self.a = self.aMesured
        self.b = 0

        self.lastSquareRecursive = LastSquareRecursiveExp(self.aTheorique, T=T)

        self.lastCindexAddedToLastSquare = 5
        self.debug = debug
        if self.debug:
            self.points = []  # listes pour debugage
            self.computedPoints = []  # listes pour debugage

    def printAB(self):
        print("a : %f , b : %f , xi ref : %f" % (self.a, self.b, self.C[-1][0]))

    def getDrift(self):
        return (self.a / self.aTheorique) - 1.0

    def appendToCAndCumpute(self, xi, yi, pente):
        self.C.append([xi, yi])

        # moindre carrés en retard car on peut modifier la fin de C...
        # a revoir
        if len(self.C) > self.lastCindexAddedToLastSquare:
            if xi > self.C[self.lastCindexAddedToLastSquare][0] + self.xMax:
                self.lastSquareRecursive.addPoint(
                    self.C[self.lastCindexAddedToLastSquare][0],
                    self.C[self.lastCindexAddedToLastSquare][1],
                )
                self.lastCindexAddedToLastSquare += 1
                self.a = self.lastSquareRecursive.a
                self.b = self.lastSquareRecursive.b

    def compareToC(self, xi, yi):

        if len(self.C) == 0:
            # test si la liste C est non vide....
            # on devrait pouvoir s'en passer
            self.C.append([xi, yi])
            self.a = self.aMesured
            self.b = yi - self.a * xi
            # self.printAB()
        else:

            # filtrage des points tel que pente % dernier point de C > aMax
            pente = (yi - self.C[-1][1]) / (xi - self.C[-1][0])
            if pente > self.aMax:
                pass

            else:
                if self.debug:
                    self.computedPoints.append([xi, yi])  #  pour debugage
                if len(self.C) > 1:
                    penteFromLast = (self.C[-1][1] - self.C[-2][1]) / (
                        self.C[-1][0] - self.C[-2][0]
                    )

                    if pente > penteFromLast or (xi - self.C[-2][0]) > self.xMax:
                        self.appendToCAndCumpute(xi, yi, pente)
                    else:
                        self.C.pop()
                        self.compareToC(xi, yi)

                else:
                    self.appendToCAndCumpute(xi, yi, pente)

    def addPoint(self, xi, yi, wi=1.0):
        self.compareToC(xi, yi)
        if self.debug:
            self.points.append([xi, yi, wi, self.a, self.b])


class QuantificationModelLastSquare:
    def __init__(
        self,
        aTheorique,
        drifMesured=0.0,
        driftMaxDeviation=float("inf"),
        T=10000,
        debug=False,
    ):

        self.aTheorique = aTheorique
        self.aMesured = self.aTheorique * (drifMesured + 1.0)

        self.a = self.aMesured
        self.b = 0
        self.lastSquareRecursive = LastSquareRecursiveExp(self.aTheorique, T=T)

        self.debug = debug
        if self.debug:
            self.points = []  # listes pour debugage
            self.C = []  # listes pour debugage

    def printAB(self):
        print("a : %f , b : %f , xi ref : %f" % (self.a, self.b, self.C[-1][0]))

    def getDrift(self):
        return (self.a / self.aTheorique) - 1.0

    def addPoint(self, xi, yi, wi=1.0):

        self.lastSquareRecursive.addPoint(xi, yi)
        self.a = self.lastSquareRecursive.a
        self.b = self.lastSquareRecursive.b
        if self.debug:
            self.points.append([xi, yi, wi, self.a, self.b])
            self.C.append([xi, yi])


class QuantificationModelStraight:
    def __init__(
        self, aTheorique, drifMesured=0.0, driftMaxDeviation=float("inf"), debug=False
    ):

        self.aTheorique = aTheorique
        self.aMesured = self.aTheorique * (drifMesured + 1.0)
        self.aMax = self.aMesured * (1.0 + driftMaxDeviation)
        self.aMin = self.aMesured / (1.0 + driftMaxDeviation)

        self.C = []  # [0,0]]  # liste de points convexes

        self.a = self.aMesured
        self.b = 0
        self.maxInterval = 0

        self.debug = debug
        if self.debug:
            self.points = []  # listes pour debugage
            self.computedPoints = []  # listes pour debugage

    def printAB(self):
        print("a : %f , b : %f , xi ref : %f" % (self.a, self.b, self.C[-1][0]))

    def getDrift(self):
        return (self.a / self.aTheorique) - 1.0

    def appendToCAndCumpute(self, xi, yi, pente):
        self.C.append([xi, yi])

        lastInterval = self.C[-1][0] - self.C[-2][0]

        if lastInterval > self.maxInterval:
            # print( lastInterval, xi)
            self.maxInterval = lastInterval
            if pente < self.aMin:
                self.a = self.aMesured
            else:
                self.a = pente
            self.b = yi - self.a * xi
            # self.printAB()

    def compareToC(self, xi, yi):

        if len(self.C) == 0:
            # test si la liste C est non vide....
            # on devrait pouvoir s'en passer
            self.C.append([xi, yi])
            self.a = self.aMesured
            self.b = yi - self.a * xi
            # self.printAB()
        else:

            # filtrage des points tel que pente % dernier point de C > aMax
            pente = (yi - self.C[-1][1]) / (xi - self.C[-1][0])
            if pente > self.aMax:
                pass

            else:
                if self.debug:
                    self.computedPoints.append([xi, yi])  #  pour debugage
                if len(self.C) > 1:
                    penteFromLast = (self.C[-1][1] - self.C[-2][1]) / (
                        self.C[-1][0] - self.C[-2][0]
                    )

                    if pente > penteFromLast:
                        self.appendToCAndCumpute(xi, yi, pente)
                    else:
                        self.C.pop()
                        self.compareToC(xi, yi)

                else:
                    self.appendToCAndCumpute(xi, yi, pente)

    def addPoint(self, xi, yi, wi=1.0):
        self.compareToC(xi, yi)
        if self.debug:
            self.points.append([xi, yi, wi, self.a, self.b])


class QuantificationModelOldRalentissementAuthorized:
    def __init__(
        self,
        aTheorique,
        drifMesured=0.0,
        driftMaxDeviation=float("inf"),
        xMax=float("inf"),
        debug=False,
    ):

        self.xMax = xMax
        self.aTheorique = aTheorique
        self.aMesured = self.aTheorique * (drifMesured + 1.0)
        self.aMax = self.aMesured * (1.0 + driftMaxDeviation)
        self.aMin = self.aMesured / (1.0 + driftMaxDeviation)

        self.C = []  # [0,0]]  # liste de points convexes

        self.a = self.aMesured
        self.b = 0
        self.maxInterval = 0

        self.debug = debug
        if self.debug:
            self.points = []  # listes pour debugage
            self.computedPoints = []  # listes pour debugage

    def printAB(self):
        print("a : %f , b : %f , xi ref : %f" % (self.a, self.b, self.C[-1][0]))

    def getDrift(self):
        return (self.a / self.aTheorique) - 1.0

    def appendToCAndCumpute(self, xi, yi, pente):
        self.C.append([xi, yi])

        lastInterval = self.C[-1][0] - self.C[-2][0]

        if lastInterval > self.maxInterval:
            # print( lastInterval, xi)
            self.maxInterval = lastInterval
            if pente < self.aMin:
                self.a = self.aMesured
            else:
                self.a = pente
            self.b = yi - self.a * xi
            # self.printAB()

    def compareToC(self, xi, yi):

        if len(self.C) == 0:
            # test si la liste C est non vide....
            # on devrait pouvoir s'en passer
            self.C.append([xi, yi])
            self.a = self.aMesured
            self.b = yi - self.a * xi
            # self.printAB()
        else:

            # filtrage des points tel que pente % dernier point de C > aMax
            pente = (yi - self.C[-1][1]) / (xi - self.C[-1][0])
            if pente > self.aMax:
                pass

            else:
                if self.debug:
                    self.computedPoints.append([xi, yi])  #  pour debugage
                if len(self.C) > 1:
                    penteFromLast = (self.C[-1][1] - self.C[-2][1]) / (
                        self.C[-1][0] - self.C[-2][0]
                    )

                    if pente > penteFromLast or (xi - self.C[-2][0]) > self.xMax:
                        self.appendToCAndCumpute(xi, yi, pente)
                    else:
                        self.C.pop()
                        self.compareToC(xi, yi)

                else:
                    self.appendToCAndCumpute(xi, yi, pente)

    def addPoint(self, xi, yi, wi=1.0):
        self.compareToC(xi, yi)
        if self.debug:
            self.points.append([xi, yi, wi, self.a, self.b])
