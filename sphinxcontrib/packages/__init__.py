# TODO Licence etc.

import os
import platform

from docutils import nodes
from docutils.statemachine import StringList
from docutils.parsers.rst.directives import flag, unchanged
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles

class SimpleTable(Directive):
    has_content = False
    has_headers = False

    @property
    def ncolumns(self):
        raise NotImplementedError()

    def headers(self):
        return []

    def body(self):
        return [[]]

    def _build_table_row(self, data):
        row = nodes.row()
        for cell in data:
            entry = nodes.entry()
            row += entry
            entry.append(nodes.paragraph(text=cell))
        return row

    def run(self):
        table = nodes.table()
        tgroup = nodes.tgroup(cols=2)
        table += tgroup
        for colwidth in [10]*self.ncolumns:
            colspec = nodes.colspec(colwidth = colwidth)
            tgroup += colspec

        # HEAD
        thead = nodes.thead()
        tgroup += thead
        for row in [self.headers()]:
            thead += self._build_table_row(row)

        # BODY
        tbody = nodes.tbody()
        tgroup += tbody
        for row in self.body():
            tbody += self._build_table_row(row)

        return [table]


class PlatformDirective(SimpleTable):
    has_headers = False

    @property
    def ncolumns(self):
        return 2

    def body(self):
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
            yield [attr.replace("_", " ").capitalize(), " ".join([str(item) for item in getattr(platform, attr)()])]



def setup(app):
    app.add_directive('packages:platform', PlatformDirective)

# * Get list of deb packages::
# 
#     dpkg-query --show --showformat='${db:Status-Status} ${binary:Package} ${Homepage} ${Section} ${Version} ${binary:Summary}\n'
# 
# * Get list of installed binaries:
# 
#   Iterate over executable files in path.
# 
# * Get list of installed C modules::
# 
#     /sbin/ldconfig -p
# 
# * Get list of installed python packages::
# 
#     import pkgutil
#     pkgutil.iter_modules()
# 
