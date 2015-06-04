#!/usr/bin python

# Copyright 2015 Louis Paternault
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Tests"""

import doctest
import pkgutil
import sys

import sphinxcontrib.packages

def load_tests(__loader, tests, __pattern):
    """Load tests (doctests).
    """
    # Loading doctests
    tests.addTests(doctest.DocTestSuite(sphinxcontrib.packages))
    for module_finder, name, __is_pkg in pkgutil.walk_packages(
            sphinxcontrib.packages.__path__,
            prefix="{}.".format(sphinxcontrib.packages.__name__),
        ):
        if name in sys.modules:
            module = sys.modules[name]
        else:
            try:
                module = module_finder.find_spec(name).loader.load_module()
            except ImportError:
                continue
        try:
            tests.addTests(doctest.DocTestSuite(module))
        except ValueError:
            # No docstring, or no doctests in the docstrings
            pass

    return tests
