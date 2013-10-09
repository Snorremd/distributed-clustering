from copy import deepcopy
import gc
from time import time
from cluster.clusterResults import ClusterResult, calc_overall_precision, calc_overall_recall, calc_overall_fmeasure, calc_tag_accuracy, calc_ground_truth, calc_gt_represented, calc_f_measure
from cluster.compactTrieCluster.baseCluster import top_base_clusters, drop_singleton_base_clusters
from cluster.compactTrieCluster.cluster import generate_clusters
from cluster.compactTrieCluster.compactTrie import generate_compact_trie
from cluster.compactTrieCluster.mergedClusters import merge_components
from cluster.compactTrieCluster.similarity import SimilarityMeasurer
from easylogging.configLogger import get_logger_for_stdout
from inputOutput.filehandling import get_corpus_settings
from text.xmlsnippets import get_snippet_collection, make_tag_index,\
    make_ground_truth_clusters

__author__ = 'snorre'

FRONT_PAGE_HEADING = 0
FRONT_PAGE_INTRODUCTION = 1
ARTICLE_HEADING = 2
ARTICLE_BYLINE = 3
ARTICLE_INTRODUCTION = 4
ARTICLE_TEXT = 5


def text_types():
    """
    Get a list of possible text types
    :rtype: list
    :return: text types
    """
    return ["FrontPageHeading",
            "FrontPageIntroduction",
            "ArticleHeading",
            "ArticleByline",
            "ArticleIntroduction",
            "ArticleText"]


class CompactTrieClusterer(object):

    def __init__(self, corpus, clusterSettings):
        self.logger = get_logger_for_stdout("CompactTrieClusterer")
        self.corpus = get_corpus_settings(corpus.name)
        self.snippetFilePath = self.corpus.name
        self.clusterSettings = clusterSettings
        self.logger.debug("Make indexes and snippet collection")
        self.tagIndex = make_tag_index(corpus.snippetFilePath)
        self.noOfSources = len(self.tagIndex)
        self.groundTruthClusters = \
            make_ground_truth_clusters(corpus.snippetFilePath)
        self.snippetCollection = get_snippet_collection(corpus.snippetFilePath)

        if self.clusterSettings.dropSingletonGTClusters:
            self.groundTruthClusters = drop_singleton_ground_truth_clusters(
                self.groundTruthClusters)


    def cluster(self, chromosome):


        ## Various clustering settings
        tagIndex = self.tagIndex
        filename = self.corpus.snippetFilePath
        groundTruthClusters = self.groundTruthClusters
        fBetaConstant = self.clusterSettings.fBetaConstant

        ## If text types are empty (no text to be included) return empty result
        if not is_nonempty_text_types(chromosome.textTypes):
            return empty_result()

        ## Filter snippet collection based on text types
        snippetCollection = filter_snippets(self.snippetCollection,
                                            chromosome.textTypes)

        start = time()

        ## Build the compact trie structure
        compactTrie = generate_compact_trie(snippetCollection,
                                         chromosome.treeType)

        ## Get base clusters
        base_clusters = top_base_clusters(compactTrie)

        if chromosome.shouldDropSingletonBaseClusters:
            drop_singleton_base_clusters(base_clusters)

        no_of_base_clusters = len(base_clusters)

        if no_of_base_clusters < 2:
            self.logger.info("Can not merge one or fewer base clusters."
                             "Assume score of zero")
            return ClusterResult(
                0, no_of_base_clusters, 0,
                0.0, 0.0, 0.0,
                (.0, .0, .0, .0, .0, .0),
                (.0, .0, .0, .0, .0, .0),
                (.0, .0, .0, .0, .0, .0))

        ## Helper object that measures similarity between base clusters
        similarity_measurer = SimilarityMeasurer(0, {"threshold": .5})

        merged_components = merge_components(base_clusters, similarity_measurer)

        clusters = generate_clusters(merged_components)

        stop = time()

        time_to_cluster = stop - start

        no_of_clusters = len(clusters)

        return self.calculate_results(clusters, groundTruthClusters,
                                      no_of_base_clusters, no_of_clusters,
                                      tagIndex, time_to_cluster)

    def calculate_results(self, clusters, groundTruthClusters,
                          no_of_base_clusters, no_of_clusters, tagIndex,
                          time_to_cluster):
        """
        Calculate two forms of results. Standard precision,
        recall and f-measure scores as done in ....
        """
        precision = calc_overall_precision(groundTruthClusters,
                                           clusters,
                                           self.noOfSources)
        recall = calc_overall_recall(groundTruthClusters,
                                     clusters,
                                     self.noOfSources)
        f_measure = calc_overall_fmeasure(groundTruthClusters,
                                          clusters,
                                          self.noOfSources,
                                          self.clusterSettings.fBetaConstant)
        tag_accuracy = calc_tag_accuracy(clusters,
                                         no_of_clusters,
                                         tagIndex)
        tag_accuracy_tuple = make_result_tuple(tag_accuracy, 2)

        ground_truths = calc_ground_truth(clusters,
                                          no_of_clusters,
                                          groundTruthClusters,
                                          tagIndex)
        ground_truth_tuple = make_result_tuple(ground_truths, 2)

        ground_truth_represented = calc_gt_represented(clusters,
                                                       groundTruthClusters,
                                                       tagIndex)
        ground_truth_represented_tuple = \
            make_result_tuple(ground_truth_represented, 2)

        f_measures = calc_f_measure(ground_truths,
                                    ground_truth_represented,
                                    self.clusterSettings.fBetaConstant)
        f_measure_tuple = make_result_tuple(f_measures, 1)



        results = ClusterResult(time_to_cluster, no_of_base_clusters,
                                no_of_clusters, precision, recall, f_measure,
                                tag_accuracy_tuple, ground_truth_tuple,
                                ground_truth_represented_tuple,
                                f_measure_tuple)
        return results


def make_result_tuple(results_list, position):
    """
    Takes a list of tuple results on the form (discrepancy, .......) and
    converts it to a one dimensional tuple (result0, result1, .., result5)
    :param results_list:
    :param position:
    :return:
    """
    result_tuple = ()
    for results_overlap_x in results_list:
        # Get the fraction of clusters to the total amount...
        result_tuple += (results_overlap_x[position],)
    return result_tuple


def drop_singleton_ground_truth_clusters(groundTruthClusters):
    """
    :type groundTruthClusters: dict
    :param groundTruthClusters: index of ground truth clusters on the form: {
    "tags": [
    "source1", ..., "sourceX"], ..., "tags": [...]}
    :rtype: dict
    :return: a filtered index of non-singleton ground truth clusters
    """
    newIndex = {}
    for tags in list(groundTruthClusters.keys()):
        sources = groundTruthClusters[tags]
        if len(sources) > 1:
            newIndex[tags] = sources
    return newIndex


def is_nonempty_text_types(textTypes):
    """
    Utility method to check if no text types are to be included
    :param textTypes: key value pairs for text type inclusion
    :type textTypes: dict
    :return: true if all text types are set to false, false if not
    :rtype: bool
    """
    nonempty = False
    for value in list(textTypes.values()):
        if value:
            nonempty = True
    return nonempty


def empty_result():
    """
    Convenience method for empty result
    :rtype: tuple
    :return: empty result set
    """
    return ClusterResult(
        0, 0, 0, .0, .0, .0,
        (.0, .0, .0, .0, .0),
        (.0, .0, .0, .0, .0, .0),
        (.0, .0, .0, .0, .0, .0),
        (.0, .0, .0, .0, .0, .0))


def filter_snippets(snippetCollection, textTypes):
    """

    :type snippetCollection: dict
    :param snippetCollection: snippets to filter based on type
    :type textTypes: dict
    :param textTypes: boolean values for inclusion/exclusion of text types
    :rtype: list
    :return: list of snippet, [source]-pairs.
    """
    filteredCollection = list()
    for textType, snippets in snippetCollection.items():
        if textTypes[textType]:  # If text type is true, do include
            filteredCollection.extend(snippets)
    return filteredCollection