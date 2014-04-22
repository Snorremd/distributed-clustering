import os
import sys
from cluster.clusterResults import ClusterResult
from cluster.clusterSettings import ClusterSettings
from cluster.clustering import CompactTrieClusterer, make_results_string
from inputOutput.filehandling import get_corpus_options, get_corpus_settings, write_to_file, append_to_file
from inputOutput.output import show_info_dialog, show_option_dialog
from geneticalgorithm.chromosome import create_random_chromosome, Chromosome

__author__ = 'snorre'

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


def average_string(type, iterable):
    result_string = "Type & Percentage \\\ \n"

    iterator = 0

    for value in iterable:
        result_string += type + "-" + str(iterator) + " & " + str(value) + "\\\ \n"
        iterator += 1

    result_string += "\n"

    return result_string



if __name__ == "__main__":

    tag_accuracy_0_total = 0
    tag_accuracy_1_total = 0
    tag_accuracy_2_total = 0
    tag_accuracy_3_total = 0
    tag_accuracy_4_total = 0
    tag_accuracy_5_total = 0

    precision_0_total = 0
    precision_1_total = 0
    precision_2_total = 0
    precision_3_total = 0
    precision_4_total = 0
    precision_5_total = 0

    recall_0_total = 0
    recall_1_total = 0
    recall_2_total = 0
    recall_3_total = 0
    recall_4_total = 0
    recall_5_total = 0

    f_measure_0_total = 0
    f_measure_1_total = 0
    f_measure_2_total = 0
    f_measure_3_total = 0
    f_measure_4_total = 0
    f_measure_5_total = 0

    time_total = 0
    no_of_clusters_total = 0
    no_of_baseclusters_total = 0

    no_of_gt_clusters = 0

    corpus_settings = find_corpus_settings()

    numberOfSets = 100
    for i in range(numberOfSets):

        chromosome = create_random_chromosome()

        # Drop singleton ground truth clusters: True, fbeta-constant: 1, store_result_details: true
        cluster_settings = ClusterSettings(False, 1, True)
        clusterer = CompactTrieClusterer(corpus_settings, cluster_settings)
        results = clusterer.cluster(chromosome)

        results_filepath = "results" + os.sep + "randomized" + os.sep + "random" + str(i) + ".txt"
        write_to_file(results_filepath, results.results_string)
        detailed_results = "\n________________________________\n".join(results.clusters_result_strings)
        append_to_file(results_filepath, detailed_results)

        print(chromosome.genes_as_tuple())

        tag_accuracy_0_total += results.tag_accuracies[0]
        tag_accuracy_1_total += results.tag_accuracies[1]
        tag_accuracy_2_total += results.tag_accuracies[2]
        tag_accuracy_3_total += results.tag_accuracies[3]
        tag_accuracy_4_total += results.tag_accuracies[4]
        tag_accuracy_5_total += results.tag_accuracies[5]

        precision_0_total += results.precisions[0]
        precision_1_total += results.precisions[1]
        precision_2_total += results.precisions[2]
        precision_3_total += results.precisions[3]
        precision_4_total += results.precisions[4]
        precision_5_total += results.precisions[5]

        recall_0_total += results.recalls[0]
        recall_1_total += results.recalls[1]
        recall_2_total += results.recalls[2]
        recall_3_total += results.recalls[3]
        recall_4_total += results.recalls[4]
        recall_5_total += results.recalls[5]

        f_measure_0_total += results.f_measures[0]
        f_measure_1_total += results.f_measures[1]
        f_measure_2_total += results.f_measures[2]
        f_measure_3_total += results.f_measures[3]
        f_measure_4_total += results.f_measures[4]
        f_measure_5_total += results.f_measures[5]

        time_total += results.time
        no_of_clusters_total += results.no_of_clusters
        no_of_baseclusters_total += results.no_of_base_clusters

        no_of_gt_clusters = results.no_of_gt_clusters

    tag_accuracy_0_avg = tag_accuracy_0_total / numberOfSets
    tag_accuracy_1_avg = tag_accuracy_1_total / numberOfSets
    tag_accuracy_2_avg = tag_accuracy_2_total / numberOfSets
    tag_accuracy_3_avg = tag_accuracy_3_total / numberOfSets
    tag_accuracy_4_avg = tag_accuracy_4_total / numberOfSets
    tag_accuracy_5_avg = tag_accuracy_5_total / numberOfSets

    precision_0_avg = precision_0_total / numberOfSets
    precision_1_avg = precision_1_total / numberOfSets
    precision_2_avg = precision_2_total / numberOfSets
    precision_3_avg = precision_3_total / numberOfSets
    precision_4_avg = precision_4_total / numberOfSets
    precision_5_avg = precision_5_total / numberOfSets

    recall_0_avg = recall_0_total / numberOfSets
    recall_1_avg = recall_1_total / numberOfSets
    recall_2_avg = recall_2_total / numberOfSets
    recall_3_avg = recall_3_total / numberOfSets
    recall_4_avg = recall_4_total / numberOfSets
    recall_5_avg = recall_5_total / numberOfSets

    f_measure_0_avg = f_measure_0_total / numberOfSets
    f_measure_1_avg = f_measure_1_total / numberOfSets
    f_measure_2_avg = f_measure_2_total / numberOfSets
    f_measure_3_avg = f_measure_3_total / numberOfSets
    f_measure_4_avg = f_measure_4_total / numberOfSets
    f_measure_5_avg = f_measure_5_total / numberOfSets

    time_avg = time_total / numberOfSets
    no_of_clusters_avg = no_of_clusters_total / numberOfSets
    no_of_base_clusters_avg = no_of_baseclusters_total / numberOfSets

    results_avg = ClusterResult(time_avg, no_of_base_clusters_avg, no_of_clusters_avg,
                                no_of_gt_clusters, 0, 0, 0,
                                [tag_accuracy_0_avg, tag_accuracy_1_avg, tag_accuracy_2_avg,
                                 tag_accuracy_3_avg, tag_accuracy_4_avg, tag_accuracy_5_avg],
                                [precision_0_avg, precision_1_avg, precision_2_avg,
                                 precision_3_avg, precision_4_avg, precision_5_avg],
                                [recall_0_avg, recall_1_avg, recall_2_avg,
                                 recall_3_avg, recall_4_avg, recall_5_avg],
                                [f_measure_0_avg, f_measure_1_avg, f_measure_2_avg,
                                 f_measure_3_avg, f_measure_4_avg, f_measure_5_avg], "", "")


    results_string = "Average results for {} number of random parameter sets:".format(numberOfSets)
    results_string += "-------------------------------------------------------"

    results_string += average_string("tag-accuracy", results_avg.precisions)
    results_string += average_string("precision", results_avg.tag_accuracies)
    results_string += average_string("recall", results_avg.recalls)
    results_string += average_string("precision", results_avg.f_measures)

    results_file_path = "results" + os.sep + "randomized" + os.sep + "average.txt"
    write_to_file(results_file_path, results_string)