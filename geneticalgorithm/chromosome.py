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
ETZIONI_SIMILARITY = 0
JACCARD_SIMILARITY = 1
COSINE_SIMILARITY = 2
AMENDMENT_1C_SIMILARITY = 3


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
        precision0 = self.result.precisions[0]
        recall0 = self.result.recalls[0]
        ## If number of clusters twice as many as ground truth clusters, subtract 0.2 from fitness.
        ## If number thrice as high, subtract 0.3 and so forth.
        print("NUMBER OF GROUND TRUTH CLUSTERS: " + str(self.result.no_of_gt_clusters))
        ratio_modifier = 0

        if self.result.no_of_gt_clusters > 0:
            cluster_ratio = (self.result.no_of_clusters / self.result.no_of_gt_clusters)
            if 0.8 <= cluster_ratio <= 3:
                ratio_modifier = 0.1
            else:
                ratio_modifier = -0.1

        #fMeasure0 = self.result.f_measures[0]
        #fMeasure1 = self.result.f_measures[1]
        self.fitness = self.result.f_measures[0] + ratio_modifier  # fMeasure0 + fMeasure1

    def mutate(self):
        """
        Mutates one of the chromosome's "genes"

        Mutates one of the objects fields/properties given a probability
        function. The method randomly select one property to mutate.
        """
        gene_to_mutate = randint(1, 11)
        if gene_to_mutate == TREETYPE:
            self.mutate_tree_type()
        elif gene_to_mutate == TOPBASECLUSTERSAMOUNT:
            self.mutate_top_base_clusters_amount()
        elif gene_to_mutate == MINTERMOCCURRENCEINCOLLECTION:
            self.mutate_min_term_occurrence()
        elif gene_to_mutate == MAXTERMRATIOINCOLLECTION:
            self.mutate_max_term_ratio()
        elif gene_to_mutate == MINLIMITFORBASECLUSTERSCORE:
            self.mutate_min_limit_bc_score()
        elif gene_to_mutate == MAXLIMITFORBASECLUSTERSCORE:
            self.mutate_max_limit_bc_score()
        elif gene_to_mutate == SHOULDDROPSINGLETONBASECLUSTERS:
            self.mutate_drop_singleton_base_clusters()
        elif gene_to_mutate == SHOULDDROPONEWORDCLUSTERS:
            self.mutate_drop_one_word_clusters()
        elif gene_to_mutate == TEXTTYPE:
            self.mutate_text_types()
        elif gene_to_mutate == TEXTAMOUNT:
            self.mutate_text_amount()
        elif gene_to_mutate == SIMILARITYMEASURE:
            self.mutate_similarity_measure()
        elif gene_to_mutate == SORTDESCENDING:
            self.mutate_sort_descending()
        else:  # Just in case
            pass

    def mutate_tree_type(self):
        """
        Mutate this chromosome's tree type
        """
        treeType = randint(0, 3)
        if treeType == SUFFIX_TREE:
            self.tree_type = (0, self.tree_type[1], self.tree_type[2])
        elif treeType == MID_SLICE:
            self.tree_type = (1, self.tree_type[1], self.tree_type[2])
        elif treeType == RANGE_SLICE:
            self.mutate_range_slice()
        elif treeType == N_SLICE:
            self.mutate_n_slice()

    def mutate_n_slice(self):
        if isinstance(self.tree_type[1], int):
            n_length = self.tree_type[1] + randint(-1, 1)
            if n_length > 10:
                n_length = 10
            elif n_length < 1:
                n_length = 1
            self.tree_type = (3, n_length, self.tree_type[2])
        else:
            self.tree_type = getRandomNSlice()

    def mutate_range_slice(self):
        tree_type = 2  # Set tree type to range slice
        if self.tree_type[1] <= 1 and \
           0 < self.tree_type[2] <= 1:  # Check if dormant genes exist
            min_range = self.tree_type[1] + round(uniform(-.1, .1), 1)
            max_range = self.tree_type[2] + round(uniform(-.1, .1), 1)

            if min_range < 0:
                min_range = 0
            elif min_range > .9:
                min_range = .9

            if max_range < min_range:
                max_range = min_range + .1
            elif max_range > 1:
                max_range = 1

            self.tree_type = (tree_type, min_range, max_range)

        else:
            self.tree_type = getRandomRangeSlice()

    def mutate_top_base_clusters_amount(self):
        new_amount = self.top_base_clusters_amount + randint(-500, 500)
        if 100 < new_amount <+ 10000:
            self.top_base_clusters_amount = new_amount
        elif new_amount > 10000:
            self.top_base_clusters_amount = 10000
        else:
            self.top_base_clusters_amount = 100

    def mutate_min_term_occurrence(self):
        new_min = self.min_term_occurrence_in_collection + randint(-5, 5)

        if new_min < 0:
            new_min = 0
        elif new_min > 150:
            new_min = 150

        self.min_term_occurrence_in_collection = new_min

    def mutate_max_term_ratio(self):
        new_ratio = self.max_term_ratio_in_collection + round(uniform(-.05, .05), 2)
        if new_ratio < 0.05:
            new_ratio = 0.05
        elif new_ratio > 1:
            new_ratio = 1

        self.max_term_ratio_in_collection = new_ratio

    def mutate_min_limit_bc_score(self):
        new_limit = self.min_limit_for_base_cluster_score + randint(-1, 1)

        if 0 <= new_limit < self.max_limit_for_base_cluster_score:
            self.min_limit_for_base_cluster_score = new_limit
        elif new_limit < 0:
            self.min_limit_for_base_cluster_score = 0
        else:
            self.min_limit_for_base_cluster_score = self.max_limit_for_base_cluster_score - 1

    def mutate_max_limit_bc_score(self):
        new_limit = self.max_limit_for_base_cluster_score + randint(-1, 1)

        if self.min_limit_for_base_cluster_score < new_limit <= 20:
            self.max_limit_for_base_cluster_score = new_limit
        elif new_limit <= self.min_limit_for_base_cluster_score:
            self.max_limit_for_base_cluster_score = self.min_limit_for_base_cluster_score + 1
        else:
            self.max_limit_for_base_cluster_score = 20

    def mutate_sort_descending(self):
        self.sort_descending = 0 if self.sort_descending else 1

    def mutate_drop_singleton_base_clusters(self):
        self.should_drop_singleton_base_clusters = 0 if self.should_drop_singleton_base_clusters else 1

    def mutate_drop_one_word_clusters(self):
        self.should_drop_one_word_clusters = 0 if self.should_drop_one_word_clusters else 1

    def mutate_text_amount(self):
        new_amount = self.text_amount + round(uniform(-.1, .1), 2)
        if new_amount > 1:
            new_amount = 1
        elif new_amount < 0:
            new_amount = 0

        self.text_amount = new_amount

    def mutate_text_types(self):
        text_type_keys = list(self.text_types.keys())
        text_type = text_type_keys[randint(0, len(text_type_keys)-1)]
        self.text_types[text_type] = 0 if self.text_types[text_type] else 1

    def mutate_similarity_measure(self):

        similarity_measure = randint(0, 3)

        if similarity_measure == ETZIONI_SIMILARITY:
            self.mutate_etzioni_similarity()
        elif similarity_measure == JACCARD_SIMILARITY:
            self.mutate_jaccard_similarity()
        elif similarity_measure == COSINE_SIMILARITY:
            self.mutate_cosine_similarity()
        elif similarity_measure == AMENDMENT_1C_SIMILARITY:
            self.mutate_amendment_1c_similarity()

    def mutate_etzioni_similarity(self):
        params = self.similarity_measure["params"]
        new_threshold = params[0] + round(uniform(-.1, .1), 2)
        if new_threshold > 1:
            new_threshold = 1
        elif new_threshold < 0:
            new_threshold = 0

        self.similarity_measure["params"] = (new_threshold, params[1], params[2])
        self.similarity_measure["similarity_method"] = 0

    def mutate_jaccard_similarity(self):
        params = self.similarity_measure["params"]
        new_threshold = params[0] + round(uniform(-.1, .1), 2)
        if new_threshold > 1:
            new_threshold = 1
        elif new_threshold < 0:
            new_threshold = 0

        self.similarity_measure["params"] = (new_threshold, params[1], params[2])
        self.similarity_measure["similarity_method"] = 1

    def mutate_cosine_similarity(self):
        params = self.similarity_measure["params"]

        change = round(uniform(-.1, .1), 2)
        rand_param = randint(0, 1)

        if not isinstance(params[1], float):
            new_cosine = round(uniform(0, 1), 2)
        elif rand_param == 1:
            new_cosine = params[1] + change
            if new_cosine > 1:
                new_cosine = 1
            elif new_cosine < 0:
                new_cosine = 0
        else:
            new_cosine = params[1]

        if rand_param == 0:  # Change jaccard threshold
            new_threshold = params[0] + change
            if new_threshold > 1:
                new_threshold = 1
            elif new_threshold < 0:
                new_threshold = 0

        else:
            new_threshold = params[0]

        self.similarity_measure["similarity_method"] = 2
        self.similarity_measure["params"] = (new_threshold, new_cosine, params[2])

    def mutate_amendment_1c_similarity(self):
        params = self.similarity_measure["params"]
        rand_param = randint(0, 2)

        if isinstance(params[1], int) and isinstance(params[2], int):
            self.mutate_existing_amendment_1c(params, rand_param)
        else:
            self.similarity_measure = random_amendment_1c()

        self.similarity_measure["similarity_method"] = 3

    def mutate_existing_amendment_1c(self, params, rand_param):
        if rand_param == 0:
            change = round(uniform(-.1, .1), 2)
            new_threshold = params[0] + change
            if new_threshold > 1:
                new_threshold = 1
            elif new_threshold < 0:
                new_threshold = 0
            self.similarity_measure["params"] = (new_threshold, params[1], params[2])

        elif rand_param == 1:  # Average corpus frequency sum
            change = randint(-10, 10)
            new_average_cf = params[1] + change
            if new_average_cf > 500:
                new_average_cf = 500
            elif new_average_cf < 0:
                new_average_cf = 0
            self.similarity_measure["params"] = (params[0], new_average_cf, params[1])

        elif rand_param == 2:
            change = randint(-5, 5)
            new_intersect_limit = params[2] + change
            if new_intersect_limit > 50:
                new_intersect_limit = 50
            elif new_intersect_limit < 0:
                new_intersect_limit = 0
            self.similarity_measure["params"] = (params[0], params[1], new_intersect_limit)

    def genes_as_tuple(self):
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
    maxLimitForBaseClusterScore = getRandomMaxLimitBCScore(minLimitForBaseClusterScore)
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
    rangeMin = round(uniform(0, .9), 1)
    rangeMax = uniform(.1, 1)
    if rangeMin > rangeMax:
        rangeMin = rangeMax - .1
    return 2, rangeMin, rangeMax


def getRandomNSlice():
    """
    Get a random nslice value
    """
    sliceLength = randint(1, 10)
    return 3, sliceLength, 0


def getRandomTopBaseClustersAmount():
    return randint(100, 10000)


def getRandomMinTermOccurrence():
    return randint(5, 150)


def getRandomMaxTermRatio():
    return round(uniform(0.05, 1.0), 2)


def getRandomMinLimitBCScore():
    return randint(0, 20)


def getRandomMaxLimitBCScore(min_limit):
    max_limit = randint(3, 25)
    if not max_limit < min_limit:
        return max_limit
    else:
        return min_limit + 1


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

    if type == ETZIONI_SIMILARITY:
        similarity_params = {"similarity_method": ETZIONI_SIMILARITY,
                             "params": (threshold, 0, 0)}
    elif type == JACCARD_SIMILARITY:
        similarity_params = {"similarity_method": JACCARD_SIMILARITY,
                             "params": (threshold, 0, 0)}
    elif type == COSINE_SIMILARITY:
        cosine_threshold = round(uniform(0, 1), 2)
        similarity_params = {"similarity_method": COSINE_SIMILARITY,
                             "params": (threshold, cosine_threshold, 0)}

    elif type == AMENDMENT_1C_SIMILARITY:
        similarity_params = random_amendment_1c()

    return similarity_params


def random_amendment_1c():
    avg_cf_threshold = randint(5, 500)
    cf_intersect_min = randint(0, 50)
    similarity_params = {"similarity_method": AMENDMENT_1C_SIMILARITY,
                         "params": (0.5, avg_cf_threshold, cf_intersect_min)}
    return similarity_params


def get_random_sort_descending():
    return randint(0, 1)


def genes_tuple_to_chromosome(geneTuple):
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
    genes1 = chromosome1.genes_as_tuple()
    genes2 = chromosome2.genes_as_tuple()
    crossOverPoint = randint(1, len(genes1) - 1)
    genes12 = genes1[0:crossOverPoint] + genes2[crossOverPoint:len(genes2)]
    genes21 = genes2[0:crossOverPoint] + genes1[crossOverPoint:len(genes1)]

    return [genes_tuple_to_chromosome(genes12),
            genes_tuple_to_chromosome(genes21)]
