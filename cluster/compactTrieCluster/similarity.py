from math import log, sqrt
from easylogging.configLogger import get_logger_for_stdout

__author__ = 'snorre'


class SimilarityMeasurer(object):
    def __init__(self, parameters, corpus_size, corpus_frequencies, raw_frequencies, document_frequencies):

        self.logger = get_logger_for_stdout("SimilarityMeasurer")
        self.corpus_size = corpus_size
        self.corpus_frequencies = corpus_frequencies
        self.document_frequencies = document_frequencies
        self.raw_frequencies = raw_frequencies
        self.similarity_type = parameters["similarity_method"]
        self.params = parameters["params"]
        self.similarity_methods = {
            0: self.jaccard_similarity,
            1: self.cosine_similarity,
            2: self.amendment_1c
        }

    def similar(self, base_cluster_1, base_cluster_2):
        """
        Calculate the boolean similarity between two base clusters with one
         of the similarity methods defined below.

        :type base_cluster_1: BaseCluster
        :param base_cluster_1: first base clusters
        :type base_cluster_2: BaseCluster
        :param base_cluster_2: second base cluster
        :return: similarity given by boolean value
        """
        return self.similarity_methods[self.similarity_type](base_cluster_1, base_cluster_2)

    def jaccard_similarity(self, base_cluster_1, base_cluster_2):
        """
        Calculate the jaccard coefficient between the two base clusters based on
         their common sources. The Jaccard coefficient is defined as
         |a intersect b| / |a| and |a intersect b| / |b|. If both are greater than 0.5
         the two base clusters are "jaccard similar".

        :type base_cluster_1: BaseCluster
        :param base_cluster_1: first base clusters
        :type base_cluster_2: BaseCluster
        :param base_cluster_2: second base cluster

        :rtype: bool
        :return: similarity given by boolean value
        """
        threshold = self.params[0]
        common = []
        for source in base_cluster_1.sources:
            if source in base_cluster_2.sources:
                common.append(source)
        size_overlap = float(len(common))  # Make sure result is not rounded
        jaccard1 = size_overlap / base_cluster_1.size
        jaccard2 = size_overlap / base_cluster_2.size

        return jaccard1 > threshold and jaccard2 > threshold

    def cosine_similarity(self, base_cluster_1, base_cluster_2):
        """
        Calculate the cosine similarity between two base clusters.

        :type base_cluster_1: BaseCluster
        :param base_cluster_1: first base clusters
        :type base_cluster_2: BaseCluster
        :param base_cluster_2: second base cluster

        :rtype: bool
        :return: similarity given by boolean value
        """
        jaccard_similar = self.jaccard_similarity(base_cluster_1, base_cluster_2)

        if jaccard_similar:
            threshold = self.params[0]
            label_vector_1 = self.label_vector(base_cluster_1)
            label_vector_2 = self.label_vector(base_cluster_2)
            cosine_sim = scalar_product(label_vector_1, label_vector_2) / \
                (magnitude(label_vector_1) * magnitude(label_vector_2))

            return cosine_sim > threshold

        else:
            return False

    def label_vector(self, base_cluster):
        """
        Original author: Richard Elling Moe
        Calculates the label vector of a base cluster, i.e. the tf-idf
         values of each word in the base cluster.

        :type base_cluster: BaseCluster
        :param base_cluster: Base cluster

        :rtype: dict
        :return: label vector for base cluster
        """
        label_vector = {}
        for word in base_cluster.label:
            label_vector[word] = self.tfidf(word, base_cluster.sources)
        return label_vector

    def term_frequency(self, word, sources):
        """
        Get the term frequency of a single word

        :type word: str
        :param word: word to calculate term frequency of
        :type sources: list
        :param sources: a list of sources in which to count word

        :rtype: int
        :return: sum of frequency for word
        """
        sum_of_frequencies = 0
        for source in sources:
            sum_of_frequencies += self.raw_frequencies[word][source]
        return sum_of_frequencies

    def inverse_document_frequency(self, word):
        """
        Get inverse document frequency given a word, a corpus size and document frequencies

        :type word: str
        :param word: word to calculate inverse document frequency for

        :rtype: float
        :return: inverse document frequency of word
        """
        return log(self.corpus_size / (1 + len(self.document_frequencies[word])))

    def tfidf(self, word, sources):
        """
        Get the tf-idf value of a word given sources

        :type word: str
        :param word: a word from a label to calculate tf-idf value for
        :type sources: list
        :param sources: sources from a base cluster

        :rtype: float
        :return: tf-idf value of word given sources
        """
        return self.term_frequency(word, sources) * self.inverse_document_frequency(word)

    def amendment_1c(self, base_cluster_1, base_cluster_2):
        """
        Original author: Richard Elling Moe

        Calculate the similarity between two base clusters given
        their jaccard similarity in addition to two additional metrics.

        The first is the average corpus frequency for the labels in the union
        of labels in base cluster 1 and base cluster 2. The average frequency
        should be less than some predefined average (for example 5).

        The second metric is the number of common labels in base cluster 1 and
        base cluster 2. This number should be greater than a predefined value
        (for example 1).

        :type base_cluster_1: BaseCluster
        :param base_cluster_1: first base clusters
        :type base_cluster_2: BaseCluster
        :param base_cluster_2: second base cluster

        :rtype: bool
        :return: similarity given by boolean value
        """
        jaccard_similar = self.jaccard_similarity(base_cluster_1, base_cluster_2)

        if jaccard_similar:
            label_intersection = []
            label_union = base_cluster_1.label
            for word in base_cluster_2.label:
                if word not in base_cluster_1.label:
                    label_union.append(word)
                else:
                    label_intersection.append(word)

            label_union_frequencies = []
            for word in label_union:
                label_union_frequencies.append(self.corpus_frequencies[word])

            average_frequency = guarded_average(label_union_frequencies)
            label_intersection_len = len(label_intersection)
            amendment1c_similar = average_frequency < self.params[1] and \
                label_intersection_len > self.params[2]
            return amendment1c_similar
        else:
            return False

def guarded_average(numbers):
    """
    Calculate the average of numbers. If list is empty, return 0.

    :type numbers: list
    :param numbers: bunch of numbers

    :rtype: float
    :return: the average value of the numbers
    """
    if not numbers:
        return 0
    else:
        length = len(numbers)
        avg = float(sum(numbers)) / length
        return avg

def scalar_product(vector1, vector2):
    """
    Original author: Richard Elling Moe
    Find the scalar product of two vectors.

    :type vector1: dict
    :param vector1: first label vector
    :type vector2: dict
    :param vector2: second label vector

    :rtype: float
    :return: scalar product of vector1 and vector2
    """
    sum_indices = 0
    indices = set().union(vector1.keys(), vector2.keys())
    for i in indices:
        if i in vector1 and i in vector2:
            sum_indices += (vector1[i] * vector2[i])
    return sum_indices


def magnitude(vector):
    """
    Original author: Richard Elling Moe
    Find the magnitude of a label vector

    :type vector: dict
    :param vector: a label vector

    :rtype: float
    :return: magnitude of vector
    """
    sum_vectors = 0
    for i in vector.keys():
        sum_vectors += vector[i] ** 2
    return sqrt(sum_vectors)