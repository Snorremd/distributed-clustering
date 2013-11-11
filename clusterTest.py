import gc
import pdb
from time import sleep
from cluster.clusterSettings import ClusterSettings
import cluster.clustering as clustering
from corpora.corpus import Corpus
from easylogging.configLogger import get_logger_for_stdout
from geneticalgorithm.chromosome import create_random_chromosome, Chromosome

__author__ = 'snorre'

logger = get_logger_for_stdout("clusterTestModule")


def cluster(chromosome, corpus, clusterSettings):
    clusterer = clustering.CompactTrieClusterer(corpus, clusterSettings)
    value = clusterer.cluster(chromosome)
    return value


def main():
    corpus = Corpus("klimauken",
                    "./corpusfiles/klimauken/klimaukenSnippetsNew3.xml",
                    "klimaukenSnippetsNew4.xml",
                    "./corpusfiles/klimauken/klimaukenOBTSnippets.xml",
                    "klimaukenOBTSnippets.xml",
                    "KlimaukenCorpusProcessor",
                    False)

    clusterSettings = ClusterSettings(True, .5)
    chromosome = Chromosome((0,0,0), 500, 5, 0.7, 1, 7, 1, 1,
                            {"FrontPageHeading": 1,
                             "FrontPageIntroduction": 1,
                             "ArticleHeading": 1,
                             "ArticleByline": 1,
                             "ArticleIntroduction": 1,
                             "ArticleText": 1})
    result = cluster(chromosome, corpus, clusterSettings)
    logger.info("Sleep to let memory clear")


if __name__ == '__main__':
    main()