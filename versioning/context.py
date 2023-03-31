import sys
import os
import subprocess

black_list = {

    'QtCore',  # ajouté par SmartFramework/serialize/pluginsserializejson_PyQt5_PySide2.py
    'QtGui',  # ajouté par SmartFramework/serialize/pluginsserializejson_PyQt5_PySide2.py
    'QtWidgets',  # ajouté par SmartFramework/serialize/pluginsserializejson_PyQt5_PySide2.py
    'IPython',
    'PIL',
    #'PyQt5',
    '__main__',
    '__mp_main__',
    '_distutils_hack',
    '_pydev_bundle',
    '_pydev_runfiles',
    '_pydevd_bundle',
    '_pydevd_frame_eval',
    '_win32sysloader',
    'atomicwrites',
    'autoreload',
    'backcall',
    'bs4',
    'cchardet',
    'cffi',
    'chardet',
    'cloudpickle',
    'colorama',
    'cycler',
    'dateutil',
    'debugpy',
    'decorator',
    'defusedxml',
    'distutils',
    'entrypoints',
    'ipykernel',
    'jedi',
    'jupyter_client',
    'jupyter_core',
    'kiwisolver',
    'lxml',
    'matplotlib',
    'matplotlib_inline',
    'ntsecuritycon',
    #'numexpr',
    #'numpy',
    'packaging',
    'pandas',
    'parso',
    'pickleshare',
    'pkg_resources',
    'prompt_toolkit',
    'psutil',
    'pydev_ipython',
    'pydevconsole',
    'pydevd',
    'pydevd_file_utils',
    'pydevd_plugins',
    'pydevd_tracing',
    'pygments',
    'pyparsing',
    'pythoncom',
    'pytz',
    'pywin32_bootstrap',
    'pywintypes',
    'setuptools',
    'sip',
    'six',
    'soupsieve',
    'spyder',
    'spyder_kernels',
    'spydercustomize',
    'storemagic',
    'tornado',
    'traitlets',
    'typing_extensions',
    'wcwidth',
    'win32api',
    'win32com',
    'win32security',
    'zmq'}


def get_context():

    paths = (os.path.abspath(p) for p in sys.path)
    stdlib = {p for p in paths
              if p.startswith(sys.prefix)
              and 'site-packages' not in p}
    for lib in list(stdlib):
        if lib.endswith('lib'):
            stdlib.add(lib+'\\importlib')
            stdlib.add(lib+'/importlib')

    loaded_package_versions = dict()
    loaded_repository = dict()
    for name, module in sorted(sys.modules.items()):

        if '.' in name:
            continue

        if not module:
            continue

        if name in sys.builtin_module_names:
            continue

        if not hasattr(module, '__file__'):
            continue

        path = module.__file__
        if path is None:
            continue
        if path.endswith(('__init__.py', '__init__.pyc', '__init__.pyo')):
            path = os.path.dirname(path)
        if os.path.dirname(path) in stdlib:
            continue

        if name in black_list:
            continue
        if hasattr(module, "__version__"):
            loaded_package_versions[name] = module.__version__
            continue

        if name == "PyQt5":
            loaded_package_versions[name] = module.QtCore.PYQT_VERSION_STR
            continue

        if os.path.exists(f"{path}/.hg"):
            hg_revision_id = subprocess.check_output(
                ("hg", "id", "--id"), cwd=path).strip().decode("cp1252")
            if hg_revision_id.endswith("+"):
                hg_diff = subprocess.check_output(
                    ("hg", "diff"), cwd=path).strip().decode("cp1252").replace('\r', '')
                loaded_repository[name] = [hg_revision_id, hg_diff]
            else:
                loaded_repository[name] = hg_revision_id

            continue

        print(f"no version for {name}")

        """splited = path.replace('\\','/').split('/')
        while splited : 
            test_directory = "/".join(splited)
            #print(test_directory)
            if os.path.exists(f"{test_directory}/.hg"):
                repository_name = os.path.split(test_directory)[1]
                if repository_name not in loaded_repository:
                    hg_revision_id = subprocess.check_output(
                        ("hg", "id", "--id"), cwd=test_directory).strip().decode("cp1252")
                    if hg_revision_id.endswith("+"):
                        hg_diff = subprocess.check_output(
                            ("hg", "diff"), cwd=test_directory).strip().decode("cp1252").replace('\r', '')
                        loaded_repository[repository_name] = [ hg_revision_id , hg_diff]
                    else :                    
                        loaded_repository[repository_name] = hg_revision_id
                break
            splited.pop(-1)
        else : 
            print(f"no version for {name}")
        """

    loaded_repository.update(loaded_package_versions)
    return loaded_repository
    #print(loaded_repository)
    #print(dumps(loaded_repository))
