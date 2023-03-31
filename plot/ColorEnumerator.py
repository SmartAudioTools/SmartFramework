# -*- coding: utf-8 -*-
"""
Created on Thu May 24 18:57:51 2018

@author: Baptiste
"""
from colorsys import hls_to_rgb


class ColorEnumerator:
    def __init__(self):
        self.hueDenominator = 3
        self.hueNumerator = 0
        self.saturation = 1.0
        self.lightness = 0.5
        self.calculatedColors = []

    def getNewColor(self, usedColors=None, printHue=False):

        if usedColors is not None:
            for color in self.calculatedColors:
                if color not in usedColors:
                    return color
        hue = self.hueNumerator / self.hueDenominator
        if printHue:
            print(self.hueNumerator, "/", self.hueDenominator)
        colorFloat = hls_to_rgb(hue, self.lightness, self.saturation)
        if self.hueDenominator > 3:
            self.hueNumerator += 2
        else:
            self.hueNumerator += 1
        if self.hueNumerator >= self.hueDenominator:
            self.hueNumerator = 1
            self.hueDenominator *= 2
        colorInt = tuple([int(f * 255 + 0.499) for f in colorFloat] + [255])
        self.calculatedColors.append(colorInt)
        return colorInt


if __name__ == "__main__":
    # app = QtWidgets.QApplication(sys.argv)
    colorEnumerator = ColorEnumerator()
    colors = [colorEnumerator.getNewColor(printHue=True) for i in range(20)]
    print(colors)
