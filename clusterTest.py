import gc
import pdb
from time import sleep
from cluster.clusterSettings import ClusterSettings
import cluster.clustering as clustering
from corpora.corpus import Corpus
from easylogging.configLogger import get_logger_for_stdout
from geneticalgorithm.chromosome import createRandomChromosome

__author__ = 'snorre'

logger = get_logger_for_stdout("clusterTestModule")

def cluster(chromosome, corpus, clusterSettings):
    clusterer = clustering.CompactTrieClusterer(corpus, clusterSettings)
    value = clusterer.cluster(chromosome)
    return value


def main():
    corpus = Corpus("klimauken",
                    "./corpusfiles/klimauken/klimaukenSnippetsNew3.xml",
                    "klimaukenSnippetsNew3.xml",
                    "./corpusfiles/klimauken/klimaukenOBTSnippets.xml",
                    "klimaukenOBTSnippets.xml",
                    "KlimaukenCorpusProcessor",
                    False)

    clusterSettings = ClusterSettings(True, .5)
    chromosome = createRandomChromosome()
    result = cluster(chromosome, corpus, clusterSettings)
    result = None
    logger.info("Sleep to let memory clear")
    sleep(1)
    gc.collect()


if __name__ == '__main__':
    sleep(1)
    while True:
        main()