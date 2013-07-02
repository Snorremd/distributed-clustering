# coding=utf-8
from xml.etree.ElementTree import ElementTree, Element, SubElement

__author__ = 'Snorre Magnus Davøen'


class SnippetBuilder(object):

    def __init__(self, sourceFilename,):
        """Initialize a snippet builder

        :type sourceFilename: basestring
        :param sourceFilename: the filename of the source corpus file
        """
        self.root = Element('snippetcollection', {'source': sourceFilename})

    def add_document(self, docId, tags, source, snippets):
        """
        :type docId: basestring
        :param docId: the id of the document
        :type tags: str
        :param tags: a string of one or more tags for document
        :type source: basestring
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