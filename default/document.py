"""LATEX: DOCUMENT NodeWriter

Provides several writers for the header and body of the document.

"""

import os
from lexor.core.writer import NodeWriter


def format_attributes(node, exclude=None):
    """Format a node's attribute. """
    if exclude is None:
        exclude = []
    att = []
    for key, val in node.items():
        if key in exclude:
            continue
        if val:
            att.append('%s=%s' % (key, val))
        else:
            att.append(key)
    return ','.join(att)


class DocumentClassNW(NodeWriter):
    """Write the document class. """

    def start(self, node):
        self.write('\\documentclass')
        att = format_attributes(node, 'class')
        if att:
            self.write('[%s]' % att)
        self.write('{%s}' % node['class'])

    def end(self, node):
        self.writer.endl()


class UsePackageNW(NodeWriter):
    """Write the usepackage node. """

    def start(self, node):
        self.writer.endl(False)
        self.write('\\usepackage')
        att = format_attributes(node)
        if att:
            self.write('[%s]' % att)
        self.write('{')
    
    def end(self, node):
        self.write('}')
        self.writer.endl()


class BibliographyNW(NodeWriter):
    """Write the bibliography node. """

    def start(self, node):
        self.writer.endl(False)
        self.write('\\bibliography')
        att = format_attributes(node, ['src', 'rel'])
        if att:
            self.write('[%s]' % att)
        if 'rel' in node:
            self.write('{%s}' % node['rel'])
        else:
            rel = os.path.basename(node['src'])
            rel, ext = os.path.splitext(rel)
            self.write('{%s}' % rel)
        self.writer.endl()
