'''
Created on May 22, 2013

@author: snorre
'''

class Corpus(object):
    '''
    Params:
        name (str): name of corpus
        filename (str): filename of snippet file
        directory (str): directory wherein corpus file is contained
        singletag (bool): if corpus use singletag clusters
    '''

    def __init__(self, name, filename, directory, singletag):
        '''
        Constructor
        '''
        self.name = name
        self. filename = filename
        self.directory = directory
        self.singletag = singletag
