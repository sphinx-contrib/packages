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

"""This is a sphinx extension providing some directives to show system information.

Its main purpose is to display a list of tools available on readthedocs:
http://packages.readthedocs.org
"""

import collections
import os
import pkg_resources
import platform
import re
import subprocess

from docutils import nodes
from docutils.statemachine import StringList
from docutils.parsers.rst.directives import flag, unchanged
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles
from docutils.parsers.rst import directives

__version__ = "0.0.0"

def node_or_str(text):
    """Return argument, converted to a node if necessary."""
    if isinstance(text, str):
        return nodes.paragraph(text=text)
    else:
        return text

def simple_compound(*items):
    """Return a compound node."""
    compound = nodes.compound()
    for item in items:
        compound.append(item)
    return compound

def simple_link(text, target):
    """Returns a link node to `target`, displaying `text`."""
    container = nodes.paragraph()
    reference = nodes.reference("", "", internal=False, refuri=target)
    reference.append(nodes.paragraph(text=text))
    container.append(reference)
    return container


def simple_table(ncolumns, headers, body):
    """Return a table node.

    :param int ncolumns: Number of columns.
    :param list headers: Headers, as a list of nodes (or strings).
    :param list body: Body, as a list of lists of nodes (or strings).
    """
    def _build_table_row(data):
        """Return the node corresponding to a row of the table."""
        row = nodes.row()
        for cell in data:
            entry = nodes.entry()
            row += entry
            entry.append(node_or_str(cell))
        return row

    table = nodes.table()
    tgroup = nodes.tgroup(cols=2)
    table += tgroup
    for colwidth in [10]*ncolumns:
        colspec = nodes.colspec(colwidth=colwidth)
        tgroup += colspec

    # HEAD
    thead = nodes.thead()
    tgroup += thead
    for row in [headers]:
        thead += _build_table_row(row)

    # BODY
    tbody = nodes.tbody()
    tgroup += tbody
    for row in body:
        tbody += _build_table_row(row)

    return table

def simple_bulletlist(items):
    """Return a bullet list nodes of arguments."""
    return nodes.bullet_list("", *[nodes.list_item('', node_or_str(item)) for item in items])

class PlatformDirective(Directive):
    """Print platform information (processors, architecture, etc.)"""
    has_content = False

    @staticmethod
    def body():
        """Iterator to the platform information."""
        for attr in [
                "machine",
                "platform",
                "system",
                "release",
                "version",
                "processor",
            ]:
            yield [attr.replace("_", " ").capitalize(), str(getattr(platform, attr)())]

        for attr in [
                "architecture",
                "linux_distribution",
            ]:
            yield [
                attr.replace("_", " ").capitalize(),
                " ".join([str(item) for item in getattr(platform, attr)()]),
                ]

    def run(self):
        return [simple_table(
            2,
            [],
            self.body(),
            )]

class BinDirective(Directive):
    """Display the list of available binaries."""

    @staticmethod
    def dirs():
        """Iterator over couples `(path, binaries)`.

        - `path` is a path of the ``PATH`` variable;
        - `binaries` is the list of binaries available in this path.
        """
        for path in os.getenv("PATH").split(":"):
            binaries = []
            for binary in sorted(os.listdir(os.path.expanduser(os.path.expandvars(path)))):
                if (
                        os.path.isfile(os.path.join(path, binary))
                        and
                        os.access(os.path.join(path, binary), os.X_OK)
                    ):
                    binaries.append(binary)
            yield (path, binaries)

    def run(self):
        items = []
        for path, binaries in self.dirs():
            item = simple_compound(nodes.literal(text=path))
            cells = []
            for binary in binaries:
                cells.append([nodes.paragraph(text=binary)])
            if cells:
                item.append(simple_table(
                    1,
                    [],
                    cells,
                    ))
            else:
                item.append(nodes.emphasis(text="empty"))
            items.append(item)
        return [simple_bulletlist(items)]

def deepdict_factory(depth):
    """Return a dict of dicts of dicts of ... of dicts of lists.

    The dicts are :class:`collections.defaultdict`.

    >>> d = deepdict_factory(2)()
    >>> type(d)
    <class 'collections.defaultdict'>
    >>> type(d[0])
    <class 'collections.defaultdict'>
    >>> type(d[0]["foo"])
    <class 'list'>
    """
    if depth == 0:
        return list
    else:
        def deepdict():
            """Return a deepdict, less deep than the current one."""
            return collections.defaultdict(deepdict_factory(depth - 1))
        return deepdict

class CmdDirective(Directive):
    """Abstract directive that executes a command, and return its output as array(s).
    """
    command = []
    regexp = ""
    headers = {}
    sections = []
    sortkey = None

    def filter(self, match): # pylint: disable=no-self-use
        """Perform some post-processing on matched lines.

        Returns a list of matched lines (which can be empty to discard
        argument).
        This function is to be overloaded, if necessary, by subclasses.
        """
        return [match]

    def _iter_match(self, output):
        """Iterator over matched lines of the output."""
        compiled_re = re.compile(self.regexp)
        for line in output:
            match = compiled_re.match(line.decode("utf8").strip())
            if match:
                yield from self.filter(match.groupdict())

    def _render_deepdict(self, deepdict):
        """Render a :class:`deepdict`.

        - If it is a deepdict, render it a bullet list of :class:`deepdict`;
        - if it is a list, render it as a table.
        """
        if isinstance(deepdict, list):
            items = dict()
            for item in deepdict:
                items[item[self.sortkey]] = [item[key] for key in self.headers]
            return simple_table(
                len(self.headers),
                self.headers.values(),
                [items[key] for key in sorted(items.keys())],
                )
        else:
            return simple_bulletlist([
                simple_compound(
                    nodes.paragraph(text=key),
                    self._render_deepdict(deepdict[key])
                    )
                for key
                in sorted(deepdict)
                ])

    def run(self):
        try:
            process = subprocess.Popen(
                self.command,
                stdin=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                )
            deepdict = deepdict_factory(len(self.sections))()
            for match in self._iter_match(process.stdout):
                subdict = deepdict
                for section in self.sections:
                    subdict = subdict[match[section]]
                subdict.append(match)
            process.wait()
        except FileNotFoundError as exception:
            error = nodes.error()
            error.append(nodes.paragraph(text=str(exception)))
            return [error]

        return [self._render_deepdict(deepdict)]

class DebDirective(CmdDirective):
    """Display the list of installed debian packages"""

    regexp = r'\t'.join([
        r'(?P<{}>[^\t]*)'.format(key)
        for key
        in ['status', 'section', 'package', 'version', 'homepage', 'summary']
        ])
    command = [
        "dpkg-query",
        "--show",
        "--showformat=${db:Status-Status}\t${Section}\t${binary:Package}\t${Version}\t${Homepage}\t${binary:Summary}\n", # pylint: disable=line-too-long
        ]
    headers = collections.OrderedDict([
        ("package_node", "Package name"),
        ("version", "Version"),
        ("summary", "Summary"),
        ])
    sortkey = "package"
    sections = ["section"]

    def filter(self, match):
        if match['status'] == "installed":
            if match['homepage']:
                match['package_node'] = simple_link(text=match['package'], target=match['homepage'])
            else:
                match['package_node'] = match['package']
            return [match]
        return []

class PyDirective(CmdDirective):
    """Abstract class to display available python modules."""

    regexp = r'\t'.join([r'(?P<{}>[^\t]*)'.format(key) for key in ['package', 'version', 'path']])
    headers = collections.OrderedDict([
        ("package", "Package name"),
        ("version", "Version"),
        ])
    sortkey = "package"
    python = ""

    def filter(self, match):
        if match['path'].startswith(pkg_resources.resource_filename(__name__, "data")):
            return []
        return [match]

    @property
    def command(self):
        """Return the command to perform to list modules."""
        return [
            self.python,
            pkg_resources.resource_filename(
                __name__,
                os.path.join("data", "bin", "list_modules.py"),
                ),
            ]

class Py3Directive(PyDirective):
    """Display available python3 modules."""

    python = "python3"

class Py2Directive(PyDirective):
    """Display available python2 modules."""

    python = "python2"

class CDirective(CmdDirective):
    """Display available C libraries."""

    regexp = r'^ *(?P<library>[^ ]*) '
    headers = collections.OrderedDict([
        ("library", "Library"),
        ])
    command = ["/sbin/ldconfig", "-p"]
    sortkey = "library"

def setup(app):
    """Register directives."""
    app.add_directive('packages:platform', PlatformDirective)
    app.add_directive('packages:bin', BinDirective)
    app.add_directive('packages:deb', DebDirective)
    app.add_directive('packages:python2', Py2Directive)
    app.add_directive('packages:python3', Py3Directive)
    app.add_directive('packages:c', CDirective)

