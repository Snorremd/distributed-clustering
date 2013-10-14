from time import sleep
from guppy import hpy

from cluster.clusterSettings import ClusterSettings
from cluster.clustering import CompactTrieClusterer
from geneticalgorithm.chromosome import create_random_chromosome
from corpora.corpus import Corpus

memheap = hpy()

__author__ = 'snorre'

if __name__ == "__main__":
    settings = ClusterSettings(False, 0.5)
    corpus = Corpus("klimauken",
                    "klimaukenSnippetsNew3.xml",
                    "/home/snorre/workspaces/masterthesis/distributed"
                    "-clustering/corpusfiles/klimauken/klimaukenSnippetsNew3"
                    ".xml",
                    "klimaukenOBT.xml",
                    "/home/snorre/workspaces/masterthesis/distributed"
                    "-clustering/corpusfiles/klimauken/klimaukenOBT.xml",
                    "KlimaUkenProcessor",
                    False)
    clusterer = CompactTrieClusterer(corpus, settings)
    for _ in range(100):
        chromosome = create_random_chromosome()
        chromosome.calc_fitness_score(clusterer)
        sleep(5)

