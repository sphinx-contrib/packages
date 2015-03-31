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

    def filter_match(self, match):
        return match

    def run(self):
        compiled_re = re.compile(self.regexp)
        TODO

class DebDirective(CmdDirective):

    regexp = r'\t'.join([r'(P<{}>[^\t]*)'.format(key) for key in ['status', 'section', 'package', 'version', 'homepage', 'summary']])
    command = [
        "dpkg-query",
        "--show",
        "--showformat='${db:Status-Status}\t${Section}\t${binary:Package}\t${Version}\t${Homepage}\t${binary:Summary}\n'",
        ]
    headers = collections.OrderedDict([
            "package": "Name",
            "version": "Version",
            "summary": "Summary",
            "homepage": "Home page",
            ])
    sections = ["section"]


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
