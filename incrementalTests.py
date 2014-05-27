from copy import deepcopy
import os
import sys
import numpy
from cluster.clusterSettings import ClusterSettings
from cluster.clustering import CompactTrieClusterer
from geneticalgorithm.chromosome import Chromosome
from inputOutput.filehandling import get_corpus_options, get_corpus_settings, get_parameters
from inputOutput.output import show_info_dialog, show_option_dialog

__author__ = 'snorre'

TABLE_HEADERS = ";Time;No. Clusters;No. Base Clusters;Precision;Recall;F-Measure;" + \
                "Precision 0;Precision 1;" + \
                "Precision 2;Precision 3;Precision 4;" + \
                "Precision 5;Recall 0;Recall 1;" + \
                "Recall 2;Recall 3;Recall 4;" + \
                "Recall 5;F-Measure 0;F-Measure 1;F-Measure 2;F-Measure 3;" + \
                "F-Measure 4;F-Measure 5"


def find_corpus_settings():
    show_info_dialog("This module lets you test different parameter sets for the\n"
                     "Compact Trie Algorithm. Parameters can be specified in the\n"
                     "testParameters.xml file. The module runs any well formed\n"
                     "snippet file that is specified in the corpora.xml file\n")
    options = get_corpus_options()
    corpus_choice = show_option_dialog(
        "Please choose one of the corpora listed below by typing their name. "
        "If you do not see your preferred corpus among the available options "
        "please add the corpus to the corpora.xml file.",
        options)
    corpus = get_corpus_settings(corpus_choice)
    if not os.path.isfile(corpus.snippetFilePath):
        show_info_dialog("Could not find snippet file. Please make sure there "
                         "is a snippet file with name {0} in directory {1} and"
                         " restart script.".format(corpus.snippetFile,
                                                   corpus.snippetFilePath))
        sys.exit()  # Exit script if no corpus file exist
    else:
        return corpus

def construct_result_tuple(result):
    """
    :type result: cluster.clusterResults.ClusterResult
    :param result:
    :return:
    """
    time_num = (result.time, result.no_of_clusters, result.no_of_base_clusters)
    prec_recall_fmes = (result.precision, result.recall, result.f_measure)
    ground_truths = result.precisions
    ground_truth_rep = result.recalls
    f_measures = result.f_measures
    return time_num, prec_recall_fmes, ground_truths, ground_truth_rep, f_measures


def tupleValuesToStringList(result_tuple):
    string_list = []
    for result in result_tuple:
        if isinstance(result, tuple):
            for item in result:
                string_list.append(str(item))
        else:
            string_list.append(result)
    return string_list


def write_results(resultTuples, filename, header):
    csvFile = open("." + os.sep + "results" + os.sep + "incrementalrichardbase2" + os.sep + filename, "w")
    csvFile.write(header + TABLE_HEADERS + "\n")

    for resultTuple in resultTuples:
        stringList = tupleValuesToStringList(resultTuple)
        line = ";".join(stringList)
        csvFile.write(line + "\n")
    csvFile.close()


def tree_types(clusterer, chromosome):
    """
    Test different tree types
    :param clusterer:
    :param chromosome:
    :return:
    """
    results_trees = []

    ## Calculate with suffixes
    chromosome.tree_type = (0, 0, 0)
    result = construct_result_tuple(clusterer.cluster(chromosome))
    result_tuple = ("Suffix",) + result

    results_trees.append(result_tuple)

    ## Calculate with mid Slices
    chromosome.tree_type = (1, 0, 0)
    result = construct_result_tuple(clusterer.cluster(chromosome))
    result_tuple = ("Midslice",) + result
    results_trees.append(result_tuple)

    ## Calculate with range slices
    chromosome.tree_type = (2, 0.3, 0.8)
    result = construct_result_tuple(clusterer.cluster(chromosome))
    result_tuple = ("Rangeslice 0.1-1.0",) + result
    results_trees.append(result_tuple)

    ## Calculate with 5-gram slices
    chromosome.tree_type = (3, 5, 0)
    result = construct_result_tuple(clusterer.cluster(chromosome))
    result_tuple = ("5-slice",) + result
    results_trees.append(result_tuple)

    def write_tree_results():
        filename = "testTrees.csv"
        header = "Tree type"
        write_results(results_trees, filename, header)

    write_tree_results()


def n_slices(clusterer, chromosome):
    results = []
    for n in range(1, 31):
        chromosome.tree_type = (3, n, 0)
        result = construct_result_tuple(clusterer.cluster(chromosome))
        result_tuple = ("{0}".format(n),) + result
        results.append(result_tuple)

    def write_n_slice_trees():
        filename = "testNSlices.csv"
        header = "n-slice"
        write_results(results, filename, header)

    write_n_slice_trees()


def range_slices(clusterer, chromosome):
    results = []
    for decimal in numpy.arange(0, 0.6, 0.1):
        chromosome.tree_type = (2, decimal, 1 - decimal)
        result = construct_result_tuple(clusterer.cluster(chromosome))
        result_tuple = ("{0}-{1}".format(str(decimal), str(1 - decimal)),) + result
        results.append(result_tuple)

    def write_range_slice_trees():
        filename = "testRangeSlices.csv"
        header = "Range-slice"
        write_results(results, filename, header)

    write_range_slice_trees()


def number_base_clusters(clusterer, chromosome):
    results = []

    def results_in_range(start, stop, step):
        for number in range(start, stop, step):
            chromosome.top_base_clusters_amount = number
            result = construct_result_tuple(clusterer.cluster(chromosome))
            result_tuple = ("{0}".format(number),) + result
            results.append(result_tuple)

    results_in_range(100, 550, 50)
    results_in_range(600, 1100, 100)
    results_in_range(1250, 5250, 250)
    results_in_range(5500, 10500, 500)
    results_in_range(11000, 18000, 1000)

    def write_base_cluster_amounts():
        filename = "testBaseClusterAmounts.csv"
        header = "Basecluster-amount"
        write_results(results, filename, header)

    write_base_cluster_amounts()


def min_term_occurrence(clusterer, chromosome):
    results = []

    def results_in_range(start, stop, step):
        for number in range(start, stop, step):
            chromosome.min_term_occurrence_in_collection = number
            result = construct_result_tuple(clusterer.cluster(chromosome))
            result_tuple = ("{0}".format(number),) + result
            results.append(result_tuple)

    results_in_range(0, 11, 1)
    results_in_range(15, 55, 5)
    results_in_range(60, 110, 10)
    results_in_range(150, 550, 50)
    results_in_range(600, 1100, 100)

    def write_min_term_occurrence():
        filename = "testMinTermOccurrence.csv"
        header = "Min Term Occurrence"
        write_results(results, filename, header)

    write_min_term_occurrence()


def max_term_ratio(clusterer, chromosome):
    results = []

    for ratio in numpy.arange(0.1, 1.05, 0.05):
        chromosome.max_term_ratio_in_collection = ratio
        result = construct_result_tuple(clusterer.cluster(chromosome))
        result_tuple = ("{0}".format(ratio),) + result
        results.append(result_tuple)

    def write_max_term_ratio():
        filename = "testMaxTermRatio.csv"
        header = "Max Term Ratio"
        write_results(results, filename, header)

    write_max_term_ratio()


def min_limit_base_cluster(clusterer, chromosome):
    results = []
    chromosome.max_limit_for_base_cluster_score = 30

    for min_value in range(0, 30):
        chromosome.min_limit_for_base_cluster_score = min_value
        result = construct_result_tuple(clusterer.cluster(chromosome))
        result_tuple = ("{0}".format(min_value),) + result
        results.append(result_tuple)

        def write_min_limit_bc():
            filename = "testMinLimitBC.csv"
            header = "Min Limit"
            write_results(results, filename, header)

    write_min_limit_bc()


def max_limit_base_cluster(clusterer, chromosome):
    results = []
    chromosome.min_limit_for_base_cluster_score = 2

    for max_value in range(3, 31):
        chromosome.max_limit_for_base_cluster_score = max_value
        result = construct_result_tuple(clusterer.cluster(chromosome))
        result_tuple = ("{0}".format(max_value),) + result
        results.append(result_tuple)

    def write_min_limit_bc():
        filename = "testMaxLimitBC.csv"
        header = "Max Limit"
        write_results(results, filename, header)

    write_min_limit_bc()


def max_limit_base_cluster_2(clusterer, chromosome):
    results = []
    chromosome.min_limit_for_base_cluster_score = 8

    for max_value in range(9, 31):
        chromosome.max_limit_for_base_cluster_score = max_value
        result = construct_result_tuple(clusterer.cluster(chromosome))
        result_tuple = ("{0}".format(max_value),) + result
        results.append(result_tuple)

    def write_min_limit_bc():
        filename = "testMaxLimitBC2.csv"
        header = "Max Limit"
        write_results(results, filename, header)

    write_min_limit_bc()

def drop_singleton_base_clusters(clusterer, chromosome):
    results = []

    for value in range(0, 2):
        chromosome.should_drop_singleton_base_clusters = value
        result = construct_result_tuple(clusterer.cluster(chromosome))
        result_tuple = ("{0}".format(value),) + result
        results.append(result_tuple)

    def write_drop_singleton_bc():
        filename = "testDropSingletonBC.csv"
        header = "Drop?"
        write_results(results, filename, header)

    write_drop_singleton_bc()


def drop_one_word_clusters(clusterer, chromosome):
    results = []

    for value in range(0, 2):
        chromosome.should_drop_one_word_clusters = value
        result = construct_result_tuple(clusterer.cluster(chromosome))
        result_tuple = ("{0}".format(value),) + result
        results.append(result_tuple)

    def write_drop_one_word_c():
        filename = "testDropOneWordClusters.csv"
        header = "Drop?"
        write_results(results, filename, header)

    write_drop_one_word_c()


def sort_descending(clusterer, chromosome):
    results = []

    for value in range(0, 2):
        chromosome.sort_descending = value
        result = construct_result_tuple(clusterer.cluster(chromosome))
        result_tuple = ("{0}".format(value),) + result
        results.append(result_tuple)

    def write_sort_descending():
        filename = "testSortDescending.csv"
        header = "Sort descending?"
        write_results(results, filename, header)

    write_sort_descending()


def article_text_amount(clusterer, chromosome):
    results = []

    for ratio in numpy.arange(0, 1.05, 0.05):
        chromosome.text_types["ArticleText"] = 1  # Remember to include article text...
        chromosome.text_amount = ratio
        result = construct_result_tuple(clusterer.cluster(chromosome))
        result_tuple = ("{0}".format(ratio),) + result
        results.append(result_tuple)

    def write_text_amount():
        filename = "testArticleTextAmount.csv"
        header = "Article Text Amount"
        write_results(results, filename, header)

    write_text_amount()


def text_types(clusterer, chromosome):
    """
    Test done with article text set to 0.15
    :param clusterer:
    :param chromosome:
    :return:
    """
    results = []

    chromosome.text_types = {"FrontPageIntroduction": 1,
                             "FrontPageHeading": 1,
                             "ArticleHeading": 1,
                             "ArticleByline": 1,
                             "ArticleIntroduction": 1,
                             "ArticleText": 1}

    result = construct_result_tuple(clusterer.cluster(chromosome))
    result_tuple = ("All",) + result
    results.append(result_tuple)

    chromosome.text_types = {"FrontPageIntroduction": 1,
                             "FrontPageHeading": 1,
                             "ArticleHeading": 0,
                             "ArticleByline": 0,
                             "ArticleIntroduction": 0,
                             "ArticleText": 0}

    result = construct_result_tuple(clusterer.cluster(chromosome))
    result_tuple = ("Frontpage",) + result
    results.append(result_tuple)

    chromosome.text_types = {"FrontPageIntroduction": 0,
                             "FrontPageHeading": 0,
                             "ArticleHeading": 1,
                             "ArticleByline": 1,
                             "ArticleIntroduction": 1,
                             "ArticleText": 0}

    result = construct_result_tuple(clusterer.cluster(chromosome))
    result_tuple = ("Article sans bread text",) + result
    results.append(result_tuple)

    chromosome.text_types = {"FrontPageIntroduction": 0,
                             "FrontPageHeading": 0,
                             "ArticleHeading": 1,
                             "ArticleByline": 1,
                             "ArticleIntroduction": 1,
                             "ArticleText": 1}

    result = construct_result_tuple(clusterer.cluster(chromosome))
    result_tuple = ("Article with bread text",) + result
    results.append(result_tuple)

    chromosome.text_types = {"FrontPageIntroduction": 0,
                             "FrontPageHeading": 0,
                             "ArticleHeading": 0,
                             "ArticleByline": 0,
                             "ArticleIntroduction": 0,
                             "ArticleText": 1}

    result = construct_result_tuple(clusterer.cluster(chromosome))
    result_tuple = ("Article text",) + result
    results.append(result_tuple)

    def write_text_types():
        filename = "testTextTypes.csv"
        header = "Text Types"
        write_results(results, filename, header)

    write_text_types()


def similarity_method(clusterer, chromosome):
    results = []

    chromosome.similarity_measure = {"similarity_method": 0, "params": (0.5, 0, 0)}
    result = construct_result_tuple(clusterer.cluster(chromosome))
    result_tuple = ("Etzioni",) + result
    results.append(result_tuple)

    chromosome.similarity_measure = {"similarity_method": 1, "params": (0.5, 0, 0)}
    result = construct_result_tuple(clusterer.cluster(chromosome))
    result_tuple = ("Jaccard",) + result
    results.append(result_tuple)

    chromosome.similarity_measure = {"similarity_method": 2, "params": (0.5, 0.5, 0)}
    result = construct_result_tuple(clusterer.cluster(chromosome))
    result_tuple = ("Cosine",) + result
    results.append(result_tuple)

    chromosome.similarity_measure = {"similarity_method": 3, "params": (0.5, 5, 1)}
    result = construct_result_tuple(clusterer.cluster(chromosome))
    result_tuple = ("Amendment1C",) + result
    results.append(result_tuple)

    def write_similarity_methods():
        filename = "testSimilarityMethods.csv"
        header = "Similarity Method"
        write_results(results, filename, header)

    write_similarity_methods()


def etzioni_similarity(clusterer, chromosome):
    results = []

    for ratio in numpy.arange(0, 1.05, 0.05):
        chromosome.similarity_measure = {"similarity_method": 0, "params": (ratio, 0, 0)}
        result = construct_result_tuple(clusterer.cluster(chromosome))
        result_tuple = ("{0}".format(ratio),) + result
        results.append(result_tuple)

    def write_etzioni_similarity():
        filename = "testEtzioniSimilarity.csv"
        header = "Threshold"
        write_results(results, filename, header)

    write_etzioni_similarity()

def jaccard_similarity(clusterer, chromosome):
    results = []

    for ratio in numpy.arange(0, 1.05, 0.05):
        chromosome.similarity_measure = {"similarity_method": 1, "params": (ratio, 0, 0)}
        result = construct_result_tuple(clusterer.cluster(chromosome))
        result_tuple = ("{0}".format(ratio),) + result
        results.append(result_tuple)

    def write_jaccard_similarity():
        filename = "testJaccardSimilarity.csv"
        header = "Threshold"
        write_results(results, filename, header)

    write_jaccard_similarity()


def cosine_similarity(clusterer, chromosome):
    results = []

    for ratio in numpy.arange(0, 1.05, 0.05):
        chromosome.similarity_measure = {"similarity_method": 2, "params": (0.5, ratio, 0)}
        result = construct_result_tuple(clusterer.cluster(chromosome))
        result_tuple = ("{0}".format(ratio),) + result
        results.append(result_tuple)

    def write_cosine_similarity():
        filename = "testCosineSimilarity.csv"
        header = "Cosine Threshold"
        write_results(results, filename, header)

    write_cosine_similarity()


def amendment1c_similarity_avg_cf(clusterer, chromosome):
    results = []

    def results_in_range(start, stop, step):
        for limit in range(start, stop, step):
            chromosome.similarity_measure = {"similarity_method": 3, "params": (0.5, limit, 1)}
            result = construct_result_tuple(clusterer.cluster(chromosome))
            result_tuple = ("{0}".format(limit),) + result
            results.append(result_tuple)

    results_in_range(0, 26, 1)
    results_in_range(27, 52, 2)
    results_in_range(55, 105, 5)
    results_in_range(110, 210, 10)
    results_in_range(220, 520, 20)


    def write_cosine_similarity():
        filename = "testAmendment1CSimilarityAvgCF.csv"
        header = "Avg CF limit"
        write_results(results, filename, header)

    write_cosine_similarity()


def amendment1c_similarity_intersect_limit(clusterer, chromosome):
    ## Use 280 as avg corpus frequency limit to not bind limit to avg cf limit
    results = []

    def results_in_range(start, stop, step):
        for limit in range(start, stop, step):
            chromosome.similarity_measure = {"similarity_method": 2, "params": (0.5, 280, limit)}
            result = construct_result_tuple(clusterer.cluster(chromosome))
            result_tuple = ("{0}".format(limit),) + result
            results.append(result_tuple)

    results_in_range(0, 26, 1)
    results_in_range(27, 52, 2)
    results_in_range(55, 105, 5)
    results_in_range(110, 210, 10)
    results_in_range(220, 520, 20)

    def write_cosine_similarity():
        filename = "testAmendment1CSimilarityIntersect.csv"
        header = "Min intersect limit"
        write_results(results, filename, header)

    write_cosine_similarity()

def main():
    corpus_settings = find_corpus_settings()
    cluster_settings = ClusterSettings(False, 1, True)
    clusterer = CompactTrieClusterer(corpus_settings, cluster_settings)

    ## This chromosome represents the base parameter set.
    ## Copy chromosome and change specific parameter to test iteratively
    chromosome = Chromosome(*get_parameters())

    tree_types(clusterer, deepcopy(chromosome))
    n_slices(clusterer, deepcopy(chromosome))
    range_slices(clusterer, deepcopy(chromosome))
    number_base_clusters(clusterer, deepcopy(chromosome))
    min_term_occurrence(clusterer, deepcopy(chromosome))
    max_term_ratio(clusterer, deepcopy(chromosome))
    min_limit_base_cluster(clusterer, deepcopy(chromosome))
    max_limit_base_cluster(clusterer, deepcopy(chromosome))
    max_limit_base_cluster_2(clusterer, deepcopy(chromosome))
    drop_singleton_base_clusters(clusterer, deepcopy(chromosome))
    drop_one_word_clusters(clusterer, deepcopy(chromosome))
    sort_descending(clusterer, deepcopy(chromosome))
    article_text_amount(clusterer, deepcopy(chromosome))
    text_types(clusterer, deepcopy(chromosome))
    similarity_method(clusterer, deepcopy(chromosome))
    etzioni_similarity(clusterer, deepcopy(chromosome))
    jaccard_similarity(clusterer, deepcopy(chromosome))
    cosine_similarity(clusterer, deepcopy(chromosome))
    amendment1c_similarity_avg_cf(clusterer, deepcopy(chromosome))
    amendment1c_similarity_intersect_limit(clusterer, deepcopy(chromosome))


if __name__ == "__main__":
    main()
