from cluster import clustering
from cluster.clusterSettings import ClusterSettings
from corpora.corpus import Corpus
from geneticalgorithm.chromosome import Chromosome
from inputOutput.filehandling import write_to_file, append_to_file

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

    chromosome = Chromosome((2, 0.48, 0.72), 1100, 7, 0.6, 2, 7, 0, 1,
                            {"FrontPageHeading": 1,
                             "FrontPageIntroduction": 1,
                             "ArticleHeading": 1,
                             "ArticleByline": 1,
                             "ArticleIntroduction": 1,
                             "ArticleText": 1}, 0.2, {"similarity_method": 1,
                             "params": (0.5, 0, 0)})

    clusterer = clustering.CompactTrieClusterer(corpus, cluster_settings)
    results = clusterer.cluster(chromosome)
    write_to_file("otherParams.txt", results.results_string)
    detailed_results = "\n__________________________________________________________".join(results.clusters_result_strings)
    append_to_file("otherParams.txt", detailed_results)

if __name__ == '__main__':
    main()