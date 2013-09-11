# -*- coding: utf-8 --
"""
The corpus module contains classes needed to process corpus files. Each class
 must implement the abstract class' (CorpusProcessor) process_file and
 write_snippet_file methods.

 The following classes are implemented:
 - KlimaukenCorpusProcessor
"""

from corpora.snippets import SnippetBuilder
from inputOutput.filehandling import sep_file_and_path
import codecs
import lxml.etree as etree

__author__ = 'snorre'

import abc


class CorpusProcessor(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, corpusPath, snippetPath):
        """
        :type corpusPath: str
        :param corpusPath: path to the corpus file
        :type snippetPath: str
        :param snippetPath: path for where to write snippet file
        """
        filePath, filename = sep_file_and_path(corpusPath)
        self.snippetPath = snippetPath
        self.corpusFile = codecs.open(corpusPath, 'r', 'utf-8')
        self.snippetBuilder = SnippetBuilder(filename)

    @abc.abstractmethod
    def process_file(self):
        """
        """
        pass

    @abc.abstractmethod
    def write_snippet_file(self):
        """
        """
        pass


class KlimaukenCorpusProcessor(CorpusProcessor):
    def __init__(self, corpusPath, snippetPath):
        CorpusProcessor.__init__(self, corpusPath, snippetPath)
        self.tags = ['</artikkel>', '<forsideoverskrift>', '<forsideingress>',
                     '<artikkeloverskrift>',
                     '<artikkelbildetekst>', '<artikkelingress>',
                     '<artikkeltekst>']
        self.endTags = ['</s>', '<word>', '</forsideverskrift>',
                        '</forsideingress>', '</artikkeloverskrift>',
                        '</artikkelbildetekst>', '</artikkelingress>',
                        '</artikkeltekst>']
        ## Oslo-Bergen Tags. Drop: pron, det, sbu, prep, konj, ...
        self.goodWords = ['subst', 'verb', 'adj',
                          'adv']
        ## OBS OBS laget etter frekvens i klimauken-dataene OBS
        self.stopWords = ['', 'v\xc3\xa6re', 'ha', 'bli', 'AV', 'ikke',
                          '\xc3\xa5r', 'f\xc3\xa5',
                          'kunne']

    def process_file(self):

        def collectwords(string):
            """
            :type string: str
            :param string: snip to collect words from
            :rtype words: str
            :return words: words in snip
            """
            words = ''
            line = self.corpusFile.readline().strip()
            while line != string:
                ## Should have read the <word>-tag now.
                self.corpusFile.readline()  # skip the "<...word...>"
                line = self.corpusFile.readline()  # get the first ground-form
                # etc
                l = self.line_list(line)
                groundForm = l[0][1:-1]  # Drop the "'s around the ground form
                if len(l) < 2:
                    print "FEIL:", groundForm, ":", l, ":FEIL"  # DEBUG REMOVE
                elif groundForm not in self.stopWords and \
                                l[1] in self.goodWords:
                    words = words + ' ' + groundForm
                line = self.scan_to_line(self.endTags)  # skip
                # remaining
                # forms, if any  (elaborate disambiguation later)
            return words

        def collectsentences():

            """
            :rtype snippets: list
            :return snippets: snippets in string
            """
            line = self.corpusFile.readline()
            snippets = []
            while line.strip() == '<s>':
                words = collectwords('</s>')
                if words != '':
                    snippets.append(words)
                line = self.corpusFile.readline()
            return snippets

        self.scan_to_line(['<snippets>'])

        line = self.scan_to_line(['<artikkel>'])

        while line.strip() == '<artikkel>':

            self.scan_to_line(['<id>'])
            line = self.scan_to_line(['<word>'])  # finds the id,
            # requiring that it exists
            docId = line[6:]  # stripping away <word>
            docId = docId[:-7]  # stripping away <\word>

            self.scan_to_line(['<tags>'])
            line = self.scan_to_line(['<word>'])  # finds the tag,
            # requiring that it exists
            tag = line[6:]  # # stripping away <word>
            tag = tag[:-7]  # # stripping away <\word>

            self.scan_to_line(['<url>'])
            line = self.scan_to_line(['<word>'])  # finds the url,
            # requiring that it exists
            url = line[6:]  # # stripping away <word>
            url = url[:-7]  # # stripping away <\word>

            line = self.scan_tag(self.tags)

            frontpageHeadings = []  # Store snippet-list, type tuples
            frontpageIntroductions = []
            articleHeadings = []
            articleBylines = []
            articleIntroductions = []
            articleTexts = []
            while line != '</artikkel>':
                if line == '<forsideoverskrift>':
                    frontpageHeadings.append(collectsentences())
                elif line == '<forsideingress>':
                    frontpageIntroductions.append(collectsentences())
                elif line == '<artikkeloverskrift>':
                    articleHeadings.append(collectsentences())
                elif line == '<artikkelbildetekst>':
                    articleBylines.append(collectsentences())
                elif line == '<artikkelingress>':
                    articleIntroductions.append(collectsentences())
                elif line == '<artikkeltekst>':
                    articleTexts.append(collectsentences())
                else:
                    print "ERROR UNKNOWN TAG"
                line = self.scan_tag(self.tags)

            self.snippetBuilder.add_document(docId, tag, url,
                                             FrontpageHeading=frontpageHeadings,
                                             FrontpageIntroduction=
                                             frontpageIntroductions,
                                             ArticleHeading=
                                             articleHeadings,
                                             ArticleByline=
                                             articleBylines,
                                             ArticleIntroduction=
                                             articleIntroductions,
                                             ArticleText=articleTexts)
            line = self.corpusFile.readline()

    def write_snippet_file(self):
        """
        """
        snippetTree = self.snippetBuilder.get_element_tree()
        xmlstring = etree.tostring(snippetTree, encoding='utf8',
                                   pretty_print=True)
        print "Xml string created, write to file"
        print self.snippetPath
        outputFile = open(self.snippetPath, "w")
        outputFile.write(xmlstring)

        ##snippetTree.write(self.snippetPath, encoding="UTF-8",
        ##                  xml_declaration=False, pretty_print=True)

    def scan_to_line(self, stringList):
        """
        :type stringList: list
        :param stringList: list of strings to scan for
        :rtype: str
        :return: str matching element in string list
        """

        def inList(line):
            for string in stringList:
                if line.startswith(string):
                    return True
            return False

        line = self.corpusFile.readline()
        while line != '' and not inList(line.strip()):
            line = self.corpusFile.readline()
        return line.strip()

    def scan_tag(self, tags):
        """
        :type tags: list
        :param tags: tags for which to scan
        """
        line = self.scan_to_line(tags)
        p = line.find('>')
        return line[:p + 1]

    def line_list(self, string):

        """
        :type string: str
        :param string: string to split to list
        :return: the list of words/terms
        :rtype: list
        """
        if string == '' or string.isspace():
            return []
        return string.strip().split(" ")
