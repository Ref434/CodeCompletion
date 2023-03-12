import importlib
import sys
import json
from sklearn import *
import numpy
from inspect import getmembers, isfunction


def get_methods(object, name_of_class, spacing=20):
    methodList = []
    for method_name in dir(object):
        try:
            if callable(getattr(object, method_name)):
                str = name_of_class + method_name
                methodList.append(str)
        except Exception:
            str = name_of_class + method_name
            methodList.append(str)

    description_method = {}
    for method in methodList:
        try:
            all_doc = eval(method).__doc__
            description_method[method.split(".")[1]] = all_doc.partition('\n')[0]
        except Exception:
            continue

    return description_method

def isModuleExist(name):
    if importlib.util.find_spec(name) is not None:
        return True
    else:
        print(f"can't find the {name!r} module")
        return False

def getModule(name):
    spec = importlib.util.find_spec(name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def writeData(name_of_file, data):
    with open(f'{name_of_file}.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

if __name__ == "__main__":
    print(dir(numpy))
    # name = 'numpy'
    # data = {}
    # if isModuleExist(name):
    #     module = getModule(name)
    #     all_module = module.__all__
    #     for module_class in all_module:
    #         data[module_class] = get_methods(eval(str(module_class)), str(module_class) + '.')
    #
    # writeData(name, data)

