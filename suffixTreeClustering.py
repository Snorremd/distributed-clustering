from cluster import clustering
from cluster.clusterSettings import ClusterSettings
from corpora.corpus import Corpus
from geneticalgorithm.chromosome import Chromosome

__author__ = 'snorre'

def main():
    corpus = Corpus("klimauken",
                    "./corpusfiles/klimauken/klimaukenSnippetsNew4.xml",
                    "klimaukenSnippetsNew4.xml",
                    "./corpusfiles/klimauken/klimaukenOBTSnippets.xml",
                    "klimaukenOBTSnippets.xml",
                    "KlimaukenCorpusProcessor",
                    False)

    cluster_settings = ClusterSettings(True, .5)

    chromosome = Chromosome((0, 0.48, 0.72), 1000, 3, 0.4, 2, 7, 1, 1,
                            {"FrontPageHeading": 1,
                             "FrontPageIntroduction": 1,
                             "ArticleHeading": 1,
                             "ArticleByline": 1,
                             "ArticleIntroduction": 1,
                             "ArticleText": 1}, 0.25, {"similarity_method": 0,
                             "params": (0.5, 73, 1)})

    clusterer = clustering.CompactTrieClusterer(corpus, cluster_settings)
    results = clusterer.cluster(chromosome)
    print(results.results_string)
    detailed_results = "\n__________________________________________________________".join(results.clusters_result_strings[:400])
    print(detailed_results)

if __name__ == '__main__':
    main()