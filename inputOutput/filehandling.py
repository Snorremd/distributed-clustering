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


def write_to_file(filepath, some_string):
    """
    Filepath relative to project root
    """
    file = open(filepath, "w", encoding="utf8")
    file.write(some_string)


def append_to_file(filepath, some_string):
    """
    Filepath relative to project root
    """
    file = open(filepath, "a", encoding="utf8")
    file.write(some_string)