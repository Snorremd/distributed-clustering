import os
import sys
from datetime import datetime
from cluster.clusterSettings import ClusterSettings
from cluster.clustering import CompactTrieClusterer
from geneticalgorithm.chromosome import Chromosome
from inputOutput.filehandling import get_corpus_options, get_corpus_settings, get_parameters, write_to_file, append_to_file
from inputOutput.output import show_info_dialog, show_option_dialog

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



def main():
    corpus_settings = find_corpus_settings()
    chromosome = Chromosome(*get_parameters())
    
    cluster_settings = ClusterSettings(True, 1)  # True, drop singleton gt clusters, 1 fbeta-constant
    clusterer = CompactTrieClusterer(corpus_settings, cluster_settings)
    results = clusterer.cluster(chromosome)
    results_filepath = "results" + os.sep + "parameter-test" + str(datetime.now()) + ".txt"

    write_to_file(results_filepath, results.results_string)
    detailed_results = "\n________________________________\n".join(results.clusters_result_strings)
    append_to_file(results_filepath, detailed_results)
    



if __name__ == "__main__":
    main()
