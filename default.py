"""LATEX: DEFAULT Writer Style

This style writes a tex document without indentations. Writes a new
line character after the first word that goes beyond a given width
(70 by default).

Note: At the moment there is no native tex parser and thus there are
no tex tags. This writer assumes that the document is a valid html
document and it attempts to write it in the latex format. Due to this
all the tex converters will aim to attempt to convert to valid html
tags.

"""

from lexor import init, load_aux
from lexor.core.writer import NodeWriter

INFO = init(
    version=(0, 0, 1, 'final', 0),
    lang='latex',
    type='writer',
    description='Writes HTML files in LaTeX form.',
    url='http://jmlopez-rod.github.io/lexor-lang/latex-writer-default',
    author='Manuel Lopez',
    author_email='jmlopez.rod@gmail.com',
    license='BSD License',
    path=__file__
)
DEFAULTS = {
    'width': '70',
    'add_block': '',
    'del_block': '',
    'header': 'setext',
    'hashheader': 'closed',
}
MOD = load_aux(INFO)
MAPPING = {
    'latex': MOD['latex'].LatexNW,
    '?latex': MOD['latex'].LatexPINW,
    '?mathjax': NodeWriter,
    'documentclass': MOD['document'].DocumentClassNW,
    'usepackage': MOD['document'].UsePackageNW,
    'bibliography': MOD['document'].BibliographyNW,
    'li': MOD['list'].ListItemNW,
    'a': MOD['nw'].AnchorNW,
    'em': MOD['inline'].EmNW,
    'i': 'em',
    'strong': MOD['inline'].StrongNW,
    'hr': MOD['nw'].HRuleNW,
    'h1': MOD['header'].HeaderNW,
    'p': MOD['paragraph'].ParagraphNW,
    '#document': MOD['nw'].DocumentNW,
    '#text': MOD['nw'].TextNW,
    '#entity': MOD['nw'].EntityNW,
    '#comment': MOD['nw'].CommentNW,
    '#doctype': MOD['nw'].DoctypeNW,
    '#cdata-section': MOD['nw'].CDataNW,
    '__default__': MOD['nw'].DefaultNW,
}
for item in ['h2', 'h3', 'h4', 'h5', 'h6']:
    MAPPING[item] = 'h1'


def pre_process(writer, _):
    """Sets the default width for the writer. """
    writer.disable_raw()
    writer.enable_wrap()
    writer.header = writer.defaults['header']
    writer.width = int(writer.defaults['width'])
    writer.pre_node = 0
    writer.list_level = 0
    for name in writer.defaults['add_block'].split(','):
        if name and name not in MOD['nw'].BLOCK:
            MOD['nw'].BLOCK.append(name)
    for name in writer.defaults['del_block'].split(','):
        try:
            MOD['nw'].BLOCK.remove(name)
        except ValueError:
            pass
