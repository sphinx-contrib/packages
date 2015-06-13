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
import glob
import operator
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

__version__ = "0.1.1"

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
    :param list headers: Headers, as a list of nodes (or strings), or ``None``,
        if there is no headers.
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
    if headers is not None:
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

def iter_paths():
    """Iterate over existing paths."""
    for string in os.getenv("PATH").split(":"):
        path = os.path.expanduser(os.path.expandvars(string))
        if os.path.exists(path) and os.path.isdir(path):
            yield path

def python_versions():
    """Iterate over [binary, version] lists of available python executables."""
    binaries = set()
    for path in iter_paths():
        for binary in glob.glob(os.path.join(path, "python*")):
            binaries.add(binary)

    pythonre = re.compile(r".*/python[.0123456789]*$")
    for binary in binaries:
        if pythonre.match(binary):
            try:
                yield [
                    nodes.literal(text=binary),
                    subprocess.check_output(
                        [binary, "--version"],
                        stdin=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                    ).strip(),
                    ]
            except subprocess.CalledProcessError:
                continue

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

class PythonVersionsDirective(Directive):
    """Print list of available python versions"""
    has_content = False

    @staticmethod
    def body():
        """Iterator to the versions."""
        return sorted(
            python_versions(),
            key=operator.itemgetter(1),
            )

    def run(self):
        return [simple_table(
            2,
            ["Binary", "Version"],
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
        for path in iter_paths():
            binaries = []
            for binary in sorted(os.listdir(path)):
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
    regexp = "(?P<line>.*)"
    headers = {}
    sections = []
    sortkey = None
    show_headers = True

    def section_names(self, name): # pylint: disable=no-self-use
        """Return the displayed name corresponding to section ``name``.
        """
        return name

    def filter(self, match): # pylint: disable=no-self-use
        """Perform some post-processing on matched lines, and iterate over result.

        Iterate over resulting objects. In particular, it can iterate zero
        objects (to discard argument), or iterate over several objects (if
        argument corresponds to several objects).

        This function is to be overloaded, if necessary, by subclasses.
        """
        yield match

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
            if self.show_headers:
                headers = self.headers.values()
            else:
                headers = None
            return simple_table(
                len(self.headers),
                headers,
                [items[key] for key in sorted(items.keys())],
                )
        else:
            return simple_bulletlist([
                simple_compound(
                    nodes.paragraph(text=self.section_names(key)),
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

    regexp = 'ii *\t' + r'\t'.join([
        r'(?P<{}>[^\t]*)'.format(key)
        for key
        in ['section', 'package', 'version', 'homepage', 'summary']
        ])
    command = [
        "dpkg-query",
        "--show",
        "--showformat=${db:Status-Abbrev}\t${Section}\t${binary:Package}\t${Version}\t${Homepage}\t${binary:Summary}\n", # pylint: disable=line-too-long
        ]
    headers = collections.OrderedDict([
        ("package_node", "Package name"),
        ("version", "Version"),
        ("summary", "Summary"),
        ])
    sortkey = "package"
    sections = ["section"]

    def filter(self, match):
        if match['homepage']:
            match['package_node'] = simple_link(text=match['package'], target=match['homepage'])
        else:
            match['package_node'] = match['package']
        yield match

class PyDirective(CmdDirective):
    """Abstract class to display available python modules."""

    regexp = r'\t'.join([r'(?P<{}>[^\t]*)'.format(key) for key in ['package', 'version', 'path']])
    headers = collections.OrderedDict([
        ("package", "Package name"),
        ("version", "Version"),
        ])
    sortkey = "package"
    python = "python"

    option_spec = {'bin':directives.unchanged}

    def filter(self, match):
        if os.path.splitext(match['path'])[0] != os.path.splitext(self.command[1])[0]:
            yield match

    @property
    def command(self):
        """Return the command to perform to list modules."""
        if "bin" not in self.options:
            self.options["bin"] = self.python
        return [
            self.options["bin"],
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
    show_headers = False

class LatexDirective(CmdDirective):
    """Display available LaTeX packages."""

    command = ["kpsepath", "tex"]
    sortkey = "package"
    headers = {'package': 'Package'}
    sections = ["type"]
    section_names = {
        "class": "Classes",
        "package": "Packages",
        }.get
    show_headers = False

    @staticmethod
    def _sty_or_cls(file):
        """Check if argument is a package or a class.

        Returns ``"package"`` or ``"class"`` if one of them, ``False``
        otherwise.
        """
        if file.endswith(".sty"):
            return "package"
        elif file.endswith(".cls"):
            return "class"
        else:
            return False

    def _find(self, path):
        """Iterator over .sty and .clsfiles in argument.

        Argument is a string representing a (maybe non-existing) path.
        """
        for __root, __dirs, files in os.walk(path):
            for file in files:
                if self._sty_or_cls(file):
                    yield file

    def filter(self, match):
        for item in match['line'].split(':'):
            if item.startswith("!!"):
                item = item[2:]
            yield from [
                dict([('package', file), ('type', self._sty_or_cls(file))])
                for file
                in self._find(item)
                ]

def setup(app):
    """Register directives."""
    app.add_directive('packages:platform', PlatformDirective)
    app.add_directive('packages:pyversions', PythonVersionsDirective)
    app.add_directive('packages:bin', BinDirective)
    app.add_directive('packages:deb', DebDirective)
    app.add_directive('packages:python', PyDirective)
    app.add_directive('packages:python2', Py2Directive)
    app.add_directive('packages:python3', Py3Directive)
    app.add_directive('packages:c', CDirective)
    app.add_directive('packages:latex', LatexDirective)

