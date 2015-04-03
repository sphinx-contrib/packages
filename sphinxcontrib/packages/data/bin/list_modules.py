#!/usr/bin/env python

import types
import pkgutil
import sys
import os

VERSION = [
        "version",
        "Version",
        "VERSION",
        "__version__",
        "__Version__",
        "__VERSION__",
        ]

def get_version(module):
    candidates = [getattr(module, attr) for attr in VERSION if hasattr(module, attr)]
    while candidates:
        first = candidates.pop()
        if callable(first):
            return str(first())
        elif type(first) == types.ModuleType:
            candidates.extend([
                getattr(first, attr) for attr in VERSION if hasattr(first, attr)
                ])
        else:
            return str(first)
    return ""

def module_list():
    while True:
        try:
            sys.path.remove(os.getcwd())
        except ValueError:
            break

    for __importer, name, __ignored in pkgutil.iter_modules():
        if name.startswith("_"):
            continue
        try:
            module = __import__(name)
            yield name, get_version(module), module.__file__
        except:
            pass

if __name__ == "__main__":
    for name, version, path in module_list():
        print("{}\t{}\t{}".format(name, version, path))
