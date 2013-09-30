import gc
import pdb
from time import sleep
from cluster.clusterSettings import ClusterSettings
import cluster.clustering as clustering
from corpora.corpus import Corpus
from geneticalgorithm.chromosome import createRandomChromosome

__author__ = 'snorre'


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
    gc.collect()


if __name__ == '__main__':
    sleep(1)
    while True:
        main()