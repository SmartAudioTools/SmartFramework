#
# Copyright Â© 2009- The Spyder Development Team
# Copyright Â© 2014-2015 Colin Duquesnoy
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
**QtPy** is a shim over the various Python Qt bindings. It is used to write
Qt binding independent libraries or applications.

If one of the APIs has already been imported, then it will be used.

Otherwise, the shim will automatically select the first available API (PyQt5, PySide2,
PyQt6 and PySide6); in that case, you can force the use of one
specific bindings (e.g. if your application is using one specific bindings and
you need to use library that use QtPy) by setting up the ``QT_API`` environment
variable.

PyQt5
=====

For PyQt5, you don't have to set anything as it will be used automatically::

    >>> from qtpy import QtGui, QtWidgets, QtCore
    >>> print(QtWidgets.QWidget)

PySide2
======

Set the QT_API environment variable to 'pyside2' before importing other
packages::

    >>> import os
    >>> os.environ['QT_API'] = 'pyside2'
    >>> from qtpy import QtGui, QtWidgets, QtCore
    >>> print(QtWidgets.QWidget)

PyQt6
=====

    >>> import os
    >>> os.environ['QT_API'] = 'pyqt6'
    >>> from qtpy import QtGui, QtWidgets, QtCore
    >>> print(QtWidgets.QWidget)

PySide6
=======

    >>> import os
    >>> os.environ['QT_API'] = 'pyside6'
    >>> from qtpy import QtGui, QtWidgets, QtCore
    >>> print(QtWidgets.QWidget)

"""

from packaging.version import parse
import os
import platform
import sys
import warnings
import importlib  # import ctypes
import ctypes


try:
    from nt import environ as environ_nt

    orignal_environ = {key.upper(): value for key, value in environ_nt.items()}
except:
    from nt import environ as environ_posix

    encoding = sys.getfilesystemencoding()
    orignal_environ = {
        key.encode(encoding, "surrogateescape"): value.decode(
            encoding, "surrogateescape"
        )
        for key, value in environ_posix.items()
    }
try:
    import winreg

    python_redefined_keys = set()
    for key, value in os.environ.items():
        if orignal_environ.get(key) != value:
            python_redefined_keys.add(key)

    def get_env(key, default=None):
        if key in python_redefined_keys:
            return os.environ.get(key, default)
        for reg_key in (
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Environment"),
            winreg.CreateKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"System\CurrentControlSet\Control\Session Manager\Environment",
            ),
        ):
            try:
                return winreg.QueryValueEx(reg_key, key)[0]
            except FileNotFoundError:
                pass
        return os.environ.get(key, default)  # utuile ?

except:

    def get_env(key, default=None):
        return os.environ.get(key, default)


# force process to be DPI Aware avoiding Window scalinf with blur with Qt6
# as the same effect than change pythonw.exe property to DPI Aware
try:  # >= win 8.1
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:  # win 8.0 or less
    ctypes.windll.user32.SetProcessDPIAware()


QT_SCALE = get_env("QT_SCALE", "false").lower()
if QT_SCALE == "default":
    pass
elif QT_SCALE == "off":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_USE_PHYSICAL_DPI"] = "1"
elif QT_SCALE == "on":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_USE_PHYSICAL_DPI"] = "0"
elif QT_SCALE.isdigit():
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_USE_PHYSICAL_DPI"] = "0"
    os.environ["QT_SCALE_FACTOR"] = QT_SCALE
else:
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_USE_PHYSICAL_DPI"] = "0"
    os.environ["QT_SCREEN_SCALE_FACTORS"] = QT_SCALE

QT_DEFAULT_FONT_SIZE = get_env("QT_DEFAULT_FONT_SIZE", "none").lower()


# Version of QtPy
__version__ = "2.2.0.dev0"


class PythonQtError(RuntimeError):
    """Error raised if no bindings could be selected."""


class PythonQtWarning(Warning):
    """Warning if some features are not implemented in a binding."""


class PythonQtValueError(ValueError):
    """Error raised if an invalid QT_API is specified."""


# Qt API environment variable name
QT_API = "QT_API"

# Names of the expected PyQt5 api
PYQT5_API = ["pyqt5"]

PYQT6_API = ["pyqt6"]

# Names of the expected PySide2 api
PYSIDE2_API = ["pyside2"]

# Names of the expected PySide6 api
PYSIDE6_API = ["pyside6"]

# Minimum supported versions of Qt and the bindings
QT5_VERSION_MIN = PYQT5_VERSION_MIN = "5.9.0"
PYSIDE2_VERSION_MIN = "5.12.0"
QT6_VERSION_MIN = PYQT6_VERSION_MIN = PYSIDE6_VERSION_MIN = "6.2.0"

QT_VERSION_MIN = QT5_VERSION_MIN
PYQT_VERSION_MIN = PYQT5_VERSION_MIN
PYSIDE_VERSION_MIN = PYSIDE2_VERSION_MIN

# Detecting if a binding was specified by the user
binding_specified = QT_API in os.environ

API_NAMES = {
    "pyqt5": "PyQt5",
    "pyside2": "PySide2",
    "pyqt6": "PyQt6",
    "pyside6": "PySide6",
}
API = get_env(
    QT_API, "auto"
).lower()  # allow to change API without restarting Spyder on Windows

if API == "auto":
    for key, value in API_NAMES.items():
        if value in sys.modules:
            API = key
    else:
        for module in ("PyQt5", "PySide2", "PyQt6", "PySide6"):
            if importlib.util.find_spec(module) is not None:
                API = module.lower()
                break

initial_api = API
if API not in API_NAMES:
    raise PythonQtValueError(
        f"Specified QT_API={repr(QT_API.lower())} is not in valid options: "
        f"{API_NAMES}"
    )

is_old_pyqt = is_pyqt46 = False
QT5 = PYQT5 = True
QT4 = QT6 = PYQT4 = PYQT6 = PYSIDE = PYSIDE2 = PYSIDE6 = False

PYQT_VERSION = None
PYSIDE_VERSION = None
QT_VERSION = None

# Unless `FORCE_QT_API` is set, use previously imported Qt Python bindings
# FORCE_QT_API = get_env('FORCE_QT_API','').lower()
if os.path.split(sys.argv[0])[1] == "spyder":
    API = "pyqt5"
# elif FORCE_QT_API :
#    if FORCE_QT_API in API_NAMES :
#        API = FORCE_QT_API
# else :  # spyder lunch new script with PyQt5 already in os.modules... how to avoid it ?
#    if 'PyQt5' in sys.modules:
#        API = initial_api if initial_api in PYQT5_API else 'pyqt5'
#    elif 'PySide2' in sys.modules:
#        API = initial_api if initial_api in PYSIDE2_API else 'pyside2'
#    elif 'PyQt6' in sys.modules:
#        API = initial_api if initial_api in PYQT6_API else 'pyqt6'
#    elif 'PySide6' in sys.modules:
#        API = initial_api if initial_api in PYSIDE6_API else 'pyside6'

if API in PYQT5_API:
    try:
        from PyQt5.QtCore import PYQT_VERSION_STR as PYQT_VERSION  # analysis:ignore
        from PyQt5.QtCore import QT_VERSION_STR as QT_VERSION  # analysis:ignore

        QT5 = PYQT5 = True

        if sys.platform == "darwin":
            macos_version = parse(platform.mac_ver()[0])
            if macos_version < parse("10.10"):
                if parse(QT_VERSION) >= parse("5.9"):
                    raise PythonQtError(
                        "Qt 5.9 or higher only works in "
                        "macOS 10.10 or higher. Your "
                        "program will fail in this "
                        "system."
                    )
            elif macos_version < parse("10.11"):
                if parse(QT_VERSION) >= parse("5.11"):
                    raise PythonQtError(
                        "Qt 5.11 or higher only works in "
                        "macOS 10.11 or higher. Your "
                        "program will fail in this "
                        "system."
                    )

            del macos_version
    except ImportError:
        API = "pyside2"
    else:
        os.environ[QT_API] = API

if API in PYSIDE2_API:
    try:
        from PySide2 import __version__ as PYSIDE_VERSION  # analysis:ignore
        from PySide2.QtCore import __version__ as QT_VERSION  # analysis:ignore

        PYQT5 = False
        QT5 = PYSIDE2 = True

        if sys.platform == "darwin":
            macos_version = parse(platform.mac_ver()[0])
            if macos_version < parse("10.11"):
                if parse(QT_VERSION) >= parse("5.11"):
                    raise PythonQtError(
                        "Qt 5.11 or higher only works in "
                        "macOS 10.11 or higher. Your "
                        "program will fail in this "
                        "system."
                    )

            del macos_version
    except ImportError:
        API = "pyqt6"
    else:
        os.environ[QT_API] = API

if API in PYQT6_API:
    try:
        from PyQt6.QtCore import PYQT_VERSION_STR as PYQT_VERSION  # analysis:ignore
        from PyQt6.QtCore import QT_VERSION_STR as QT_VERSION  # analysis:ignore

        QT5 = PYQT5 = False
        QT6 = PYQT6 = True

    except ImportError:
        API = "pyside6"
    else:
        os.environ[QT_API] = API

if API in PYSIDE6_API:
    try:
        from PySide6 import __version__ as PYSIDE_VERSION  # analysis:ignore
        from PySide6.QtCore import __version__ as QT_VERSION  # analysis:ignore

        QT5 = PYQT5 = False
        QT6 = PYSIDE6 = True

    except ImportError:
        API = "pyqt5"
    else:
        os.environ[QT_API] = API


# If a correct API name is passed to QT_API and it could not be found,
# switches to another and informs through the warning
if API != initial_api and binding_specified:
    warnings.warn(
        'Selected binding "{}" could not be found, '
        'using "{}"'.format(initial_api, API),
        RuntimeWarning,
    )


# Set display name of the Qt API
API_NAME = API_NAMES[API]
os.environ["PYQTGRAPH_QT_LIB"] = API_NAME
try:
    # QtDataVisualization backward compatibility (QtDataVisualization vs. QtDatavisualization)
    # Only available for Qt5 bindings > 5.9 on Windows
    from . import QtDataVisualization as QtDatavisualization  # analysis:ignore
except (ImportError, PythonQtError):
    pass


def _warn_old_minor_version(name, old_version, min_version):
    """Warn if using a Qt or binding version no longer supported by QtPy."""
    warning_message = (
        "{name} version {old_version} is not supported by QtPy. "
        "To ensure your application works correctly with QtPy, "
        "please upgrade to {name} {min_version} or later.".format(
            name=name, old_version=old_version, min_version=min_version
        )
    )
    warnings.warn(warning_message, PythonQtWarning)


# Warn if using an End of Life or unsupported Qt API/binding minor version
if QT_VERSION:
    if QT5 and (parse(QT_VERSION) < parse(QT5_VERSION_MIN)):
        _warn_old_minor_version("Qt5", QT_VERSION, QT5_VERSION_MIN)
    elif QT6 and (parse(QT_VERSION) < parse(QT6_VERSION_MIN)):
        _warn_old_minor_version("Qt6", QT_VERSION, QT6_VERSION_MIN)

if PYQT_VERSION:
    if PYQT5 and (parse(PYQT_VERSION) < parse(PYQT5_VERSION_MIN)):
        _warn_old_minor_version("PyQt5", PYQT_VERSION, PYQT5_VERSION_MIN)
    elif PYQT6 and (parse(PYQT_VERSION) < parse(PYQT6_VERSION_MIN)):
        _warn_old_minor_version("PyQt6", PYQT_VERSION, PYQT6_VERSION_MIN)
elif PYSIDE_VERSION:
    if PYSIDE2 and (parse(PYSIDE_VERSION) < parse(PYSIDE2_VERSION_MIN)):
        _warn_old_minor_version("PySide2", PYSIDE_VERSION, PYSIDE2_VERSION_MIN)
    elif PYSIDE6 and (parse(PYSIDE_VERSION) < parse(PYSIDE6_VERSION_MIN)):
        _warn_old_minor_version("PySide6", PYSIDE_VERSION, PYSIDE6_VERSION_MIN)
