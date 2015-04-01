# TODO Licence etc.

import collections
import os
import platform
import re
import subprocess

from docutils import nodes
from docutils.statemachine import StringList
from docutils.parsers.rst.directives import flag, unchanged
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles

def simpletable(ncolumns, headers, body):
    def _build_table_row(data):
        row = nodes.row()
        for cell in data:
            entry = nodes.entry()
            row += entry
            entry.append(cell)
        return row

    table = nodes.table()
    tgroup = nodes.tgroup(cols=2)
    table += tgroup
    for colwidth in [10]*ncolumns:
        colspec = nodes.colspec(colwidth = colwidth)
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

def bullet_list(items):
    return nodes.bullet_list("", *[nodes.list_item('', item) for item in items])

class PlatformDirective(Directive):
    has_content = False

    def body(self):
        for attr in [
                "machine",
                "platform",
                "system",
                "release",
                "version",
                "processor",
                ]:
            yield [
                    nodes.paragraph(text=text)
                    for text
                    in [attr.replace("_", " ").capitalize(), str(getattr(platform, attr)())]
                    ]

        for attr in [
                "architecture",
                "linux_distribution",
                ]:
            yield [
                    nodes.paragraph(text=text)
                    for text
                    in [attr.replace("_", " ").capitalize(), " ".join([str(item) for item in getattr(platform, attr)()])]
                    ]

    def run(self):
        return [simpletable(
            2,
            [],
            self.body(),
            )]

class BinDirective(Directive):

    def dirs(self):
        for path in os.getenv("PATH").split(":"):
            binaries = []
            for binary in sorted(os.listdir(os.path.expanduser(os.path.expandvars(path)))):
                if os.path.isfile(os.path.join(path, binary)) and os.access(os.path.join(path, binary), os.X_OK):
                    binaries.append(binary)
            yield (path, binaries)

    def run(self):
        items = []
        for path, binaries in self.dirs():
            item = nodes.compound()
            item.append(nodes.literal(text=path))
            cells = []
            for binary in binaries:
                cells.append([nodes.paragraph(text=binary)])
            if cells:
                item.append(simpletable(
                    1,
                    [],
                    cells,
                    ))
            else:
                item.append(nodes.emphasis(text="empty"))
            items.append(item)
        return [bullet_list(items)]

def deepdict_factory(depth):
    """TODO

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
        def deep_dict():
            return collections.defaultdict(deepdict_factory(depth - 1))
        return deep_dict

class CmdDirective(Directive):
    regexp = ""
    command = []
    headers = {}
    sections = []

    def filter_match(self, match):
        return match

    def _iter_match(self, output):
        compiled_re = re.compile(self.regexp)
        for line in output:
            match = compiled_re.match(line)
            if match:
                processed_match = self.filter_match(match.groupdict())
                if processed_match is not None:
                    yield processed_match

    def _render_deepdict(self, deepdict):
        if type(deepdict) == list:
            return simpletable(
                    len(self.headers),
                    [nodes.paragraph(text=value) for value in self.headers.values()],
                    [
                        [nodes.paragraph(text=item[key]) for key in self.headers]
                        for item
                        in deepdict
                        ]
                    )
        else:
            return TODO_RECURSIVE_LISTE_SORTED(deepdict)

    def run(self):
        process = subprocess.Popen(
                self.command,
                stdin=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                universal_newlines=True,
                )
        deepdict = deepdict_factory(len(self.sections))()
        for match in self._iter_match(process.stdout):
            subdict = deepdict
            for section in self.sections:
                subdict = subdict[section]
            subdict.append(match)
        process.wait()

        return [self._render_deepdict(deepdict)]

class DebDirective(CmdDirective):

    regexp = r'\t'.join([r'(?P<{}>[^\t]*)'.format(key) for key in ['status', 'section', 'package', 'version', 'homepage', 'summary']])
    command = [
        "dpkg-query",
        "--show",
        "--showformat='${db:Status-Status}\t${Section}\t${binary:Package}\t${Version}\t${Homepage}\t${binary:Summary}\n'",
        ]
    headers = collections.OrderedDict([
            ("package", "Package name"),
            ("version", "Version"),
            ("summary", "Summary"),
            ])
    #sections = ["section"] TODO
    # TODO Make name a link to homepage


    def filter(self, match):
        if match['status'] == "ii":
            return match
        else:
            return None


def setup(app):
    app.add_directive('packages:platform', PlatformDirective)
    app.add_directive('packages:bin', BinDirective)
    app.add_directive('packages:deb', DebDirective)

# * Get list of installed C modules::
# 
#     /sbin/ldconfig -p
# 
# * Get list of installed python packages::
# 
#     import pkgutil
#     pkgutil.iter_modules()
# 
