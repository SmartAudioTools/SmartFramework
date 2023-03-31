import numpy
from qtpy.QtGui import QImage

gray_table = [(255 << 24) + (g << 16) + (g << 8) + g for g in range(256)]


def numpy2qimage(array, QFormat=None, alpha=255, color_table=gray_table):
    """
    Transform numpy array into QImage.
    Data copy is avoided if possible.
    The QImage.data attribute contain the underlying numpy array
    to prevent python freeing that memory while the image is in use.
    (same or a copy of the given array, if copy was needed )
    """
    if numpy.ndim(array) == 2:
        h, w = array.shape
        if (QFormat is None) or (
            QFormat is QImage.Format_Indexed8
        ):  # lent pour affichage sur QWidget par contre rapide pour QGlWidget
            img = QImage(
                numpy.require(array, numpy.uint8, "C").data,
                w,
                h,
                QImage.Format_Indexed8,
            )
            img.setColorTable(color_table)
            img.data = array
            return img
        elif QFormat is QImage.Format_RGB32:
            # 0.7 a 0.9 msec (65793    = (1<<16)+(1<<8)+1)
            bgrx = numpy.require(array * 65793, numpy.uint32, "C")
            img = QImage(bgrx.data, w, h, QImage.Format_RGB32)
            # permet de garder un reference de l'image et lui eviter un destruction qui fait planter PySide2
            img.data = bgrx
            return img
        elif QFormat is QImage.Format_ARGB32:
            bgra = numpy.empty((h, w, 4), numpy.uint8, "C")  # 0.01 mec
            bgra[..., 0] = array
            bgra[..., 1] = array  # 0.38 msec
            bgra[..., 2] = array
            bgra[..., 3] = alpha
            img = QImage(bgra.data, w, h, QImage.Format_ARGB32)
            img.data = bgra
            return img
        elif QFormat is QImage.Format_ARGB32_Premultiplied:
            bgra = numpy.empty((h, w, 4), numpy.uint8, "C")  # 0.01 mec
            array = array * (alpha / 255)
            bgra[..., 0] = array
            bgra[..., 1] = array  # 0.38 msec
            bgra[..., 2] = array
            bgra[..., 3] = alpha
            img = QImage(bgra.data, w, h, QImage.Format_ARGB32_Premultiplied)
            img.data = bgra
            return img

    elif numpy.ndim(array) == 3:
        h, w, channels = array.shape
        if channels == 3:
            bgrx = numpy.empty((h, w, 4), numpy.uint8, "C")
            bgrx[..., :3] = array
            img = QImage(bgrx.data, w, h, QImage.Format_RGB32)
            img.data = bgrx
            return img
        elif channels == 4:
            bgrx = numpy.require(array, numpy.uint8, "C")
            img = QImage(bgrx.data, w, h, QImage.Format_ARGB32)
            img.data = bgrx
            return img
        else:
            raise ValueError(
                "Color images can expects the last dimension to contain exactly three (R,G,B) or four (R,G,B,A) channels"
            )
    else:
        raise ValueError("can only convert 2D or 3D arrays")
