#!/usr/bin/env python

# Copyright Louis Paternault 2015
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 1

"""List all python modules available to python."""

import logging
import os
import pkgutil
import sys
import types

LOGGER = logging.getLogger()
LOGGER.addHandler(logging.StreamHandler())

__version__ = "0.1.1"

VERSION_NAMES = [
    "version",
    "Version",
    "VERSION",
    "__version__",
    "__Version__",
    "__VERSION__",
    ]

def get_version(module):
    """Guess the version of argument, and returns it, as a string."""
    candidates = [getattr(module, attr) for attr in VERSION_NAMES if hasattr(module, attr)]
    while candidates:
        first = candidates.pop()
        if callable(first):
            return str(first())
        elif isinstance(first, types.ModuleType):
            candidates.extend([
                getattr(first, attr) for attr in VERSION_NAMES if hasattr(first, attr)
                ])
        else:
            return str(first)
    return ""

def module_list():
    """Yield the list of modules (with version and path)."""
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
        except BaseException as error: # pylint: disable=broad-except
            LOGGER.warning("Error while importing {}: {}.".format(name, error))

if __name__ == "__main__":
    for package, version, path in module_list():
        print("{}\t{}\t{}".format(package, version, path))
