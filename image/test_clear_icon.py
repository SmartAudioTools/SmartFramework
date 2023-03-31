import sys
import cv2
import numpy
import math
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.image.ImageShowUI import ImageShowUI

app = QtWidgets.QApplication(
    sys.argv,
)
path = "D:/Projets/Python/SmartFramework/designer/plugins/MidiOut.png"
image_RGBA = cv2.imread(path, cv2.IMREAD_UNCHANGED)
alpha_normalized = image_RGBA[:, :, 3] / 255
image_RGB = (
    255 * (1 - alpha_normalized)[..., numpy.newaxis]
    + image_RGBA[:, :, :3] * alpha_normalized[..., numpy.newaxis]
)
image = image_RGB.mean(axis=2)
factor = 1 / 15
image_shape = numpy.array(image.shape)
new_shape = numpy.round(image_shape * factor).astype(int)
classic_resampling = cv2.resize(image, new_shape, interpolation=cv2.INTER_AREA).astype(
    numpy.uint8
)
classic_resampling_RGB = numpy.repeat(classic_resampling[:, :, None], 3, axis=2)
resampling_x_3 = cv2.resize(
    image, [new_shape[0] * 3, new_shape[1]], interpolation=cv2.INTER_AREA
).astype(numpy.uint8)
clear_ressampling_BGR = resampling_x_3.reshape(*new_shape, 3)
clear_ressampling_RGB = clear_ressampling_BGR[..., ::-1]
new_image = numpy.concatenate(
    (classic_resampling_RGB, clear_ressampling_RGB, clear_ressampling_BGR)
)
widget = ImageShowUI(noSystemBackground=False, autoRescale=False, smooth=False)
widget.inImage(new_image)
widget.show()
app.exec_()
