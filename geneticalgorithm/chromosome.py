"""
Created on Mar 8, 2013

@author: snorre
"""
from random import randint, uniform
from cluster import clustering

##  Map genes to numbers
from cluster.clustering import text_types

TREETYPE = 1
TOPBASECLUSTERSAMOUNT = 2
MINTERMOCCURRENCEINCOLLECTION = 3
MAXTERMRATIOINCOLLECTION = 4
MINLIMITFORBASECLUSTERSCORE = 5
MAXLIMITFORBASECLUSTERSCORE = 6
SHOULDDROPSINGLETONBASECLUSTERS = 7
SHOULDDROPONEWORDCLUSTERS = 8
TEXTTYPE = 9

## Constants for tree types
SUFFIX_TREE = 0
MID_SLICE = 1
RANGE_SLICE = 2
N_SLICE = 3


class Chromosome:
    """Represents a parameter list for the compact trie clustering algorithm.

    This class models a chromosome (in genetic algorithms) and is a
    representation of the parameters used in the compact trie clustering
    algorithm. It contains parameters for tree type (and slice lengths),
    the max number of base clusters to produce, the min occurrence and
    max occurrence ratio for terms wherein the term is not considered
    a stop word, min and max limits for base cluster scoring, and
    truthy/falsy values to determine if singleton and one word clusters
    should be dropped.

    The object has methods to set a fitness as well as randomly mutate
    one or more of the parameters.
    """

    #ID Counter
    idCounter = 1

    def __init__(self,
                 treeType,
                 topBaseClustersAmount,
                 minTermOccurrenceInCollection,
                 maxTermRatioInCollection,
                 minLimitForBaseClusterScore,
                 maxLimitForBaseClusterScore,
                 shouldDropSingletonBaseClusters,
                 shouldDropOneWordClusters,
                 textType):
        """
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
        """
        self.id = Chromosome.idCounter
        Chromosome.idCounter += 1
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
        self.textTypes = textType

    def calc_fitness_score(self, compactTrieClusterer):
        """
        Returns the fitness of the chromosome

        Args:
            cSetting (clusterSettings): An object wrapping data
            and settings needed to run the clustering algorithm,
            the parameters in chromosome excluded.

        Calculate fitness as the average of the two
        """

        self.result = compactTrieClusterer.cluster(self)
        compactTrieClusterer = None
        fMeasure0 = self.result[4][0]
        fMeasure1 = self.result[4][1]
        self.fitness = fMeasure0 + fMeasure1


    def mutate(self):
        """
        Mutates one of the chromosome's "genes"

        Mutates one of the objects fields/properties given a probability
        function. The method randomly select one property to mutate.
        """
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
                self.shouldDropOneWordClusters,
                self.textTypes)

    def chromosome_as_dict(self):
        textTypesKeys = text_types()
        chromosomeDict = {
            "id": self.id,
            "tree_type_1": self.treeType[0],
            "tree_type_2": self.treeType[1],
            "tree_type_3": self.treeType[2],
            "text_type_frontpageheading": self.textTypes[textTypesKeys[0]],
            "text_type_frontpageintroduction": self.textTypes[textTypesKeys[1]],
            "text_type_articleheading": self.textTypes[textTypesKeys[2]],
            "text_type_articlebyline": self.textTypes[textTypesKeys[3]],
            "text_type_articleintroduction": self.textTypes[textTypesKeys[4]],
            "text_type_articletext": self.textTypes[textTypesKeys[5]],
            "top_base_clusters_amount": self.topBaseClustersAmount,
            "min_term_occurrence_collection": self
            .minTermOccurrenceInCollection,
            "max_term_ratio_collection": self.maxTermRatioInCollection,
            "min_limit_base_cluster_score": self
            .minLimitForBaseClusterScore,
            "max_limit_base_cluster_score": self
            .maxLimitForBaseClusterScore,
            "drop_singleton_base_clusters": self
            .shouldDropSingletonBaseClusters,
            "drop_one_word_clusters": self.shouldDropOneWordClusters,
            "fitness": self.fitness
        }
        if self.result:
            chromosomeDict["fmeasure"] = self.result[1][0]
            chromosomeDict["precision"] = self.result[1][1]
            chromosomeDict["recall"] = self.result[1][2]
            chromosomeDict["fmeasure"] = self.result[1][0]
            chromosomeDict["time"] = self.result[0][0]
            chromosomeDict["number_of_clusters"] = self.result[0][1]
            chromosomeDict["number_of_base_clusters"] = self.result[0][2]
            chromosomeDict["precision_0"] = self.result[2][0]
            chromosomeDict["precision_1"] = self.result[2][1]
            chromosomeDict["precision_2"] = self.result[2][2]
            chromosomeDict["precision_3"] = self.result[2][3]
            chromosomeDict["precision_4"] = self.result[2][4]
            chromosomeDict["precision_5"] = self.result[2][5]
            chromosomeDict["recall_0"] = self.result[3][0]
            chromosomeDict["recall_1"] = self.result[3][1]
            chromosomeDict["recall_2"] = self.result[3][2]
            chromosomeDict["recall_3"] = self.result[3][3]
            chromosomeDict["recall_4"] = self.result[3][4]
            chromosomeDict["recall_5"] = self.result[3][5]
            chromosomeDict["f_measure_0"] = self.result[4][0]
            chromosomeDict["f_measure_1"] = self.result[4][1]
            chromosomeDict["f_measure_2"] = self.result[4][2]
            chromosomeDict["f_measure_3"] = self.result[4][3]
            chromosomeDict["f_measure_4"] = self.result[4][4]
            chromosomeDict["f_measure_5"] = self.result[4][5]
        return chromosomeDict

    def get_precision(self):
        return self.result[1][0]

    def get_recall(self):
        return self.result[1][1]

    def get_fmeasure(self):
        return self.result[1][2]

    def get_precisions(self):
        return self.result[2]

    def get_recalls(self):
        return self.result[3]

    def get_fmeasures(self):
        return self.result[4]

    def get_time_number_clusters(self):
        return self.result[0]


def createRandomChromosome():
    """
    Create and return a chromosome with random values
    """
    treeType = getRandomTreeType()
    topBaseClustersAmount = randint(0, 5000)
    minTermOccurrenceInCollection = randint(1, 100)
    maxTermRatioInCollection = uniform(.1, 1)
    minLimitForBaseClusterScore = randint(1, 5)
    maxLimitForBaseClusterScore = randint(6, 10)
    shouldDropSingletonBaseClusters = randint(0, 1)
    shouldDropOneWordClusters = randint(0, 1)
    textType = getRandomTextType()

    return Chromosome(treeType,
                      topBaseClustersAmount,
                      minTermOccurrenceInCollection,
                      maxTermRatioInCollection,
                      minLimitForBaseClusterScore,
                      maxLimitForBaseClusterScore,
                      shouldDropSingletonBaseClusters,
                      shouldDropOneWordClusters,
                      textType)


def getRandomTreeType():
    """
    Return a tuple representing a randomized tree type
    """
    treeType = randint(0, 3)
    if treeType == SUFFIX_TREE:
        return 0, 0, 0
    elif treeType == MID_SLICE:
        return 1, 0, 0
    elif treeType == RANGE_SLICE:
        return getRandomRangeSlice()
    elif treeType == N_SLICE:
        return getRandomNSlice()


def getRandomRangeSlice():
    """
    Get random range slice values
    """
    rangeMin = uniform(.3, .5)
    rangeMax = uniform(.6, .8)
    return 2, rangeMin, rangeMax


def getRandomNSlice():
    """
    Get a random nslice value
    """
    sliceLength = randint(1, 20)
    return 3, sliceLength, 0


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


def getRandomTextType():
    textTypes = {}
    for i in range(6):
        key = clustering.text_types()[i]
        textTypes[key] = randint(0, 1)
    return textTypes


def genesTupleToChromosome(geneTuple):
    """
    Takes a tuple of genes and transforms it to a chromosome
    :param geneTuple:
    """
    return Chromosome(geneTuple[0],
                      geneTuple[1],
                      geneTuple[2],
                      geneTuple[3],
                      geneTuple[4],
                      geneTuple[5],
                      geneTuple[6],
                      geneTuple[7],
                      geneTuple[8])


def crossChromosomes(chromosome1, chromosome2):
    """
    Takes two  parent chromosomes cross them and return two children
    chromosomes
    """
    genes1 = chromosome1.genesAsTuple()
    genes2 = chromosome2.genesAsTuple()
    crossOverPoint = randint(1, len(genes1) - 1)
    genes12 = genes1[0:crossOverPoint] + genes2[crossOverPoint:len(genes2)]
    genes21 = genes2[0:crossOverPoint] + genes1[crossOverPoint:len(genes1)]

    return [genesTupleToChromosome(genes12),
            genesTupleToChromosome(genes21)]
