#!/usr/bin/env python

# TODO
# Make a main() function
# Make it work with both python2 and python3

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

for __importer, name, __ignored in pkgutil.iter_modules():
    try:
        module = __import__(name)
        version = None
        for attr in VERSION:
            if hasattr(module, attr):
                version = getattr(module, attr)
                if callable(version):
                    version = version()
        if version is None:
            print(name)
        else:
            print(name, version)
    except:
        pass
