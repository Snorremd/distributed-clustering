from random import randint
from time import time
from cluster.clusterResults import ClusterResult, calc_overall_precision, calc_overall_recall, calc_overall_fmeasure, \
    calc_tag_accuracy, calc_ground_truth, calc_gt_represented, calc_f_measure, sort_clusters
from cluster.compactTrieCluster.baseCluster import top_base_clusters, drop_singleton_base_clusters
from cluster.compactTrieCluster.cluster import generate_clusters, drop_one_word_clusters
from cluster.compactTrieCluster.compactTrie import generate_compact_trie
from cluster.compactTrieCluster.mergedClusters import merge_components
from cluster.compactTrieCluster.similarity import SimilarityMeasurer
from easylogging.configLogger import get_logger_for_stdout
from inputOutput.filehandling import get_corpus_settings
from text.wordOccurrence import get_word_frequencies
from text.xmlsnippets import get_snippet_collection, make_tag_index, \
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
    def __init__(self, corpus, cluster_settings):
        self.logger = get_logger_for_stdout("CompactTrieClusterer")
        self.corpus = get_corpus_settings(corpus.name)
        self.snippet_file_path = self.corpus.snippetFilePath
        self.cluster_settings = cluster_settings
        self.logger.debug("Make indexes and snippet collection")
        self.tag_index = make_tag_index(self.snippet_file_path)
        self.no_of_sources = len(self.tag_index)
        self.ground_truth_clusters = \
            make_ground_truth_clusters(self.snippet_file_path)
        self.snippet_collection, self.no_of_sources = \
            get_snippet_collection(self.snippet_file_path)
        self.word_frequencies = get_word_frequencies(self.snippet_collection, self.no_of_sources)

        if self.cluster_settings.dropSingletonGTClusters:
            self.ground_truth_clusters = drop_singleton_ground_truth_clusters(
                self.ground_truth_clusters)

    def cluster(self, chromosome):

        self.logger.info("Cluster corpus {0} with parameter set:\n{1}".format(self.corpus.name,
                                                                              chromosome.genesAsTuple()))

        ## Various clustering settings
        tag_index = self.tag_index
        ground_truth_clusters = self.ground_truth_clusters

        ## If text types are empty (no text to be included) return empty result
        if not is_nonempty_text_types(chromosome.text_types):
            return empty_result()

        ## Filter snippet collection based on text types
        snippet_collection = filter_snippets(self.snippet_collection,
                                             chromosome.text_types,
                                             chromosome.text_amount)

        start = time()

        ## Build the compact trie structure
        compact_trie = generate_compact_trie(snippet_collection,
                                             chromosome.tree_type)

        ## Get base clusters
        self.logger.info("Generate top base clusters")
        base_clusters = top_base_clusters(compact_trie,
                                          chromosome.top_base_clusters_amount,
                                          chromosome.min_term_occurrence_in_collection,
                                          chromosome.max_term_ratio_in_collection,
                                          chromosome.min_limit_for_base_cluster_score,
                                          chromosome.max_limit_for_base_cluster_score,
                                          chromosome.sort_descending)

        if chromosome.should_drop_singleton_base_clusters:
            drop_singleton_base_clusters(base_clusters)

        no_of_base_clusters = len(base_clusters)

        if no_of_base_clusters < 2:
            self.logger.info("Can not merge one or fewer base clusters."
                             "Assume score of zero")
            return ClusterResult(
                0, no_of_base_clusters, 0, len(self.ground_truth_clusters),
                0.0, 0.0, 0.0,
                (.0, .0, .0, .0, .0, .0),
                (.0, .0, .0, .0, .0, .0),
                (.0, .0, .0, .0, .0, .0),
                (.0, .0, .0, .0, .0, .0), "empty", "empty")

        ## Helper object that measures similarity between base clusters
        similarity_measurer = SimilarityMeasurer(chromosome.similarity_measure,
                                                 self.no_of_sources,
                                                 self.word_frequencies[0],
                                                 self.word_frequencies[1],
                                                 self.word_frequencies[2])

        self.logger.info("Merge {0} base clusters and make cluster components".format(no_of_base_clusters))
        merged_components = merge_components(base_clusters, similarity_measurer)

        clusters = generate_clusters(merged_components)

        if chromosome.should_drop_one_word_clusters:
            clusters = drop_one_word_clusters(clusters)
        stop = time()

        time_to_cluster = stop - start
        self.logger.info("Made {0} clusters in {1} seconds".format(len(clusters), time_to_cluster))

        no_of_clusters = len(clusters)
        if no_of_clusters == 0:
            return ClusterResult(
                no_of_clusters, no_of_base_clusters, len(self.ground_truth_clusters),
                0, 0.0, 0.0, 0.0,
                (.0, .0, .0, .0, .0, .0),
                (.0, .0, .0, .0, .0, .0),
                (.0, .0, .0, .0, .0, .0),
                (.0, .0, .0, .0, .0, .0), "empty", "empty")

        self.logger.info("Calculate results")
        return self.calculate_results(clusters, ground_truth_clusters,
                                      no_of_base_clusters, no_of_clusters,
                                      tag_index, time_to_cluster, chromosome)

    def calculate_results(self, clusters, ground_truth_clusters,
                          no_of_base_clusters, no_of_clusters, tag_index,
                          time_to_cluster, chromosome):
        """
        Calculate two forms of results. Standard precision,
        recall and f-measure scores as done in ....
        """
        precision = calc_overall_precision(ground_truth_clusters,
                                           clusters,
                                           self.no_of_sources)
        recall = calc_overall_recall(ground_truth_clusters,
                                     clusters,
                                     self.no_of_sources)
        f_measure = calc_overall_fmeasure(ground_truth_clusters,
                                          clusters,
                                          self.no_of_sources,
                                          self.cluster_settings.fBetaConstant)
        tag_accuracy = calc_tag_accuracy(clusters,
                                         no_of_clusters,
                                         tag_index)
        tag_accuracy_tuple = make_result_tuple(tag_accuracy, 2)

        ground_truths = calc_ground_truth(clusters,
                                          no_of_clusters,
                                          ground_truth_clusters,
                                          tag_index)
        ground_truth_tuple = make_result_tuple(ground_truths, 2)

        ground_truth_represented = calc_gt_represented(clusters,
                                                       ground_truth_clusters,
                                                       tag_index)
        ground_truth_represented_tuple = \
            make_result_tuple(ground_truth_represented, 2)

        f_measures = calc_f_measure(ground_truths,
                                    ground_truth_represented,
                                    self.cluster_settings.fBetaConstant)
        f_measure_tuple = make_result_tuple(f_measures, 1)

        sorted_clusters = sort_clusters(clusters, tag_index, ground_truth_clusters)

        param_string = make_parameter_string(chromosome)

        results_string = param_string + \
            "\n\n" + \
            make_results_string(tag_accuracy, ground_truths, ground_truth_represented,
                                no_of_clusters, len(ground_truth_clusters))

        clusters_result_strings = make_clusters_details_string(sorted_clusters, tag_index)

        results = ClusterResult(time_to_cluster, no_of_base_clusters,
                                no_of_clusters, len(self.ground_truth_clusters),
                                precision, recall, f_measure,
                                tag_accuracy_tuple, ground_truth_tuple,
                                ground_truth_represented_tuple,
                                f_measure_tuple, results_string, clusters_result_strings)

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


def drop_singleton_ground_truth_clusters(ground_truth_clusters):
    """
    :type ground_truth_clusters: dict
    :param ground_truth_clusters: index of ground truth clusters on the form: {
    "tags": [
    "source1", ..., "sourceX"], ..., "tags": [...]}
    :rtype: dict
    :return: a filtered index of non-singleton ground truth clusters
    """
    new_index = {}
    for tags in list(ground_truth_clusters.keys()):
        sources = ground_truth_clusters[tags]
        if len(sources) > 1:
            new_index[tags] = sources
    return new_index


def is_nonempty_text_types(text_types_dict):
    """
    Utility method to check if no text types are to be included
    :param text_types_dict: key value pairs for text type inclusion
    :type text_types_dict: dict
    :return: true if all text types are set to false, false if not
    :rtype: bool
    """
    nonempty = False
    for value in list(text_types_dict.values()):
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
        0, 0, 0, 0, .0, .0, .0,
        (.0, .0, .0, .0, .0, .0),
        (.0, .0, .0, .0, .0, .0),
        (.0, .0, .0, .0, .0, .0),
        (.0, .0, .0, .0, .0, .0), "empty", "empty")


def filter_snippets(snippet_collection, text_types_dict, text_amount):
    """

    :type snippet_collection: dict
    :param snippet_collection: snippets to filter based on type
    :type text_types_dict: dict
    :param text_types_dict: boolean values for inclusion/exclusion of text types
    :rtype: list
    :return: list of snippet, [source]-pairs.
    """
    filtered_collection = list()
    for textType, snippets in snippet_collection.items():
        if text_types_dict['ArticleText']:
            amount = int(len(snippets) / text_amount)
            snippets = snippets[:amount-1]
        if text_types_dict[textType]:  # If text type is true, do include
            filtered_collection.extend(snippets[:])
    return filtered_collection


def random_snippets(snippets, amount):
    """
    Return random amount selection of snippets from snippets list
    """
    result = [snippets[0]]
    del snippets[0]
    counter = 1
    while len(snippets) > 0 and counter < amount:
        random_pos = randint(0, len(snippets) - 1)
        result.append(snippets[random_pos])
        del snippets[random_pos]

    return result


def make_results_string(resultsTagAccuracy,
                        resultsGroundTruth,
                        resultsGroundTruthRep,
                        noOfClusters,
                        noOfGTClusters):
    tagAccuracy = "Tag Accuracy:\n"
    tagAccuracy += "Overlap - Number/NoClusters - Fraction - Accumulated\n"
    tagAccuracy += "----------------------------------------------------\n"
    for (i, countMatch, fraction, accumulated) in resultsTagAccuracy:
        tagAccuracy += str(i) + "\t %2i" % (countMatch) + "/" + \
                       str(noOfClusters) + \
                       "\t\t%.3f" % (fraction) + "\t " + \
                       "%.3f" % (accumulated) + "\n"

    groundTruthString = "Ground truth:\n"
    groundTruthString += "Overlap - Number/NoClusters - Fraction - Accumulated\n"
    groundTruthString += "----------------------------------------------------\n"
    for (i, countMatch, fraction, accumulated) in resultsGroundTruth:
        groundTruthString += str(i) + "\t %2i" % (countMatch) + "/" + \
                             str(noOfClusters) + \
                             "\t\t%.3f" % (fraction) + "\t " + \
                             "%.3f" % (accumulated) + "\n"

    groundTruthRepString = "Ground truth represented:\n"
    groundTruthRepString += "Overlap - Number/NoClusters - Fraction - Accumulated\n"
    groundTruthRepString += "----------------------------------------------------\n"
    for (i, countMatch, fraction, accumulated) in resultsGroundTruthRep:
        groundTruthRepString += str(i) + "\t %2i" % (countMatch) + "/" + \
                                str(noOfGTClusters) + \
                                "\t\t%.3f" % (fraction) + "\t " + \
                                "%.3f" % (accumulated) + "\n"

    return tagAccuracy + "\n" + groundTruthString + "\n" + groundTruthRepString


def make_clusters_details_string(sorted_clusters, tag_index):

    sorted_clusters_result_strings = []
    for cluster in sorted_clusters:
        cluster_string = \
            ("\n"
             "{0}/{1}\n"
             "< {2} > :\n"
            ).format(cluster.tag_accuracy,
                     cluster.cluster.number_of_sources,
                     cluster.cluster.label)
        if cluster.ground_truth_best_match == 5:
            cluster_string = " ".join("*", cluster_string)

        for source in cluster.cluster.sources:
            cluster_string += "  {0}\n".format(tag_index[source])

        cluster_string += "\n"
        cluster_string += str(cluster.cluster)
        cluster_string += "\n---------------------\n"
        sorted_clusters_result_strings.append(cluster_string)

    return sorted_clusters_result_strings


def make_parameter_string(chromosome):
    param_string = "###################################\n" \
                   "Parameter set for clustering:\n\n"

    tree_type = ""
    if chromosome.tree_type[0] == 0:
        tree_type = "Suffix Tree"
    elif chromosome.tree_type[0] == 1:
        tree_type = "Midslice trie"
    elif chromosome.tree_type == 2:
        tree_type = "{0}-slice trie".format(chromosome.tree_type[1])
    elif chromosome.tree_type == 3:
        tree_type = "Range-slice trie (min = {0}, max = {1}".format(
            chromosome.tree_type[1], chromosome.tree_type[2]
        )

    top_base_cluster = "Top base clusters: {0}".format(chromosome.top_base_clusters_amount)

    min_max_term_occurrence = "Min term occurrence: {0}, Max term ratio: {1}".format(
        chromosome.min_term_occurrence_in_collection,
        chromosome.max_term_ratio_in_collection
    )

    min_max_limit_bc_score = "Min & Max limit bc score: {0}, {1}".format(
        chromosome.min_limit_for_base_cluster_score,
        chromosome.max_limit_for_base_cluster_score
    )

    if chromosome.sort_descending:
        base_cluster_sort = "Sort base cluster: {0} first".format("best")
    else:
        base_cluster_sort = "Sort base cluster: {0} first".format("worst")

    drop_clusters = "Drop clusters:"
    if chromosome.should_drop_singleton_base_clusters:
        drop_clusters += "\n\tSingleton Base Clusters"
    if chromosome.should_drop_one_word_clusters:
        drop_clusters += "\n\tOne Word Clusters"
    drop_clusters += "\n"

    text_types = "Text types: "
    for (text_type, include) in chromosome.text_types.items():
        if include:
            text_types += text_type + ", "

    text_amount = "Amount of article text: {0}".format(chromosome.text_amount)

    similarity_measure = "Similarity measure: "
    if chromosome.similarity_measure["similarity_method"] == 0:
        similarity_measure = "Jaccard similarity, threshold: {0}".format(chromosome.similarity_measure["params"][0])
    elif chromosome.similarity_measure["similarity_method"] == 1:
        similarity_measure = "Jaccard similarity, threshold: {0}\n"
        similarity_measure += "Cosine similarity, cos-threshold {1}"
        similarity_measure.format(chromosome.similarity_measure["params"][0],
                                  chromosome.similarity_measure["params"][1]
                                  )
    elif chromosome.similarity_measure["similarity_method"] == 2:
        similarity_measure = "Jaccard Similarity, Threshold: {0}\n".format(chromosome.similarity_measure["params"][0])
        similarity_measure += \
            "Amendment 1d Similarity, max corpus frequency avg = {0}, min label intersect = {1}".format(
                chromosome.similarity_measure["params"][1], chromosome.similarity_measure["params"][2]
            )

    param_string += "\n".join([tree_type, top_base_cluster, min_max_term_occurrence, min_max_limit_bc_score,
                               base_cluster_sort, drop_clusters, text_types, text_amount, similarity_measure])

    return param_string