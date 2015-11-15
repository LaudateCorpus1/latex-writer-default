"""LATEX: LATEX NodeWriter

Writes math mode.

"""

from lexor.core.writer import NodeWriter


class LatexNW(NodeWriter):
    """Write the bibliography node. """

    def start(self, node):
        if node['type'] == 'inline':
            if node['char'] == '$':
                self.write('$')
            else:
                self.write('\\(')
        else:
            if node['char'] == '$$':
                self.write('$$')
            else:
                self.write('\\[')

    def end(self, node):
        if node['type'] == 'inline':
            if node['char'] == '$':
                self.write('$')
            else:
                self.write('\\)')
        else:
            if node['char'] == '$$':
                self.write('$$')
            else:
                self.write('\\]')


class LatexPINW(NodeWriter):
    """Overloading the start method to make sure that we are not
    printing an extra space when writing `~`. """

    def start(self, node):
        if node.data.startswith('~'):
            strbuffer = self.writer.string_buffer
            try:
                if strbuffer[-1] == ' ':
                    self.writer.string_buffer = strbuffer[:-1]
            except IndexError:
                pass
