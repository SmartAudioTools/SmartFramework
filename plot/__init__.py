# -*- coding: utf-8 -*-
"""
functions.py -  Miscellaneous functions with no other home
Copyright 2010  Luke Campagnola
Distributed under MIT/X11 license. See license.txt for more information.
"""

from __future__ import division
from qtpy import QtGui, QtCore
from qtpy import API_NAME
import struct
import numpy as np

if API_NAME == "PyQt5":
    PYQT = True
    try:
        from PyQt5 import sip
    except ImportError:
        # some Linux distros package it this way (e.g. Ubuntu)
        import sip
elif API_NAME == "PyQt6":
    PYQT = True
    from PyQt6 import sip
elif API_NAME == "PySide2":
    PYQT = False
    import shiboken2 as shiboken
elif API_NAME == "PySide6":
    PYQT = False
    import shiboken6 as shiboken


def _compute_backfill_indices(isfinite):
    # the presence of inf/nans result in an empty QPainterPath being generated
    # this behavior started in Qt 5.12.3 and was introduced in this commit
    # https://github.com/qt/qtbase/commit/c04bd30de072793faee5166cff866a4c4e0a9dd7
    # We therefore replace non-finite values

    # credit: Divakar https://stackoverflow.com/a/41191127/643629
    mask = ~isfinite
    idx = np.arange(len(isfinite))
    idx[mask] = -1
    np.maximum.accumulate(idx, out=idx)
    first = np.searchsorted(idx, 0)
    if first < len(isfinite):
        # Replace all non-finite entries from beginning of arr with the first finite one
        idx[:first] = first
        return idx
    else:
        return None


def _arrayToQPath_all(x, y, finiteCheck):
    n = len(x)
    if n == 0:
        return QtGui.QPainterPath()

    backfill_idx = None
    if finiteCheck:
        isfinite = np.isfinite(x) & np.isfinite(y)
        if not np.all(isfinite):
            backfill_idx = _compute_backfill_indices(isfinite)

    chunksize = 10000
    numchunks = (n + chunksize - 1) // chunksize
    minchunks = 3

    if numchunks < minchunks:
        # too few chunks, batching would be a pessimization
        poly = create_qpolygonf(n)
        arr = ndarray_from_qpolygonf(poly)

        if backfill_idx is None:
            arr[:, 0] = x
            arr[:, 1] = y
        else:
            if isinstance(x, np.ndarray):
                arr[:, 0] = x[backfill_idx]
            else:
                for idx in backfill_idx:
                    arr[idx, 0] = x[idx]
            if isinstance(y, np.ndarray):
                arr[:, 1] = y[backfill_idx]
            else:
                for idx in backfill_idx:
                    arr[idx, 1] = y[idx]

        path = QtGui.QPainterPath()
        if hasattr(path, "reserve"):  # Qt 5.13
            path.reserve(n)
        path.addPolygon(poly)
        return path

    # at this point, we have numchunks >= minchunks

    path = QtGui.QPainterPath()
    if hasattr(path, "reserve"):  # Qt 5.13
        path.reserve(n)
    subpoly = QtGui.QPolygonF()
    subpath = None
    for idx in range(numchunks):
        sl = slice(idx * chunksize, min((idx + 1) * chunksize, n))
        currsize = sl.stop - sl.start
        if currsize != subpoly.size():
            if hasattr(subpoly, "resize"):
                subpoly.resize(currsize)
            else:
                subpoly.fill(QtCore.QPointF(), currsize)
        subarr = ndarray_from_qpolygonf(subpoly)
        if backfill_idx is None:
            subarr[:, 0] = x[sl]
            subarr[:, 1] = y[sl]
        else:
            bfv = backfill_idx[sl]  # view
            subarr[:, 0] = x[bfv]
            subarr[:, 1] = y[bfv]
        if subpath is None:
            subpath = QtGui.QPainterPath()
        subpath.addPolygon(subpoly)
        path.connectPath(subpath)
        if hasattr(subpath, "clear"):  # Qt 5.13
            subpath.clear()
        else:
            subpath = None
    return path


def _arrayToQPath_finite(x, y, isfinite=None):
    n = x.shape[0]
    if n == 0:
        return QtGui.QPainterPath()

    if isfinite is None:
        isfinite = np.isfinite(x) & np.isfinite(y)

    path = QtGui.QPainterPath()
    if hasattr(path, "reserve"):  # Qt 5.13
        path.reserve(n)

    sidx = np.nonzero(~isfinite)[0] + 1
    # note: the chunks are views
    xchunks = np.split(x, sidx)
    ychunks = np.split(y, sidx)
    chunks = list(zip(xchunks, ychunks))

    # create a single polygon able to hold the largest chunk
    maxlen = max(len(chunk) for chunk in xchunks)
    subpoly = create_qpolygonf(maxlen)
    subarr = ndarray_from_qpolygonf(subpoly)

    # resize and fill do not change the capacity
    if hasattr(subpoly, "resize"):
        subpoly_resize = subpoly.resize
    else:
        # PyQt will be less efficient
        def subpoly_resize(n, v=QtCore.QPointF()):
            return subpoly.fill(v, n)

    # notes:
    # - we backfill the non-finite in order to get the same image as the
    #   old codepath on the CI. somehow P1--P2 gets rendered differently
    #   from P1--P2--P2
    # - we do not generate MoveTo(s) that are not followed by a LineTo,
    #   thus the QPainterPath can be different from the old codepath's

    # all chunks except the last chunk have a trailing non-finite
    for xchunk, ychunk in chunks[:-1]:
        lc = len(xchunk)
        if lc <= 1:
            # len 1 means we have a string of non-finite
            continue
        subpoly_resize(lc)
        subarr[:lc, 0] = xchunk
        subarr[:lc, 1] = ychunk
        subarr[lc - 1] = subarr[lc - 2]  # fill non-finite with its neighbour
        path.addPolygon(subpoly)

    # handle last chunk, which is either all-finite or empty
    for xchunk, ychunk in chunks[-1:]:
        lc = len(xchunk)
        if lc <= 1:
            # can't draw a line with just 1 point
            continue
        subpoly_resize(lc)
        subarr[:lc, 0] = xchunk
        subarr[:lc, 1] = ychunk
        path.addPolygon(subpoly)

    return path


def arrayToQPath(x, y, connect="all", finiteCheck=True):
    """
    Convert an array of x,y coordinates to QPainterPath as efficiently as
    possible. The *connect* argument may be 'all', indicating that each point
    should be connected to the next; 'pairs', indicating that each pair of
    points should be connected, or an array of int32 values (0 or 1) indicating
    connections.

    Parameters
    ----------
    x : (N,) ndarray
        x-values to be plotted
    y : (N,) ndarray
        y-values to be plotted, must be same length as `x`
    connect : {'all', 'pairs', 'finite', (N,) ndarray}, optional
        Argument detailing how to connect the points in the path. `all` will
        have sequential points being connected.  `pairs` generates lines
        between every other point.  `finite` only connects points that are
        finite.  If an ndarray is passed, containing int32 values of 0 or 1,
        only values with 1 will connect to the previous point.  Def
    finiteCheck : bool, default Ture
        When false, the check for finite values will be skipped, which can
        improve performance. If nonfinite values are present in `x` or `y`,
        an empty QPainterPath will be generated.

    Returns
    -------
    QPainterPath
        QPainterPath object to be drawn

    Raises
    ------
    ValueError
        Raised when the connect argument has an invalid value placed within.

    Notes
    -----
    A QPainterPath is generated through one of two ways.  When the connect
    parameter is 'all', a QPolygonF object is created, and
    ``QPainterPath.addPolygon()`` is called.  For other connect parameters
    a ``QDataStream`` object is created and the QDataStream >> QPainterPath
    operator is used to pass the data.  The memory format is as follows

    numVerts(i4)
    0(i4)   x(f8)   y(f8)    <-- 0 means this vertex does not connect
    1(i4)   x(f8)   y(f8)    <-- 1 means this vertex connects to the previous vertex
    ...
    cStart(i4)   fillRule(i4)

    see: https://github.com/qt/qtbase/blob/dev/src/gui/painting/qpainterpath.cpp

    All values are big endian--pack using struct.pack('>d') or struct.pack('>i')
    This binary format may change in future versions of Qt
    """

    n = len(x)
    if n == 0:
        return QtGui.QPainterPath()

    connect_array = None
    if isinstance(connect, np.ndarray):
        # make connect argument contain only str type
        connect_array, connect = connect, "array"

    isfinite = None

    if connect == "finite":
        if not finiteCheck:
            # if user specified to skip finite check, then we skip the heuristic
            return _arrayToQPath_finite(x, y)

        # otherwise use a heuristic
        # if non-finite aren't that many, then use_qpolyponf
        isfinite = np.isfinite(x) & np.isfinite(y)
        nonfinite_cnt = n - np.sum(isfinite)
        all_isfinite = nonfinite_cnt == 0
        if all_isfinite:
            # delegate to connect='all'
            connect = "all"
            finiteCheck = False
        elif nonfinite_cnt / n < 2 / 100:
            return _arrayToQPath_finite(x, y, isfinite)
        else:
            # delegate to connect=ndarray
            # finiteCheck=True, all_isfinite=False
            connect = "array"
            connect_array = isfinite

    if connect == "all":
        return _arrayToQPath_all(x, y, finiteCheck)

    backstore = QtCore.QByteArray()
    backstore.resize(4 + n * 20 + 8)  # contents uninitialized
    backstore.replace(0, 4, struct.pack(">i", n))
    # cStart, fillRule (Qt.FillRule.OddEvenFill)
    backstore.replace(4 + n * 20, 8, struct.pack(">ii", 0, 0))
    arr = np.frombuffer(
        backstore, dtype=[("c", ">i4"), ("x", ">f8"), ("y", ">f8")], count=n, offset=4
    )

    backfill_idx = None
    if finiteCheck:
        if isfinite is None:
            isfinite = np.isfinite(x) & np.isfinite(y)
            all_isfinite = np.all(isfinite)
        if not all_isfinite:
            backfill_idx = _compute_backfill_indices(isfinite)

    if backfill_idx is None:
        arr["x"] = x
        arr["y"] = y
    else:
        if isinstance(x, np.ndarray):
            arr["x"] = x[backfill_idx]
        else:
            arr["x"] = [x[idx] for idx in backfill_idx]
        if isinstance(y, np.ndarray):
            arr["y"] = y[backfill_idx]
        else:
            arr["y"] = [y[idx] for idx in backfill_idx]

    # decide which points are connected by lines
    if connect == "pairs":
        arr["c"][0::2] = 0
        arr["c"][1::2] = 1  # connect every 2nd point to every 1st one
    elif connect == "array":
        # Let's call a point with either x or y being nan is an invalid point.
        # A point will anyway not connect to an invalid point regardless of the
        # 'c' value of the invalid point. Therefore, we should set 'c' to 0 for
        # the next point of an invalid point.
        arr["c"][:1] = 0  # the first vertex has no previous vertex to connect
        arr["c"][1:] = connect_array[:-1]
    else:
        raise ValueError('connect argument must be "all", "pairs", "finite", or array')

    path = QtGui.QPainterPath()
    if hasattr(path, "reserve"):  # Qt 5.13
        path.reserve(n)

    ds = QtCore.QDataStream(backstore)
    ds >> path
    return path


def ndarray_from_qpolygonf(polyline):
    nbytes = 2 * len(polyline) * 8
    if PYQT:
        buffer = polyline.data()
        if buffer is None:
            buffer = sip.voidptr(0)
        buffer.setsize(nbytes)
    else:
        ptr = polyline.data()
        if ptr is None:
            ptr = 0
        buffer = shiboken.VoidPtr(ptr, nbytes, True)
    memory = np.frombuffer(buffer, np.double).reshape((-1, 2))
    return memory


def create_qpolygonf(size):
    polyline = QtGui.QPolygonF()
    if PYQT:
        polyline.fill(QtCore.QPointF(), size)
    else:
        polyline.resize(size)
    return polyline


class Pen(QtGui.QPen):
    """A command line friendly layer over `QPen`.

    The interpretation of the `*rest` parameters is type dependent:

    - `Qt.PenStyle`: sets the pen style.
    - `QColor` or `Qt.GlobalColor`: sets the pen color.
    - `float`: sets the pen width.
    """

    def __init__(self, *rest):
        QtGui.QPen.__init__(self)
        self.setWidthF(1.0)
        self.setCosmetic(True)
        for item in rest:
            if isinstance(item, bool):
                self.setCosmetic(item)
            elif isinstance(item, int):
                self.setStyle(QtCore.Qt.PenStyle(item))
            elif np.iterable(item) and len(item) in (3, 4):
                self.setColor(QtGui.QColor(*item))
            elif isinstance(item, (QtGui.QColor, QtCore.Qt.GlobalColor)):
                self.setColor(item)
            elif isinstance(item, float):
                self.setWidthF(item)
                # print("Pen fails to accept %s." % item)
        self.originalWidth = self.widthF()
        # permet d'eviter au premier appel de self.setBold(False) a la ligne ci-dessous
        self.bold = False

    def __serializejson__(self):
        args = []
        color = self.color().getRgb()
        if color != (0, 0, 0, 255):
            args.append(list(color))
        if self.originalWidth != 1.0:
            args.append(self.originalWidth)
        if self.style() != 1:
            style = self.style()
            try:
                value = style._value_
            except AttributeError:
                value = int(style)
            args.append(value)
            # pour l'instant ne sais pas comment serialiser une enumeration Qt.SolidLine ect...
        if not self.isCosmetic():
            args.append(False)
        return self.__class__, tuple(args)

    def setBold(self, b):
        b = float(b)
        if b != self.bold:
            self.bold = b
            self.setWidthF(self.originalWidth * (1.0 + 2.0 * b))

    def setColor(self, color):
        if np.iterable(color):
            color = QtGui.QColor(*color)
        QtGui.QPen.setColor(self, color)

    def setOppacity(self, oppacity):
        if isinstance(oppacity, float):
            newColor = self.color()
            newColor.setAlphaF(oppacity)
        elif isinstance(oppacity, int):
            newColor = self.color()
            newColor.setAlpha(oppacity)
        else:
            raise Exception("oppacity is not int or float")
        QtGui.QPen.setColor(self, newColor)

    def getOppacity(self):
        return self.color().getRgb()[3]

    oppacity = QtCore.Property(float, getOppacity, setOppacity)
