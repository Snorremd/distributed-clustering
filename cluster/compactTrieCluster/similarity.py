__author__ = 'snorre'


class SimilarityMeasurer(object):

    def __init__(self, similarity_type, parameters):

        self.similarity_type = similarity_type
        self.parameters = parameters
        self.functions = {
            0: self.jaccard_similarity
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
        return self.functions[0](base_cluster_1, base_cluster_2)

    def jaccard_similarity(self, base_cluster_1, base_cluster_2):
        """
        Calculate the jaccard coefficient between the two base clusters based on
        their common sources.
        :type base_cluster_1: BaseCluster
        :param base_cluster_1: first base clusters
        :type base_cluster_2: BaseCluster
        :param base_cluster_2: second base cluster
        :return: similarity given by boolean value
        """
        threshold = self.parameters["threshold"]
        common = []
        for source in base_cluster_1.sources:
            if source in base_cluster_2.sources:
                common.append(source)
        size_overlap = float(len(common))  # Make sure result is not rounded
        jaccard1 = size_overlap/base_cluster_1.size
        jaccard2 = size_overlap/base_cluster_2.size

        return jaccard1 > threshold and jaccard2 > threshold
