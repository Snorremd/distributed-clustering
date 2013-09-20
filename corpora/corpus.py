"""
Created on May 22, 2013

@author: snorre
"""

class Corpus(object):
    """
    Params:
        name (str): name of corpus
        filename (str): filename of snippet file
        directory (str): directory wherein corpus file is contained
        singletag (bool): if corpus use singletag clusters
    """

    def __init__(self, name, snippetFilePath, snippetFile, corpusFilePath,
                 corpusFile, processorName, singleTag):
        """
        Constructor
        """
        self.name = name
        self.snippetFilePath = snippetFilePath
        self.snippetFile = snippetFile
        self.corpusFilePath = corpusFilePath
        self.corpusFile = corpusFile
        self.processorName = processorName
        self.singleTag = singleTag
