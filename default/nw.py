"""LEXOR: DEFAULT NodeWriters

Collection of NodeWriter objects to write html files in the lexor
format without indentations and breaks lines after the first word
that goes beyond a certain column number.

"""

import re
import textwrap
from lexor.core.writer import NodeWriter
import lexor.core.elements as core
RE = re.compile(r'\s+')
TW = textwrap.TextWrapper()
RAWTEXT = (
    'script', 'style', 'textarea', 'title'
)
BLOCK = [
    'address', 'article', 'aside', 'blockquote', 'dir',
    'div', 'dl', 'fieldset', 'footer', 'form', 'header', 'hgroup',
    'hr', 'main', 'menu', 'nav', 'pre', 'section', 'table', 'ol',
    'ul', 'li', 'link', '#doctype', 'head', 'body', 'document',
    'table',
]
BLOCK.extend(RAWTEXT)


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


class TextNW(NodeWriter):
    """Writes text nodes with multiple spaces removed. """

    def data(self, node):
        if self.writer.pre_node:
            self.write(node.data)
            return
        text = re.sub(RE, ' ', node.data)
        if text != ' ':
            self.write(text)
        else:
            char = self.writer.last()[-1]
            if char not in ' \n' and (node.index != 0 and
                                      node.prev.name not in BLOCK and
                                      node.next is not None and
                                      node.next.name not in BLOCK):
                self.write(text)


class EntityNW(NodeWriter):
    """Display the entity nodes. """

    mapping = {
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&ndash;': '--',
        '&#8211;': '--',
        '&mdash;': '---',
        '&#8212;': '---',
        '&#8216;': "'",
        '&#8217;': "'",
        '&#8220;': '"',
        '&#8221;': '"',
        '&#8226;': '*',
        '&bull;': '*',
        '&nbsp;': ' ',
        '&quot;': '"',
        '&ldquo;': '"',
        '&rdquo;': '"',
    }

    def __init__(self, writer):
        NodeWriter.__init__(self, writer)
        for i in xrange(32, 127):
            self.mapping['&#%d;' % i] = chr(i)

    def data(self, node):
        try:
            data = self.mapping[node.data]
        except KeyError:
            if node.data == '\\backslash':
                data = '\\'
            elif node.data[0] == '\\':
                data = node.data[1:]
            else:
                data = node.data
        self.write(data)


class DefaultNW(NodeWriter):
    """Default way of writing LEXOR elements. """

    def start(self, node):
        if node.name == 'pre':
            self.writer.pre_node += 1
            self.writer.enable_raw()
            if 'pre' in BLOCK:
                self.writer.endl(False)
        if not self.writer.pre_node and node.name in BLOCK:
            self.writer.endl(False)
        if isinstance(node, core.ProcessingInstruction):
            self.write('<%s' % node.name, split=True)
            if '\n' in node.data:
                self.write('\n')
            else:
                self.write(' ')
            return
        if isinstance(node, core.Void) or '_void' in node:
            self.write('\\%s' % node.name)
        else:
            self.write('\\begin{%s}' % node.name)
        att = format_attributes(node, ['args', 'id', '_void'])
        if att:
            self.write('[%s]' % att)
        if 'args' in node:
            # Need a split function which can escape `,`
            data = [item.strip() for item in node['args'].split(',')]
            for item in data:
                self.write('{%s}' % item)
        if '_void' in node:
            self.write('{')
        elif 'id' in node:
            self.write('\\label{%s}' % node['id'])

    def data(self, node):
        if (node.name in RAWTEXT or
                isinstance(node, core.ProcessingInstruction)):
            enabled = self.writer.raw_enabled()
            if not enabled:
                self.writer.enable_raw()
            self.write(node.data)
            if not enabled:
                self.writer.disable_raw()
        else:
            text = re.sub(RE, ' ', node.data)
            self.write(text)

    def child(self, node):
        if self.writer.pre_node:
            return True
        for child in node.child:
            if child.name not in ['#text', '#entity']:
                return True
        for child in node.child:
            self.writer.get_node_writer(child.name).data(child)
        if not isinstance(node, core.Void):
            self.write('\\end{%s}' % node.name)
        if node.name in BLOCK:
            self.writer.endl(False)

    def end(self, node):
        if node.name == 'pre':
            self.writer.pre_node -= 1
            if self.writer.pre_node == 0:
                self.writer.disable_raw()
        raw = self.writer.pre_node
        if node.child is None:
            if isinstance(node, core.ProcessingInstruction):
                self.write('?>')
            elif isinstance(node, core.RawText):
                self.write('%%')
            if not raw:
                self.writer.endl(False)
        elif '_void' in node:
            self.write('}')
            if 'id' in node:
                self.write('\\label{%s}' % node['id'])
        else:
            self.write('\\end{%s}' % node.name)
            if not raw and node.name in BLOCK:
                self.writer.endl(False)


class DoctypeNW(NodeWriter):
    """Writes the doctype node: `<!DOCTYPE ...>`. """

    def start(self, node):
        self.write('<!DOCTYPE ')

    def data(self, node):
        self.write(re.sub(RE, ' ', node.data).strip())

    def end(self, node):
        self.write('>\n')


class CDataNW(NodeWriter):
    """Writes the CDATA node. """

    def start(self, node):
        self.write('<![CDATA[', split=True)

    def data(self, node):
        enabled = self.writer.raw_enabled()
        if not enabled:
            self.writer.enable_raw()
        data = node.data.split(']]>')
        for index in xrange(len(data)-1):
            self.write(data[index] + ']]]]><![CDATA[>')
        self.write(data[-1])
        if not enabled:
            self.writer.disable_raw()

    def end(self, node):
        self.write(']]>')


class CommentNW(NodeWriter):
    """Comment can also follow the tree structure. They have to be
    formatted to reflect this. """
    raw_enabled = None
    re_user =  re.compile(r'(?P<user>[A-Z]*):')
    match = False

    def start(self, node):
        if node.prev is not None:
            if node.prev.name == '#text':
                index = node.prev.data.rfind('\n')
                if index != -1:
                    line = node.prev.data[index+1:]
                    if line.strip() == '':
                        self.writer.endl(False)
        self.raw_enabled = self.writer.raw_enabled()
        if not self.raw_enabled:
            self.writer.enable_raw()
        self.match = self.re_user.match(node.data)
        if self.match:
            self.write('\\%scomment{' % self.match.group('user'))

    def data(self, node):
        if self.match:
            start = len(self.match.group('user'))
            self.write(node.data[start+2:])
        else:
            lines = node.data.split('\n')
            if len(lines) == 1:
                self.write('% '+lines[0])
                return
            self.write('% '+lines[0])
            self.write('\n')
            for num in xrange(1, len(lines)-1):
                self.write('% ')
                self.write(lines[num].strip())
                self.write('\n')
            self.write('% ')
            self.write(lines[-1].lstrip())

    def end(self, node):
        if self.match:
            self.write('}')
        else:
            self.writer.endl()
        if not self.raw_enabled:
            self.writer.disable_raw()
        if node.next is not None:
            nnext = node.next
            if nnext.name == '#text' and nnext.data.startswith('\n'):
                self.writer.endl()


class DocumentNW(NodeWriter):
    """Finish document with a new line character. """

    def end(self, node):
        self.writer.endl(False)


class HRuleNW(NodeWriter):
    """Display hr element. """

    def start(self, _):
        self.writer.endl(False)
        self.writer.endl()
        self.write('-'*self.writer.width)
        self.write('\n\n')


class AnchorNW(NodeWriter):
    """Anchor element display. """

    def start(self, _):
        self.write('[')

    def end(self, node):
        self.write(']')
        exclude = []
        if 'href' in node:
            href = node['href']
            exclude.append('href')
        else:
            href = ''
        if 'title' in node:
            title = ' "%s"' % node['title']
            exclude.append('title')
        else:
            title = ''
        self.write('(%s%s)' % (href, title), split=True)
        if node.attlen - len(exclude) > 0:
            self.write('{%s}' % format_attributes(node, exclude))
