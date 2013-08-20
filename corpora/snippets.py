# coding=utf-8
#from xml.etree.ElementTree import ElementTree, Element, SubElement
from lxml.etree import ElementTree, Element, SubElement

__author__ = 'Snorre Magnus Davøen'


class SnippetBuilder(object):
    """
    SnippetBuilder implements functionality for building snippet xml
    documents. It creates a root element <snippetcollection> with a
    sourcefile attribute. A caller method may insert documents <snippet>
    elements with attributes for docId, tags and source. It should also
    provide a list of snippets whit which to fill the snippet element.
    """

    def __init__(self, sourceFilename, ):
        """Initialize a snippet builder

        :type sourceFilename: str
        :param sourceFilename: the filename of the source corpus file
        """
        self.root = Element('snippetcollection', {'source': sourceFilename})

    def add_document(self, docId, tags, source, snippets):
        """
        :type docId: str
        :param docId: the id of the document
        :type tags: str
        :param tags: a string of one or more tags for document
        :type source: str
        :param source: the source of the document
        :type snippets: list
        :param snippets: a list of snippets contained in the document
        """
        document = SubElement(self.root, 'snippet',
                              {'id': docId, 'tags': tags, 'source': source})
        self.add_snippets(document, snippets)

    def add_snippets(self, document, snippetTuples):
        """
        :type document: xml.etree.ElementTree.Element
        :param document: the document in which to insert snippets
        :type snippetTuples: list
        :param snippetTuples: a list of tuples with snippet - attribute pairs
        """
        for snippets, snippetType in snippetTuples:
            for snippet in snippets:
                snip = SubElement(document, 'snip', {'type': snippetType})
                snip.text = snippet

    def get_element_tree(self):
        """
        :return: a snippet collection represented as an element tree
        :rtype: xml.etree.ElementTree.ElementTree
        """
        return ElementTree(self.root)