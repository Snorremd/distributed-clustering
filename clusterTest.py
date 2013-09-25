from time import sleep
from guppy import hpy
from cluster.clusterSettings import ClusterSettings
from cluster.clustering import CompactTrieClusterer
from corpora.corpus import Corpus
from geneticalgorithm.chromosome import createRandomChromosome

__author__ = 'snorre'


def cluster(chromosome, corpus, clusterSettings):
    clusterer = CompactTrieClusterer(corpus, clusterSettings)


def main():
    corpus = Corpus("klimauken",
                    "./corpusfiles/klimauken/klimaukenSnippetsNew3.xml",
                    "klimaukenSnippetsNew3.xml",
                    "./corpusfiles/klimauken/klimaukenOBTSnippets.xml",
                    "klimaukenOBTSnippets.xml",
                    "KlimaukenCorpusProcessor",
                    False)

    clusterSettings = ClusterSettings(True, .5)
    while True:
        chromosome = createRandomChromosome()
        cluster(chromosome, corpus, clusterSettings)
        hippie = hpy()
        print hippie.heap()
        sleep(1)


if __name__ == '__main__':
    main()