import PIL.Image
from . import Win32IconImagePlugin

ico = PIL.Image.open("3stars.ico")
print(ico.size)
ico.show()
# OS dependent display of 256x256 PNG image from ico resource
print(ico.info["sizes"])
ico.size = (16, 16)
ico.show()

# OS dependent display of 16x16 DIB image from ico resource
# flipped = ico.transpose(PIL.Image.FLIP_TOP_BOTTOM)
# flipped.show()
