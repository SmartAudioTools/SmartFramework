import os

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_USE_PHYSICAL_DPI"] = "1"
import sys
from pyqt5_tools.entrypoints import main

if __name__ == "__main__":
    sys.argv = ["qt5-tools", "designer"]
    sys.exit(main())
