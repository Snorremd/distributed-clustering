from copy import deepcopy
import gc
from cluster.compactTrie.compactTrie import generate_compact_trie
from easylogging.configLogger import getLoggerForStdOut
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
        self.logger = getLoggerForStdOut("CompactTrieClusterer")
        self.corpus = corpus
        self.clusterSettings = clusterSettings
        self.logger.debug("Make indexes and snippet collection")
        self.tagIndex = make_tag_index(corpus.snippetFilePath)
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

        ## Build the compact trie structure
        compactTrie = generate_compact_trie(snippetCollection,
                                         chromosome.treeType)

        return compactTrie


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
    return (
        (0, 0, 0),
        (.0, .0, .0),
        (.0, .0, .0, .0, .0, .0),
        (.0, .0, .0, .0, .0, .0),
        (.0, .0, .0, .0, .0, .0)
    )


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