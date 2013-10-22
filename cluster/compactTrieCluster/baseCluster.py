from easylogging.configLogger import get_logger_for_stdout
from text.wordOccurrence import count_sources, get_word_sources

__author__ = 'snorre'


logger = get_logger_for_stdout("baseClusterModule")


class BaseCluster(object):
    def __init__(self):
        self.label = ""
        self.sources = []
        self.size = 0.0

    def add_sources(self, sources):
        """
        Add sources to base clusters
        :type sources: list
        :param sources: sources to add
        """
        for source in sources:
            if not source in self.sources:
                self.sources.append(source)
                self.size += 1.0

    def __str__(self):
        """
        Used when print-method is called on self
        """
        print(self.label + ":"),
        print(self.sources)


def sort_base_clusters(baseClusters, noOfSources, wordSources, minNoInCollection,
                       maxRatioInCollection, minLimitForBaseClusterScore,
                       maxLimitForBaseClusterScore):

    def compute_score(baseCluster):
        """
        Compute score for base cluster
        :type baseCluster: BaseCluster
        :param baseCluster:
        :rtype: float
        :return: base cluster score
        """

        def f(n):
            """
            Define
            :type n: int
            :param n: length of base cluster phrase
            :rtype: int
            :return:
            """
            if n <= minLimitForBaseClusterScore:
                return 0
            elif n > maxLimitForBaseClusterScore:
                return 7
            else:
                return n

        def effective_words(label):
            """
            """
            n = 0
            for word in label:
                wordSourcesLength = len(wordSources[word])
                ratioInCollection = float(wordSourcesLength) / \
                                    float(noOfSources)
                if wordSourcesLength > minNoInCollection and \
                                ratioInCollection <= maxRatioInCollection:
                    ## If word contributes to phrase length
                    n += 1
            return n

        base_cluster_score = baseCluster.size * f(effective_words(baseCluster.label))
        return base_cluster_score

    baseClusters.sort(key=compute_score, reverse=True)


def top_base_clusters(compactTrie,
                      topBaseClustersAmount=500,
                      minNoInCollection=3,
                      maxRatioInCollection=0.4,
                      minLimitForBaseClusterScore=1,
                      maxLimitForBaseClusterScore=6
                      ):
    """

    :param compactTrie:
    :param topBaseClustersAmount:
    :param minNoInCollection:
    :param maxRatioInCollection:
    :param minLimitForBaseClusterScore:
    :param maxLimitForBaseClusterScore:
    :return:
    """

    baseClusters = generate_base_cluster(compactTrie.root)
    noOfSources = count_sources(compactTrie.root)
    wordSources = get_word_sources(compactTrie.root)

    sort_base_clusters(baseClusters, noOfSources, wordSources, minNoInCollection,
                       maxRatioInCollection, minLimitForBaseClusterScore,
                       maxLimitForBaseClusterScore)

    if topBaseClustersAmount > len(baseClusters):
        return baseClusters
    else:
        return baseClusters[:topBaseClustersAmount]

def generate_base_cluster(compactTrieNode):
    """

    :type compactTrieNode: CompactTrieNode
    :param compactTrieNode:
    :return:
    """
    base_clusters = []

    for subtree in compactTrieNode.subtrees.values():
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
    for base_cluster in base_clusters:
        if len(base_cluster.sources) == 1:
            del base_cluster