from easylogging.configLogger import get_logger_for_stdout
from text.wordOccurrence import count_sources, get_word_sources

__author__ = 'snorre'


logger = get_logger_for_stdout("baseClusterModule")


class BaseCluster(object):
    """
    The BaseCluster class models a base cluster.
    """

    ## Id counter
    id = 0

    def __init__(self):
        self.id = BaseCluster.id
        BaseCluster.id += 1
        self.label = []
        self.sources = set()
        self.size = 0.0
        self.score = 0.0

    def add_sources(self, sources):
        """
        Add sources to base clusters

        :type sources: list
        :param sources: sources to add
        """
        for source in sources:
            if not source in self.sources:
                self.sources.add(source)
                self.size += 1.0

    def __str__(self):
        ## Override str function
        label = " ".join(self.label)
        return "Label: " + label + "\nScore: " + str(self.score) + "\n\n"


def sort_base_clusters(base_clusters, no_of_sources, word_sources, min_no_in_collection,
                       max_ratio_in_collection, min_limit_for_base_cluster_score,
                       max_limit_for_base_cluster_score, sort_descending):
    """
    Sort a list of base clusters given the parameters used to calculate the base cluster score.

    :type base_clusters: list
    :param base_clusters: list base clusters to sort
    :type no_of_sources: int
    :param no_of_sources: Number of documents in corpus
    :type word_sources: dict
    :param word_sources: an index of words mapping to sources the words appear in
    :type min_no_in_collection: int
    :param min_no_in_collection: the minimum number of occurrences for a word to be counted
    :type max_ratio_in_collection: float
    :param max_ratio_in_collection: maximum word frequency ratio in order to be counted
    :param min_limit_for_base_cluster_score: Min limit for score calculation
    :type max_limit_for_base_cluster_score: int
    :param max_limit_for_base_cluster_score: Max limit for score calculation
    :type sort_descending: int
    :param sort_descending: (bool) sort best base clusters first
    """

    def compute_score(base_cluster):
        """
        Compute score for a base cluster

        :type base_cluster: BaseCluster
        :param base_cluster:

        :rtype: float
        :return: base cluster score
        """

        def f(n):
            """
            The implementation of the base cluster score function, f.

            :type n: int
            :param n: length of base cluster phrase

            :rtype: int
            :return: the score of the base cluster
            """
            if n <= min_limit_for_base_cluster_score:
                return 0
            elif n > max_limit_for_base_cluster_score:
                return 7
            else:
                return n

        def effective_words(label):
            """
            Finds the effective length of a base cluster label.

            :type label: list
            :param label: a base cluster label

            :rtype: int
            :return: the effective length of the base cluster label
            """
            n = 0
            for word in label:
                word_sources_length = len(word_sources[word])
                ratio_in_collection = float(word_sources_length) / float(no_of_sources)

                if word_sources_length > min_no_in_collection and \
                        ratio_in_collection <= max_ratio_in_collection:
                    ## If word contributes to phrase length
                    n += 1
            return n

        base_cluster_score = base_cluster.size * f(effective_words(base_cluster.label))
        base_cluster.score = base_cluster_score
        return base_cluster_score

    reverse_sort = True if sort_descending else False  # Ternary pattern
    base_clusters.sort(key=compute_score, reverse=reverse_sort)


def top_base_clusters(compact_trie,
                      top_base_clusters_amount=500,
                      min_no_in_collection=3,
                      max_ratio_in_collection=0.4,
                      min_limit_for_base_cluster_score=1,
                      max_limit_for_base_cluster_score=6,
                      sort_descending=1
                      ):
    """
    Find the top or bottom x base clusters based on a compact trie.

    :type compact_trie: cluster.compactTrieCluster.compactTrie.CompactTrie
    :param compact_trie: The compact trie object containing all compact trie nodes
    :type top_base_clusters_amount: int
    :param top_base_clusters_amount: number of base clusters to return
    :type min_no_in_collection: int
    :param min_no_in_collection: minimum word frequency in order to be counted
    :type max_ratio_in_collection: float
    :param max_ratio_in_collection: maximum word frequency ratio in order to be counted
    :type min_limit_for_base_cluster_score: int
    :param min_limit_for_base_cluster_score: Min limit for score calculation
    :type max_limit_for_base_cluster_score: int
    :param max_limit_for_base_cluster_score: Max limit for score calculation
    :type sort_descending: int
    :param sort_descending: (bool) sort best base clusters first

    :rtype: list
    :return: top/bottom x base clusters
    """
    base_clusters = generate_base_cluster(compact_trie.root)
    no_of_sources = count_sources(compact_trie.root)
    word_sources = get_word_sources(compact_trie.root)

    sort_base_clusters(base_clusters, no_of_sources, word_sources, min_no_in_collection,
                       max_ratio_in_collection, min_limit_for_base_cluster_score,
                       max_limit_for_base_cluster_score, sort_descending)

    if top_base_clusters_amount > len(base_clusters):
        return base_clusters
    else:
        return base_clusters[:top_base_clusters_amount]


def generate_base_cluster(compact_trie_node):
    """
    Recursively generate base clusters from a compact trie node. The start of the recursion
    should be called on the root node of the compact trie.

    :type compact_trie_node: cluster.compactTrieCluster.compactTrie.CompactTrieNode
    :param compact_trie_node: A compact trie node to generate base clusters from

    :rtype: list
    :return: a list of base clusters
    """
    base_clusters = []

    for subtree in compact_trie_node.subtrees.values():
        new_base_cluster = BaseCluster()
        new_base_cluster.label = subtree.generate_node_label()
        new_base_cluster.add_sources(subtree.sources)
        new_base_cluster.size = float(len(new_base_cluster.sources))
        subtree_base_clusters = generate_base_cluster(subtree)
        for base_cluster in subtree_base_clusters:
            new_base_cluster.add_sources(base_cluster.sources)
            base_clusters.append(base_cluster)
        base_clusters.append(new_base_cluster)
    return base_clusters


def drop_singleton_base_clusters(base_clusters):
    """
    Deletes singleton base clusters, i.e. base clusters with a single source.

    :type base_clusters: list
    :param base_clusters: a list of base clusters

    :rtype list:
    :return: filtered base clusters list
    """
    base_clusters = [bc for bc in base_clusters if len(bc.sources) != 1]
    return base_clusters