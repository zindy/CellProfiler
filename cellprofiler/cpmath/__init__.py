import inspect
import importlib
import sys
import warnings
from exceptions import DeprecationWarning
warnings.warn(
    "This package is deprecated, please use centrosome instead",
    DeprecationWarning)

def bind_members(full_module_name):
    '''Bind the members of centrosome's version of a module
    
    module_function - determine the module to bind by inspecting this function
    '''
    module = sys.modules[full_module_name]
    module_name = full_module_name.rsplit(".")[-1]
    warnings.warn(
        "This package is deprecated, please use centrosome.%s instead" % 
        module_name,
        DeprecationWarning, stacklevel=2)
    src_module = importlib.import_module('centrosome.'+module_name)
    for name, value in inspect.getmembers(src_module):
        if inspect.getmodule(value) in (None, src_module):
            setattr(module, name, value)
