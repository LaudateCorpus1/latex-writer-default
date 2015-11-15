"""LATEX: LIST NodeWriter

Writes the items.

"""

from lexor.core.writer import NodeWriter
from lexor.command.lang import load_rel

NW = load_rel(__file__, 'nw')


class ListItemNW(NodeWriter):
    """List elements display. """

    def start(self, node):
        self.write('\\item')
        att = NW.format_attributes(node)
        if att != '':
            self.write('[%s] ' % att)
        else:
            self.write(' ')
        self.writer.flush_buffer()

    def end(self, _):
        self.writer.endl(False, tail=False)
