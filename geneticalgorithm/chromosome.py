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
TEXTAMOUNT = 10
SIMILARITYMEASURE = 11
SORTDESCENDING = 12

## Constants for tree types
SUFFIX_TREE = 0
MID_SLICE = 1
RANGE_SLICE = 2
N_SLICE = 3

## Constants for similarity types
JACCARD_SIMILARITY = 0
COSINE_SIMILARITY = 1
AMENDMENT_1C_SIMILARITY = 2


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
                 textType,
                 text_amount,
                 similarity_measure,
                 sortDescending):
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
        self.tree_type = treeType
        self.top_base_clusters_amount = topBaseClustersAmount
        self.min_term_occurrence_in_collection = minTermOccurrenceInCollection
        self.max_term_ratio_in_collection = maxTermRatioInCollection
        self.min_limit_for_base_cluster_score = minLimitForBaseClusterScore
        self.max_limit_for_base_cluster_score = maxLimitForBaseClusterScore
        self.sort_descending = sortDescending
        self.should_drop_singleton_base_clusters = shouldDropSingletonBaseClusters
        self.should_drop_one_word_clusters = shouldDropOneWordClusters
        self.fitness = 0
        self.result = None
        self.text_types = textType
        self.text_amount = text_amount
        self.similarity_measure = similarity_measure

    def calc_fitness_score(self, compact_trie_clusterer):
        """
        Returns the fitness of the chromosome

        Args:
            cSetting (clusterSettings): An object wrapping data
            and settings needed to run the clustering algorithm,
            the parameters in chromosome excluded.

        Calculate fitness as the average of the two
        """

        self.result = compact_trie_clusterer.cluster(self)
        fMeasure0 = self.result.f_measures[0]
        fMeasure1 = self.result.f_measures[1]
        self.fitness = fMeasure0 + fMeasure1

    def mutate(self):
        """
        Mutates one of the chromosome's "genes"

        Mutates one of the objects fields/properties given a probability
        function. The method randomly select one property to mutate.
        """
        geneToMutate = randint(1, 11)
        if geneToMutate == TREETYPE:
            self.tree_type = getRandomTreeType()
        elif geneToMutate == TOPBASECLUSTERSAMOUNT:
            self.top_base_clusters_amount = getRandomTopBaseClustersAmount()
        elif geneToMutate == MINTERMOCCURRENCEINCOLLECTION:
            self.min_term_occurrence_in_collection = getRandomMinTermOccurrence()
        elif geneToMutate == MAXTERMRATIOINCOLLECTION:
            self.max_term_ratio_in_collection = getRandomMaxTermRatio()
        elif geneToMutate == MINLIMITFORBASECLUSTERSCORE:
            self.min_limit_for_base_cluster_score = getRandomMinLimitBCScore()
        elif geneToMutate == MAXLIMITFORBASECLUSTERSCORE:
            self.max_limit_for_base_cluster_score = getRandomMaxLimitBCScore()
        elif geneToMutate == SHOULDDROPSINGLETONBASECLUSTERS:
            self.should_drop_singleton_base_clusters = randint(0, 1)
        elif geneToMutate == SHOULDDROPONEWORDCLUSTERS:
            self.should_drop_one_word_clusters = randint(0, 1)
        elif geneToMutate == TEXTTYPE:
            self.text_types = getRandomTextType()
        elif geneToMutate == TEXTAMOUNT:
            self.text_amount = get_random_text_amount()
        elif geneToMutate == SIMILARITYMEASURE:
            self.similarity_measure = get_random_similarity_measure()
        elif geneToMutate == SORTDESCENDING:
            self.sort_descending = get_random_sort_descending()
        else:  # Just in case
            pass

    def genesAsTuple(self):
        return (self.tree_type,
                self.top_base_clusters_amount,
                self.min_term_occurrence_in_collection,
                self.max_term_ratio_in_collection,
                self.min_limit_for_base_cluster_score,
                self.max_limit_for_base_cluster_score,
                self.should_drop_singleton_base_clusters,
                self.should_drop_one_word_clusters,
                self.text_types,
                self.text_amount,
                self.similarity_measure,
                self.sort_descending)

    def chromosome_as_dict(self):
        text_types_keys = text_types()
        chromosome_dict = {
            "id": self.id,
            "tree_type_1": self.tree_type[0],
            "tree_type_2": self.tree_type[1],
            "tree_type_3": self.tree_type[2],
            "text_type_frontpageheading": self.text_types[text_types_keys[0]],
            "text_type_frontpageintroduction": self.text_types[text_types_keys[1]],
            "text_type_articleheading": self.text_types[text_types_keys[2]],
            "text_type_articlebyline": self.text_types[text_types_keys[3]],
            "text_type_articleintroduction": self.text_types[text_types_keys[4]],
            "text_type_articletext": self.text_types[text_types_keys[5]],
            "text_amount": self.text_amount,
            "top_base_clusters_amount": self.top_base_clusters_amount,
            "min_term_occurrence_collection": self
            .min_term_occurrence_in_collection,
            "max_term_ratio_collection": self.max_term_ratio_in_collection,
            "min_limit_base_cluster_score": self
            .min_limit_for_base_cluster_score,
            "max_limit_base_cluster_score": self
            .max_limit_for_base_cluster_score,
            "order_descending": self.sort_descending,
            "similarity_measure_method": self
            .similarity_measure["similarity_method"],
            "similarity_measure_threshold": self
            .similarity_measure["params"][0],
            "similarity_measure_avg_cf_threshold": self
            .similarity_measure["params"][1],
            "similarity_measure_cf_intersect_min": self
            .similarity_measure["params"][2],
            "drop_singleton_base_clusters": self
            .should_drop_singleton_base_clusters,
            "drop_one_word_clusters": self.should_drop_one_word_clusters,
            "fitness": self.fitness
        }
        if self.result:
            chromosome_dict["precision"] = self.result.precision
            chromosome_dict["recall"] = self.result.recall
            chromosome_dict["fmeasure"] = self.result.f_measure
            chromosome_dict["time"] = self.result.time
            chromosome_dict["number_of_clusters"] = self.result.no_of_clusters
            chromosome_dict["number_of_base_clusters"] = self.result\
                .no_of_base_clusters

            for i in range(6):

                chromosome_dict["tag_accuracy_{0}".format(i)] = self.result\
                    .tag_accuracies[i]

                chromosome_dict["precision_{0}".format(i)] = self.result\
                    .precisions[i]

                chromosome_dict["recall_{0}".format(i)] = self.result\
                    .recalls[i]

                chromosome_dict["f_measure_{0}".format(i)] = self.result\
                    .f_measures[i]

        return chromosome_dict

    def get_precision(self):
        return self.result.precision

    def get_recall(self):
        return self.result.recall

    def get_fmeasure(self):
        return self.result.f_measure

    def get_tag_accuracies(self):
        print(self.result)
        return self.result.tag_accuracies

    def get_precisions(self):
        return self.result.precisions

    def get_recalls(self):
        return self.result.recalls

    def get_fmeasures(self):
        return self.result.f_measures

    def get_time_number_clusters(self):
        return (self.result.time, self.result.no_of_clusters,
                self.result.no_of_base_clusters)


def create_random_chromosome():
    """
    Create and return a chromosome with random values
    """
    tree_type = getRandomTreeType()
    top_base_clusters_amount = getRandomTopBaseClustersAmount()
    minTermOccurrenceInCollection = getRandomMinTermOccurrence()
    maxTermRatioInCollection = getRandomMaxTermRatio()
    minLimitForBaseClusterScore = getRandomMinLimitBCScore()
    maxLimitForBaseClusterScore = getRandomMaxLimitBCScore()
    sort_descending = get_random_sort_descending()
    shouldDropSingletonBaseClusters = randint(0, 1)
    shouldDropOneWordClusters = randint(0, 1)
    textType = getRandomTextType()
    text_amount = get_random_text_amount()
    similarity_measure = get_random_similarity_measure()

    return Chromosome(tree_type,
                      top_base_clusters_amount,
                      minTermOccurrenceInCollection,
                      maxTermRatioInCollection,
                      minLimitForBaseClusterScore,
                      maxLimitForBaseClusterScore,
                      shouldDropSingletonBaseClusters,
                      shouldDropOneWordClusters,
                      textType,
                      text_amount,
                      similarity_measure,
                      sort_descending)


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


def get_random_text_amount():
    return round(uniform(0.1, 1.0), 2)


def get_random_similarity_measure():
    type = randint(0, 2)
    similarity_params = {}
    threshold = round(uniform(0, 1), 2)

    if type == JACCARD_SIMILARITY:
        similarity_params = {"similarity_method": 0,
                             "params": (threshold, 0, 0)}

    elif type == COSINE_SIMILARITY:
        similarity_params = {"similarity_method": 1,
                             "params": (threshold, 0, 0)}

    elif type == AMENDMENT_1C_SIMILARITY:
        avg_cf_threshold = randint(5, 100)  # TODO: Find reasonable values
        cf_intersect_min = randint(0, 10)
        similarity_params = {"similarity_method": 2,
                             "params": (0.5, avg_cf_threshold, cf_intersect_min)}

    return similarity_params


def get_random_sort_descending():
    return randint(0, 1)


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
                      geneTuple[8],
                      geneTuple[9],
                      geneTuple[10],
                      geneTuple[11])


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
