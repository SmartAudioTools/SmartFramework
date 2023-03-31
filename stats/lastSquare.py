from math import exp


class LastSquareRecursive:
    """calcul les moindres carres de facon recursive , sans stocker les points , ni les ponderer"""

    def __init__(self, a=0, b=0, debug=False):

        self.Exi2 = 0
        self.Exi = 0
        self.Eyixi = 0
        self.Eyi = 0
        self.Ewi = 0
        self._a = a
        self._b = b

        # pour debugage
        self.debug = debug
        if self.debug:
            self.points = []
        self.computed = False

    def addPoint(self, xi, yi, wi=1):
        self.computed = False
        self.Ewi += wi
        self.Exi2 += wi * xi**2
        self.Exi += wi * xi
        self.Eyixi += wi * yi * xi
        self.Eyi += wi * yi

        # pour debugage
        if self.debug:
            self.points.append([xi, yi, wi, self.a, self.b, self.getY(xi)])

    def computeAB(self):

        n = self.Ewi
        if n > 1:
            Exi2 = self.Exi2
            Exi = self.Exi
            Eyi = self.Eyi
            Eyixi = self.Eyixi
            self._a = float(Eyixi * n - Eyi * Exi) / float(Exi2 * n - Exi**2)
            self._b = float(Exi * Eyixi - Eyi * Exi2) / float(Exi**2 - Exi2 * n)
        elif n == 1:
            self._b = self.Eyi - self._a * self.Exi
        self.computed = True

    def getY(self, x):
        if not self.computed:
            self.computeAB()
        return self._a * x + self._b

    @property
    def a(self):
        if not self.computed:
            self.computeAB()
        return self._a

    @property
    def b(self):
        if not self.computed:
            self.computeAB()
        return self._b

    def getAB(self):
        if not self.computed:
            self.computeAB()
        return [self._a, self._b]


class LastSquareRecursiveReweightLiars(LastSquareRecursive):
    """suprime les liars de facon un peu crade..."""

    def __init__(self, a=0, b=0, seuil=1.0, reweight=0.0, debug=False):
        LastSquareRecursive.__init__(self, a, b, debug)
        self.seuil = seuil
        self.reweight = reweight

    def addPoint(self, xi, yi, wi=1):
        if self.Ewi > 100 and abs(yi - self.getY(xi)) > self.seuil:
            wi = self.reweight
        LastSquareRecursive.addPoint(self, xi, yi, wi)


class LastSquareRecursiveMoving(LastSquareRecursive):
    """calcul les moindres carres sur les nMax derniers points,
    il faudra verifier qu\'on accumule pas d\'erreures"""

    def __init__(self, a=0, b=0, nMax=100, debug=False):

        LastSquareRecursive.__init__(self, a, b, debug)
        self.lastPoints = []
        self.nMax = nMax

    def addPoint(self, xi, yi, wi=1):

        LastSquareRecursive.addPoint(self, xi, yi, wi)
        self.lastPoints.append([xi, yi, wi])
        if self.Ewi > self.nMax:
            self.delIndex(0)

    def delIndex(self, index):
        point = self.lastPoints.pop(0)
        self.delPoint(point[0], point[1], point[2])

    def delPoint(self, xi, yi, wi=1):

        self.Ewi -= wi
        self.Exi2 -= wi * xi**2
        self.Exi -= wi * xi
        self.Eyixi -= wi * yi * xi
        self.Eyi -= wi * yi


class LastSquareRecursiveMoving2(LastSquareRecursive):
    """calcul les moindres carres sur les nMax derniers points,
    plutot que de propager erreures, on soustrait les sommes partielles d\'un point en retard"""

    def __init__(self, a=0, b=0, nMax=100, debug=False):
        self.actualLastSquare = LastSquareRecursive()
        self.delayLastSquare = LastSquareRecursive()
        self.lastPoints = []  # listes pour debugage
        self.nMax = nMax
        self.debug = debug
        if self.debug:
            self.points = []  # listes pour debugage

    def addPoint(self, xi, yi, wi=1):
        self.lastPoints.append([xi, yi, wi])
        self.actualLastSquare.addPoint(xi, yi, wi)
        if len(self.lastPoints) > self.nMax:
            point = self.lastPoints.pop(0)
            self.delayLastSquare.addPoint(point[0], point[1], point[2])
            # print('suprime un point')
        if self.debug:
            self.points.append([xi, yi, wi, self.a, self.b])

    def computeAB(self):

        n = len(self.lastPoints)
        if n > 1:
            Exi2 = self.actualLastSquare.Exi2 - self.delayLastSquare.Exi2
            Exi = self.actualLastSquare.Exi - self.delayLastSquare.Exi
            Eyixi = self.actualLastSquare.Eyixi - self.delayLastSquare.Eyixi
            Eyi = self.actualLastSquare.Eyi - self.delayLastSquare.Eyi
            self._a = float(Eyixi * n - Eyi * Exi) / float(Exi2 * n - Exi**2)
            self._b = float(Exi * Eyixi - Eyi * Exi2) / float(Exi**2 - Exi2 * n)
        elif n == 1:
            self._b = self.lastPoints[-1][1] - self.a * self.lastPoints[-1][0]

        self.computed = True


class LastSquareRecursiveExp(LastSquareRecursive):
    """calcul les moindres carres sur les derniers points
    avec un ponderation exponentielle decroissante"""

    def __init__(self, a=0, b=0, T=100.0, debug=False):
        LastSquareRecursive.__init__(self, a, b, debug)
        self.rw = exp(-1.0 / T)

    def addPoint(self, xi, yi, wi=1):
        rw = self.rw
        self.Ewi *= rw
        self.Exi2 *= rw
        self.Exi *= rw
        self.Eyixi *= rw
        self.Eyi *= rw
        LastSquareRecursive.addPoint(self, xi, yi, wi)


class LastSquareRecursiveExpReweightLiars(LastSquareRecursiveExp):
    """calcul les moindres carres sur les derniers points
    avec un ponderation exponentielle décroissante
    tente de suprimer les layer .... (a nettement ameliorer)"""

    def __init__(self, a=0, b=0, T=100.0, seuil=1.0, reweight=0.0, debug=False):
        LastSquareRecursiveExp.__init__(self, a, b, T, debug)
        self.seuil = seuil
        self.reweight = reweight

    def addPoint(self, xi, yi, wi=1):
        if self.Ewi > 50 and abs(yi - self.getY(xi)) > self.seuil:
            wi = self.reweight
        LastSquareRecursiveExp.addPoint(self, xi, yi, wi)
