'''
Created on Mar 8, 2013

@author: snorre
'''
from random import randint, uniform
from cluster import cluster
from tasks.result import CompactTrieClusteringResult

# Map genes to numbers
TREETYPE = 1
TOPBASECLUSTERSAMOUNT = 2
MINTERMOCCURRENCEINCOLLECTION = 3
MAXTERMRATIOINCOLLECTION = 4
MINLIMITFORBASECLUSTERSCORE = 5
MAXLIMITFORBASECLUSTERSCORE = 6
SHOULDDROPSINGLETONBASECLUSTERS = 7
SHOULDDROPONEWORDCLUSTERS = 8


class Chromosome:
    '''Represents a parameter list for the compact trie clustering algorithm.

    This class models a chromosome (in genetic algorithms) and is a
    representation of the parameters used in the compact trie clustering
    algorithm. It contains parameters for tree type (and slice lenghts),
    the max number of base clusters to produce, the min occurrence and
    max occurrence ratio for terms wherein the term is not considered
    a stop word, min and max limits for base cluster scoring, and
    truthy/falsy values to determine if singleton and one word clusters
    should be dropped.

    The object has methods to set a fitness as well as randomly mutate
    one or more of the parameters.
    '''

    def __init__(self,
                 treeType,
                 topBaseClustersAmount,
                 minTermOccurrenceInCollection,
                 maxTermRatioInCollection,
                 minLimitForBaseClusterScore,
                 maxLimitForBaseClusterScore,
                 shouldDropSingletonBaseClusters,
                 shouldDropOneWordClusters):
        '''
        Constructor for the Chromosome class.

        Args:
            treeType (tuple): takes tree values:
                                1. treetype (0 suffix, 1 midslice,
                                            2 rangeslice, 3 nslice)
                                2. 
            topBaseClustersAmount (int): the amount of base clusters to use for
                                            merging to components
            minTermOccurrenceInCollection (int): the lowest limit for which a word
                                                    is not considered a stop word
            maxTermRatioInCollection (int): the max ratio at which a word is not
                                            considered a stop word
            minLimitForBaseClusterScore (int): the limit at which the base
                                                cluster receives a score of 0
            maxLimitForBaseClusterScore (int): the limit at which the base
                                                cluster receives a score of 7.
            shouldDropSingletonBaseClusters (int): boolean (0,1)
            shouldDropOneWordClusters (int): boolean (0,1)
        '''
        self.treeType = treeType
        self.topBaseClustersAmount = topBaseClustersAmount
        self.minTermOccurrenceInCollection = minTermOccurrenceInCollection
        self.maxTermRatioInCollection = maxTermRatioInCollection
        self.minLimitForBaseClusterScore = minLimitForBaseClusterScore
        self.maxLimitForBaseClusterScore = maxLimitForBaseClusterScore
        self.shouldDropSingletonBaseClusters = shouldDropSingletonBaseClusters
        self.shouldDropOneWordClusters = shouldDropOneWordClusters
        self.fitness = 0
        self.result = None

    def calc_fitness_score(self, compactTrieClusterer):
        '''Returns the fitness of the chromosome

        Args:
            cSetting (clusterSettings): An object wrapping data
            and settings needed to run the clustering algorithm,
            the parameters in chromosome excluded.

        Calculate fitness as the average of the two
        '''
        self.result = compactTrieClusterer.cluster(self)
        fMeasure0 = self.result[4][0]
        fMeasure1 = self.result[4][1]
        self.fitness = fMeasure0 + fMeasure1

    def mutate(self):
        '''Mutates one of the chromosome's "genes"

        Mutates one of the objects fields/properties given a probability
        function. The method randomly select one property to mutate.
        '''
        geneToMutate = randint(1, 8)
        if geneToMutate == TREETYPE:
            self.treeType = getRandomTreeType()
        elif geneToMutate == TOPBASECLUSTERSAMOUNT:
            self.topBaseClustersAmount = getRandomTopBaseClustersAmount()
        elif geneToMutate == MINTERMOCCURRENCEINCOLLECTION:
            self.minTermOccurrenceInCollection = getRandomMinTermOccurrence()
        elif geneToMutate == MAXTERMRATIOINCOLLECTION:
            self.maxTermRatioInCollection = getRandomMaxTermRatio()
        elif geneToMutate == MINLIMITFORBASECLUSTERSCORE:
            self.minLimitForBaseClusterScore = getRandomMinLimitBCScore()
        elif geneToMutate == MAXLIMITFORBASECLUSTERSCORE:
            self.maxLimitForBaseClusterScore = getRandomMaxLimitBCScore()
        elif geneToMutate == SHOULDDROPSINGLETONBASECLUSTERS:
            self.shouldDropSingletonBaseClusters = randint(0, 1)
        elif geneToMutate == SHOULDDROPONEWORDCLUSTERS:
            self.shouldDropOneWordClusters = randint(0, 1)
        else:  # Just in case
            pass

    def genesAsTuple(self):
        return (self.treeType,
                self.topBaseClustersAmount,
                self.minTermOccurrenceInCollection,
                self.maxTermRatioInCollection,
                self.minLimitForBaseClusterScore,
                self.maxLimitForBaseClusterScore,
                self.shouldDropSingletonBaseClusters,
                self.shouldDropOneWordClusters)

    def get_precision(self):
        return self.result[2]

    def get_recall(self):
        return self.result[3]

    def get_fmeasure(self):
        return self.result[4]

    def get_time_number_clusters(self):
        return self.result[0]


def createRandomChromosome():
    '''Create and return a chromosome with random values
    '''
    treeType = getRandomTreeType()
    topBaseClustersAmount = randint(0, 5000)
    minTermOccurenceInCollection = randint(1, 100)
    maxTermRatioInCollection = uniform(.1, 1)
    minLimitForBaseClusterScore = randint(1, 5)
    maxLimitForBaseClusterScore = randint(6, 10)
    shouldDropSingletonBaseClusters = randint(0, 1)
    shouldDropOneWordClusters = randint(0, 1)

    return Chromosome(treeType,
                      topBaseClustersAmount,
                      minTermOccurenceInCollection,
                      maxTermRatioInCollection,
                      minLimitForBaseClusterScore,
                      maxLimitForBaseClusterScore,
                      shouldDropSingletonBaseClusters,
                      shouldDropOneWordClusters)


def getRandomTreeType():
    '''Return a tuple representing a randomized tree type
    '''
    treeType = randint(0, 3)
    if treeType == cluster.SUFFIXTREE:
        return (0, 0, 0)
    elif treeType == cluster.MIDSLICE:
        return (1, 0, 0)
    elif treeType == cluster.RANGESLICE:
        return getRandomRangeSlice()
    elif treeType == cluster.NSLICE:
        return getRandomNSlice()


def getRandomRangeSlice():
    '''Get random range slice values
    '''
    rangeMin = uniform(.1, .5)
    rangeMax = uniform(.6, .9)
    return (2, rangeMin, rangeMax)


def getRandomNSlice():
    '''Get a random nslice value
    '''
    sliceLength = randint(1, 20)
    return (3, sliceLength, 0)


def getRandomTopBaseClustersAmount():
    return randint(100, 5000)


def getRandomMinTermOccurrence():
    return randint(5, 500)


def getRandomMaxTermRatio():
    return round(uniform(0.1, 1.0), 2)


def getRandomMinLimitBCScore():
    return randint(1, 5)


def getRandomMaxLimitBCScore():
    return randint(3, 9)


def getRandomShouldDropSingletons():
    return randint(0, 1)


def genesTupleToChromosome(tuple):
    '''Takes a tuple of genes and transforms it to a chromosome
    '''
    return Chromosome(tuple[0],
                      tuple[1],
                      tuple[2],
                      tuple[3],
                      tuple[4],
                      tuple[5],
                      tuple[6],
                      tuple[7])


def crossChromosomes(chromosome1, chromosome2):
    '''Takes two  parent chromosomes cross them and return two children
    chromosomes
    '''
    genes1 = chromosome1.genesAsTuple()
    genes2 = chromosome2.genesAsTuple()
    crossOverPoint = randint(1, len(genes1) - 1)
    genes12 = genes1[0:crossOverPoint] + genes2[crossOverPoint:len(genes2)]
    genes21 = genes2[0:crossOverPoint] + genes1[crossOverPoint:len(genes1)]

    return [genesTupleToChromosome(genes12),
            genesTupleToChromosome(genes21)]
