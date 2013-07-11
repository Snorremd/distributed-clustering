'''
Created on Apr 9, 2013

@author: snorre
'''


class ClusterSettings:
    '''
    A class for wrapping information needed for clustering
    '''

    def __init__(self, dropSingletonGTClusters,
                 fBetaConstant, corpusName):
        '''
        Constructor
        '''
        self.dropSingletonGTClusters = dropSingletonGTClusters
        self.fBetaConstant = fBetaConstant
        self.corpusName = corpusName
