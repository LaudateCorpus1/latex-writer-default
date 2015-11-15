"""LATEX: HEADER NodeWriter

Writes the headers.

"""

from lexor.core.writer import NodeWriter


class HeaderNW(NodeWriter):
    """Writes a header element. """
    mapping = {
        'h1': 'chapter',
        'h2': 'section',
        'h3': 'subsection',
        'h4': 'subsubsection',
        'h5': 'paragraph',
        'h6': 'subparagraph',
    }
    label = True
    indent = None
    wrap_enabled = None

    def start(self, node):
        self.wrap_enabled = self.writer.wrap_enabled()
        if self.wrap_enabled:
            self.writer.disable_wrap()
        self.writer.endl(False)
        self.writer.endl()
        if self.writer.indent:
            self.indent = self.writer.indent
            self.writer.indent = ''
        self.label = True
        if 'class' in node and 'nolabel' in node['class']:
            self.label = False
        self.write('\\%s' % self.mapping[node.name])
        if not self.label:
            self.write('*')
        if 'alt' in node:
            self.write('[%s]' % node['alt'])
        self.write('{')

    def end(self, node):
        self.label = True
        if 'class' in node and 'nolabel' in node['class']:
            self.label = False
        self.write('}')
        if 'id' in node and self.label:
            self.write('\\label{%s}' % node['id'])
        self.write('\n\n')
        if self.wrap_enabled:
            self.writer.enable_wrap()
        if self.indent:
            self.writer.indent = self.indent
