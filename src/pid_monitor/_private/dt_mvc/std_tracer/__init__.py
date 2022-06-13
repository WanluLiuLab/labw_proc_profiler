"""
std_tracer -- All standard tracers

This Python file encodes all standard tracers,
which only depends on psutil or UNIX ProcFS.

Other tracers that may depend on third-party libraries or software is located in other files
under :py:mod:`additional_tracer`.
"""
import importlib
import os
import pkgutil

for module_info in pkgutil.iter_modules([os.path.dirname(__file__)]):
    mod_fullname = f"{__name__}.{module_info.name}"
    mod = importlib.import_module(mod_fullname)
    for names_in_all in mod.__all__:
        globals()[names_in_all] = getattr(mod, names_in_all)
