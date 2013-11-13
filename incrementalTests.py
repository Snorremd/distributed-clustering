from copy import deepcopy
import os
import sys
from cluster.clusterSettings import ClusterSettings
from cluster.clustering import CompactTrieClusterer
from geneticalgorithm.chromosome import Chromosome
from inputOutput.filehandling import get_corpus_options, get_corpus_settings, get_parameters
from inputOutput.output import show_info_dialog, show_option_dialog

__author__ = 'snorre'

TABLE_HEADERS = ";Precision;recall;F-Measure;Time;No. Clusters;" + \
               "No. Base Clusters;Ground Truth 0;Ground Truth 1;" + \
               "Ground Truth 2;Ground Truth 3;Ground Truth 4;" + \
               "Ground Truth 5;Ground Truth Rep 0;Ground Truth Rep 1;" + \
               "Ground Truth Rep 2;Ground Truth Rep 3;Ground Truth Rep 4;" + \
               "Ground Truth Rep 5;fMeasure 1;fMeasure 2;fMeasure 3;" + \
               "fMeasure 4;fMeasure 5"


def find_corpus_settings():
    show_info_dialog("This module lets you test different parameter sets for the\n"
                     "Compact Trie Algoritm. Parameters can be specified in the\n"
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


def tupleValuesToStringList(resultTuple):
    stringList = []
    for result in resultTuple:
        if isinstance(result, tuple):
            for item in result:
                stringList.append(str(item))
        else:
            stringList.append(result)
    return stringList


def writeResults(resultTuples, filename, header):
    csvFile = open("." + os.sep + "results" + os.sep + "incremental" + os.sep + filename, "w")
    csvFile.write(header + TABLE_HEADERS + "\n")

    for resultTuple in resultTuples:
        stringList = tupleValuesToStringList(resultTuple)
        line = ";".join(stringList)
        csvFile.write(line + "\n")
    csvFile.close()


def tree_types(clusterer, chromosome):
    resultsTrees = []

    ## Calculate with suffixes
    chromosome.tree_type = (0, 0, 0)
    result = construct_result_tuple(clusterer.cluster(chromosome))
    resultTuple = ("Suffix",) + result

    resultsTrees.append(resultTuple)

    ## Calculate with mid Slices
    chromosome.tree_type = (1, 0, 0)
    result = construct_result_tuple(clusterer.cluster(chromosome))
    resultTuple = ("Midslice",) + result
    resultsTrees.append(resultTuple)

    ## Calculate with range slices
    chromosome.tree_type = (2, 0.1, 1.0)
    result = construct_result_tuple(clusterer.cluster(chromosome))
    resultTuple = ("Rangeslice 0.1-1.0",) + result
    resultsTrees.append(resultTuple)

    ## Calculate with 5-gram slices
    chromosome.tree_type = (3, 5, 0)
    result = construct_result_tuple(clusterer.cluster(chromosome))
    resultTuple = ("5-slice",) + result
    resultsTrees.append(resultTuple)


    def writeTreeResults(resultsTrees):
        filename = "testTrees.csv"
        header = "Tree type"
        writeResults(resultsTrees, filename, header)

    writeTreeResults(resultsTrees)

def main():
    corpus_settings = find_corpus_settings()
    cluster_settings = ClusterSettings(False, 1, True)
    clusterer = CompactTrieClusterer(corpus_settings, cluster_settings)

    ## This chromosome represents the base parameter set.
    ## Copy chromosome and change specific parameter to test iteratively
    chromosome = Chromosome(*get_parameters())

    tree_types(clusterer, deepcopy(chromosome))





if __name__ == "__main__":
    main()
