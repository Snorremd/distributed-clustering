from easylogging.configLogger import getLoggerForStdOut
from text.xmlsnippets import get_snippet_collection, make_tag_index, make_ground_truth_clusters

__author__ = 'snorre'

## Tree types
SUFFIX_TREE = 0
MID_SLICE = 1
RANGE_SLICE = 2
N_SLICE = 3

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
