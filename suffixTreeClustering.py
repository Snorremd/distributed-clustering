from cluster import clustering
from cluster.clusterSettings import ClusterSettings
from corpora.corpus import Corpus
from geneticalgorithm.chromosome import Chromosome

__author__ = 'snorre'

def main():
    corpus = Corpus("klimauken",
                    "./corpusfiles/klimauken/klimaukenSnippetsNew3.xml",
                    "klimaukenSnippetsNew4.xml",
                    "./corpusfiles/klimauken/klimaukenOBTSnippets.xml",
                    "klimaukenOBTSnippets.xml",
                    "KlimaukenCorpusProcessor",
                    False)

    cluster_settings = ClusterSettings(True, .5)

    chromosome = Chromosome((0,0,0), 3000, 3, 0.7, 1, 7, 1, 1,
                            {"FrontPageHeading": 1,
                             "FrontPageIntroduction": 1,
                             "ArticleHeading": 1,
                             "ArticleByline": 1,
                             "ArticleIntroduction": 1,
                             "ArticleText": 1}, 1, {"similarity_method": 0,
                             "params": (0.5, 0, 0)})

    clusterer = clustering.CompactTrieClusterer(corpus, cluster_settings)
    results = clusterer.cluster(chromosome)
    print(results.results_string)

if __name__ == '__main__':
    main()