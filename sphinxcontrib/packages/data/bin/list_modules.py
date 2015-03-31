#!/usr/bin/env python

# TODO
# Make a main() function
# Make it work with both python2 and python3

import types
import pkgutil
import sys
import os

while True:
    try:
        sys.path.remove(os.getcwd())
    except ValueError:
        break

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

for __importer, name, __ignored in pkgutil.iter_modules():
    if name.startswith("_"):
        continue
    try:
        module = __import__(name)
        print("{}\t{}".format(name, get_version(module)))
    except:
        pass
