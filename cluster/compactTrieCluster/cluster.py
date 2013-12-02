from text.phrases import phrase_to_string


class Cluster(object):
    """
    The Cluster class models a final cluster in the Compact Trie Clustering algorithm
    """

    def __init__(self):
        self.label = []  # label for the cluster as a whole ?
        self.labels = []
        self.sources = []
        self.number_of_sources = 0  # increment rather than post-merge-count
        self.word_frequency = {}  # word frequency in the cluster
        self.number_of_words = 0  # increment rather than post-merge-count?
        self.source_overlap = []  # shared-by-all sources
        self.label_overlap = []  # shared-by-all words

    def add_sources(self, sources):
        """
        Add a list of sources to the cluster

        :type sources: list
        :param sources: sources (documents) from corpus
        """
        for source in sources:
            if not source in self.sources:
                self.sources.append(source)
                self.number_of_sources += 1

    def collect_words(self, label_list):
        """
        Collects words from a label list counting frequency of each word

        :type label_list: list
        :param label_list: labels from merged component
        """
        for label in label_list:
            if label in self.word_frequency:
                self.word_frequency[label] += 1
            else:
                self.word_frequency[label] = 1
                self.number_of_words += 1

    def make_label(self):
        """
        Constructs a label for the whole component based on the
        list of words occurring in labels sorted by frequency.
        """
        label_list = []
        for (x, y) in self.word_frequency.items():
            label_list.append((y, x))
        label_list.sort(reverse=True)
        for (x, y) in label_list:
            self.label.append(y)

    def __str__(self):
        ## Override __str__ method of object class
        sources = []
        labels = []
        for label in self.labels:
            labels.append(phrase_to_string(label))
        for source in self.sources:
            sources.append(source[7:])
        string_rep = "<{0}>\n" \
                     "Labels: {1}\n" \
                     "Label overlap: {2}\n" \
                     "Num of sources: {3}\n" \
                     "Source overlap: {4}\n" \
                     "Sources:\n{5}"\
            .format(phrase_to_string(self.label),
                    "|".join(labels),
                    ", ".join(self.label_overlap),
                    self.number_of_sources,
                    self.source_overlap,
                    "\n".join(sources)
                    )

        return string_rep


def generate_clusters(component_list):
    """
    Make clusters for each merged component in the component list

    :type component_list: list
    :param component_list: a list of components (base cluster lists)
    :return:
    """
    clusters = []

    for component in component_list:
        new_cluster = Cluster()
        for base_cluster in component:
            new_cluster.add_sources(base_cluster.sources)
            new_cluster.labels.append(base_cluster.label)
            new_cluster.collect_words(base_cluster.label)
        new_cluster.source_overlap = common(map(lambda x: x.sources,
                                                component))
        new_cluster.label_overlap = common(map(lambda x: x.label, component))
        new_cluster.make_label()

        clusters.append(new_cluster)

    return clusters


def drop_one_word_clusters(clusters):
    """
    Drop all clusters with labels shorter than two terms/words

    :type clusters: list
    :param clusters: cluster list to filter

    :rtype: list
    :return: a filtered list of clusters
    """

    def singleton_cluster(cluster):
        if len(cluster.labels) > 1 or len(cluster.labels[0]) > 1:
            return False
        else:
            return True

    return [cluster for cluster in clusters if not singleton_cluster(cluster)]


def flatten(lists):
    """
    Return a flat list of all elements contained within a list of lists

    :type lists: list
    :param lists: list of lists
    :return: a flattened list of all elements contained within the lists
    """
    flat_list = []
    for a_list in lists:
        for element in a_list:
            flat_list.append(element)
    return flat_list


def common(lists):
    """
    Returns a list of all the elements common in lists

    :type lists: list, map
    :param lists: a list of lists of elements
    :rtype: list
    :return: all common elements of lists
    """
    lists = list(lists)
    all_elements = flatten(lists)
    common_elements = []
    for element in all_elements:
        if not element in common_elements:
            common_elements.append(element)

    for element in common_elements[:]:
        for a_list in lists:
            if not element in a_list:
                del common_elements[common_elements.index(element)]
                break

    return common_elements