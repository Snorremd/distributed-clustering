from corpora.corpus import Corpus

__author__ = 'Snorre Magnus Davoeen'

import sys
import os
import ntpath
from xml.etree import ElementTree as ET


def get_root_path():
    pathToMain = os.path.abspath(sys.modules['__main__'].__file__)
    return sep_file_and_path(pathToMain)[0]


def sep_file_and_path(path):

    """Handle paths with ending slash
    :type path: str
    :param path: the path to separate
    :return: filename and path tuple
    :rtype: tuple
    """
    head, tail = ntpath.split(path)
    return head, tail or ntpath.split(head)


def get_server_config():
    configTree = ET.parse(get_root_path() + os.sep + "serverConfig.xml")
    options = []
    for setting in configTree.getroot():
        options.append(setting.text)
    return options


def get_client_config():
    configTree = ET.parse(get_root_path() + os.sep + "clientConfig.xml")
    options = []
    for setting in configTree.getroot():
        options.append(setting.text)
    return options


def get_corpus_options():
    corpusTree = ET.parse(get_root_path() + os.sep + "corpora.xml")
    options = []
    for corpus in corpusTree.getroot().findall("corpus"):
        options.append(corpus.get('name'))
    return options


def get_corpus_settings(choice):
    """
    Given a corpus name, get all settings for that corpus

    :type choice: str
    :param choice: corpus name
    :rtype: Corpus
    :return: A corpus object with all settings for given corpus
    """
    ## Get path of corpus and snippet files from corpora.xml
    corpusTree = ET.parse(get_root_path() + os.sep + "corpora.xml")
    corpusSettings = corpusTree.getroot().findall(
        ".corpus[@name='{0}']".format(choice))[0]

    corpusPath = get_root_path() + os.sep + "corpusfiles" + os.sep
    corpusPath += corpusSettings.findall(".directory")[0].text
    corpusFile = corpusSettings.findall(".corpusfile")[0].text
    corpusFilePath = corpusPath + os.sep + corpusFile
    snippetFile = corpusSettings.findall(".snippetfile")[0].text
    snippetFilePath = corpusPath + os.sep + snippetFile

    ## Get processor name
    processorName = corpusSettings.findall(".processorname")[0].text

    ## Is corpus single tag?
    singleTag = corpusSettings.findall(".singletag")[0].text
    if singleTag == "True":
        singleTag = True
    elif singleTag == "False":
        singleTag = False
    else:
        singleTag = False ## Assume the best...

    corpus = Corpus(choice, snippetFilePath, snippetFile, corpusFilePath,
                    corpusFile, processorName, singleTag)

    return corpus


def get_parameters():
    """
    Reads the textParameters.xml file to load a parameter
    set into a chromosome which can then be used to cluster
    a snippet file.
    :rtype: Chromosome
    :return: A chromosome object with parameters
    """
    ## Get parameters for CTC from testParameters.xml
    paramsTree = ET.parse(get_root_path() + os.sep + "testParameters.xml")
    params = paramsTree.getroot()
    print(str(params))

    tree_types = eval(params.findall(".tree_type")[0].text)  # Eval text to tuple
    top_base_clusters_amount = int(params.findall(".top_base_clusters_amount")[0].text)
    min_term_occurrence_in_collection = int(params.findall(".min_term_occurrence_in_collection")[0].text)
    max_term_ratio_in_collection = float(params.findall(".max_term_ratio_in_collection")[0].text)
    min_limit_for_base_cluster_score = int(params.findall(".min_limit_for_base_cluster_score")[0].text)
    max_limit_for_base_cluster_score = int(params.findall(".max_limit_for_base_cluster_score")[0].text)
    should_drop_singleton_base_clusters = int(params.findall(".should_drop_singleton_base_clusters")[0].text)
    should_drop_one_word_clusters = int(params.findall(".should_drop_one_word_clusters")[0].text)
    text_amount = float(params.findall(".text_amount")[0].text)
    text_types = eval(params.findall(".text_types")[0].text)
    similarity_measure = eval(params.findall(".similarity_measure")[0].text)
    sort_descending = int(params.findall(".sort_descending")[0].text)

    return (tree_types, top_base_clusters_amount, min_term_occurrence_in_collection,
            max_term_ratio_in_collection, min_limit_for_base_cluster_score,
            max_limit_for_base_cluster_score, should_drop_singleton_base_clusters,
            should_drop_one_word_clusters, text_types, text_amount, similarity_measure, sort_descending)

def write_to_file(file_path, some_string):
    """
    Filepath relative to project root
    """
    file = open(get_root_path() + os.sep + file_path, "w", encoding="utf8")
    file.write(some_string)
    file.close()


def append_to_file(file_path, some_string):
    """
    Filepath relative to project root
    """
    file = open(get_root_path() + os.sep + file_path, "a", encoding="utf8")
    file.write(some_string)