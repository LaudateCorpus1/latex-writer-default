"""LEXOR: INLINE NodeWriter

Here we define inline node writers.

"""

from lexor.core.writer import NodeWriter


class StrongNW(NodeWriter):
    """Strong element display. """

    def start(self, node):
        self.write('{\\bf ')

    def end(self, node):
        self.write('}')


class EmNW(NodeWriter):
    """Strong element display. """

    def start(self, node):
        self.write('\\emph{')

    def end(self, node):
        self.write('}')
