"""The corpusprocessor module implements a console based dialog to create
snippet xml files based on corpus files. It uses the corpora.xml file to list
available corpora and to determine which CorpusProcessor class to use for
the corpus processing task. CorpusProcessor-classes need to be implemented
on a corpus basis."""

from importlib import import_module
from inputOutput.filehandling import get_root_path
from inputOutput.output import show_info_dialog, show_option_dialog, \
    show_confirmation_dialog
import xml.etree.ElementTree as ET
import os
import sys

__author__ = 'snorre'

if __name__ == "__main__":
    show_info_dialog(
        "This module takes corpus files and generated snippet files compatible "
        "with the compact trie clustering algorithm.\n It uses a corpus "
        "processor implemented specifically for the corpus in question.")

    ## Find available corpora in corpora.xml
    corpusTree = ET.parse(get_root_path() + os.sep + "corpora.xml")
    options = []
    for corpus in corpusTree.getroot().findall("corpus"):
        options.append(corpus.get('name'))

    choice = show_option_dialog(
        "Please choose one of the corpora listed below by typing their name. "
        "If you do not see your preferred corpus among the available options "
        "please add the corpus to the corpora.xml file.",
        options)

    ## Get path of corpus and snippet files from corpora.xml
    corpusSettings = corpusTree.getroot().findall(
        ".corpus[@name='{0}']".format(choice))[0]

    corpusPath = get_root_path() + os.sep + "corpusfiles" + os.sep
    corpusPath += corpusSettings.findall(".directory")[0].text
    corpusFile = corpusSettings.findall(".corpusfile")[0].text
    corpusFilePath = corpusPath + os.sep + corpusFile
    snippetFile = corpusSettings.findall(".snippetfile")[0].text
    snippetFilePath = corpusPath + os.sep + snippetFile

    if not os.path.isfile(corpusFilePath):
        show_info_dialog("Could not find corpus file. Please make sure there "
                         "is a corpus file with name {0} in directory {1} and"
                         " restart script.".format(corpusPath, corpusFile))
        sys.exit()  # Exit script if no corpus file exist

    if os.path.isfile(snippetFilePath):
        choice = show_confirmation_dialog("A snippet file with name {0} "
                                          "already exists. Do you want to "
                                          "overwrite it?".format(snippetFile))
        if not choice:
            sys.exit()  # If user declines overwrite, exit script

    ## Get name of CorpusProcessor class, import corpus module
    processorName = corpusSettings.findall(".processorname")[0].text
    corpusModule = import_module("corpora.corpus")
    try:
        processorClass = getattr(corpusModule, processorName)
    except AttributeError:
        show_info_dialog("Could not find any corpus processor with name {0} "
                         "in python module corpus. Please specify an existing"
                         " and compatible processor in corpora.xml or "
                         "implement the specified processor in {0}."
                         .format(processorName))
        sys.exit()  # Could not find a corpus processor exit script
    else:
        ## Corpus processor exist, create instance and process corpus file
        processor = processorClass(corpusFilePath, snippetFilePath)
        processor.process_file()
        processor.write_snippet_file()

        show_info_dialog("Completed processing of {0} and wrote {1} to {2}."
        .format(corpusFile, snippetFile, snippetFilePath))