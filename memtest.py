from cluster.clusterSettings import ClusterSettings
from cluster.clustering import CompactTrieClusterer
from geneticalgorithm.chromosome import createRandomChromosome
from text.corpora import Corpus
from guppy import hpy
import gc
memheap = hpy()

__author__ = 'snorre'

if __name__ == "__main__":
    settings = ClusterSettings(False, 0.5, "klimauken")
    corpus = Corpus("klimauken", "klimaukenSnippetsNew.json", "klimauken",
                    False)
    clusterer = CompactTrieClusterer(corpus, settings)
    for _ in xrange(100):
        print memheap.heap()
        chromosome = createRandomChromosome()
        chromosome.calc_fitness_score(clusterer)

