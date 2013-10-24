from lib2to3.patcomp import _type_of_literal
import math
from cluster.compactTrieCluster.cluster import common
from text.phrases import string_to_phrase

__author__ = 'snorre'


class ClusterResult(object):
    """
    A container class for clustering results
    """

    def __init__(self, time, no_of_base_clusters, no_of_clusters, no_of_gt_clusters,
                 precision, recall, f_measure, tag_accuracies, precisions,
                 recalls, f_measures, results_string):
        self.time = time
        self.no_of_base_clusters = no_of_base_clusters
        self.no_of_clusters = no_of_clusters
        self.no_of_gt_clusters = no_of_gt_clusters
        self.precision = precision
        self.recall = recall
        self.f_measure = f_measure
        self.tag_accuracies = tag_accuracies
        self.precisions = precisions
        self.recalls = recalls
        self.f_measures = f_measures
        self.results_string = results_string

    def __str__(self):
        stringRep = ""

        for property, value in vars(self).items():
            stringRep += str(property) + ": " + str(value) + "\n"
        return stringRep


def calc_tag_accuracy(clusters,
                      no_of_clusters,
                      tag_index):
    """
    Calculate the tag accuracy of the results
    :param clusters:
    :param no_of_clusters:
    :param tag_index:
    :return:
    """
    def count_matches(discrepancy):
        count = 0
        for cluster in clusters:
            tag_list = []
            for source in cluster.sources:
                string = tag_index[source].replace('-', ' ')
                tag_list.append(string_to_phrase(string))
            if len(common(map(lambda cluster:
                              cluster, tag_list))) == 5 - discrepancy:
                count += 1
        return count

    ## Make a list of tuples containing count match results
    match_result = []
    for i in range(6):
        count_match = count_matches(i)
        p = 0
        for k in range(i):
            p += count_matches(k)
            ## Tuple (index, countMatch, ratio, accumulated)
        match_result.append((i,
                            count_match,
                            count_match / float(no_of_clusters),
                            (p + count_match) / float(no_of_clusters)))
    return match_result


def calc_ground_truth(clusters,
                      no_of_clusters,
                      ground_truth_clusters,
                      tag_index):
    """
    Calculate ground truth (precision) for clusters
    :param clusters:
    :param no_of_clusters:
    :param ground_truth_clusters:
    :param tag_index:
    :return:
    """
    count = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    for cluster in clusters:
        best_match = 0
        for gtc_key in ground_truth_clusters.keys():
            if list_contains_list(cluster.sources,
                                  ground_truth_clusters[gtc_key]):
                ## Make a list of tags occurring in the cluster's sources
                tag_list = []
                for source in cluster.sources:
                    string = tag_index[source].replace('-', ' ')
                    tag_list.append(string_to_phrase(string))
                gtc_key_string = gtc_key.replace('-', ' ')
                tag_list.append(string_to_phrase(gtc_key_string))
                common_elements = common(map(lambda cluster: cluster,
                                             tag_list))
                d = len(common_elements)
                if d > best_match:
                    best_match = d
        count[best_match] += 1

    ground_truth_results = []
    for i in (5, 4, 3, 2, 1, 0):
        p = 0
        for k in range(i, 6):
            p += count[k]
        ground_truth_results.append((5 - i,
                                    count[i],
                                    count[i] / float(no_of_clusters),
                                    p / float(no_of_clusters)))
    return ground_truth_results


def calc_gt_represented(clusters,
                        ground_truth_clusters,
                        tag_index):
    count = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    for gtc_key in ground_truth_clusters.keys():
        best_match = 0
        for cluster in clusters:
            if list_contains_list(cluster.sources, ground_truth_clusters[
                gtc_key]):
                tag_list = []
                for source in cluster.sources:
                    string = tag_index[source].replace('-', ' ')
                    tag_list.append(string_to_phrase(string))
                gtc_key_string = gtc_key.replace('-', ' ')
                tag_list.append(string_to_phrase(gtc_key_string))
                d = len(common(map(lambda cluster:
                                   cluster, tag_list)))
                if d > best_match:
                    best_match = d
        count[best_match] += 1

    result = []
    for i in (5, 4, 3, 2, 1, 0):
        p = 0
        for k in range(i, 6):
            p += count[k]
        result.append((5 - i,
                       count[i],
                       count[i] / float(len(ground_truth_clusters)),
                       p / float(len(ground_truth_clusters))))
    return result


def calc_f_measure(ground_truth, ground_truth_rep, f_beta_constant):
    """
    Combine ground truth (precision) and ground truth represented (recall) to
     get the f-measure values for each overlap level.
    :param ground_truth:
    :param ground_truth_rep:
    :param f_beta_constant:
    :return:
    """
    f_measure_results = []
    for i in range(len(ground_truth)):
        precision = ground_truth[i][2]  # Get precision fraction
        recall = ground_truth_rep[i][2]  # Get recall fraction

        ## Calc F-measure as the weighted average of precision and recall
        f_measure = float(0)
        if not (precision == 0 and recall == 0):  # Never divide by zero
            numerator = precision * recall
            denominator = (math.pow(f_beta_constant, 2) * precision) + recall
            f_measure = (1 + math.pow(f_beta_constant, 2)) * (
                numerator / denominator)

        f_measure_results.append((ground_truth[i][0], f_measure))
    return f_measure_results


def calc_overall_precision(ground_truth_clusters, clusters, no_of_sources):
    """Calculate precision of clusters given ground truth clusters

    This method implements an overall precision measurement based on the
    formula for the overall F-Measure described in the article:
    http://dx.doi.org/10.1145/1242572.1242590

    :type ground_truth_clusters: dict
    :param ground_truth_clusters: mapping tags to source list
    :type: list
    :param clusters: cluster objects
    :type no_of_sources: int
    :param no_of_sources: the number of sources in the collection
    :rtype: float
    :return: the precision of the cluster result
    """
    overall_precision = 0.0
    ## For each category (gtctags) in groundTruthClusters
    for ground_truth_tags in ground_truth_clusters.keys():
        sources = ground_truth_clusters.get(ground_truth_tags)
        ## Find factor of category sources length to document number
        category_factor = float(len(sources)) / float(no_of_sources)
        max_precision = 0.0
        ## Find max precision out of all clusters j given category i
        for cluster in clusters:

            intersection_length = float(len(set(sources) &
                                           set(cluster.sources)))

            precision = intersection_length / float(len(cluster.sources))

            if precision > max_precision:
                max_precision = precision

        overall_precision += category_factor * max_precision

    return overall_precision


def calc_overall_recall(ground_truth_clusters, clusters, no_of_sources):
    """Calculate recall of clusters given ground truth clusters

    This method implements an overall recall measurement based on the
    formula for the overall F-Measure described in the article:
    http://dx.doi.org/10.1145/1242572.1242590

    :type ground_truth_clusters: dict
    :param ground_truth_clusters: mapping tags to source list
    :type: list
    :param clusters: cluster objects
    :type no_of_sources: int
    :param no_of_sources: the number of sources in the collection
    :rtype: float
    :return: the recall of the cluster result
    """
    overall_recall = 0.0
    ## For each category (gtctags) in groundTruthClusters
    for ground_truth_tags in ground_truth_clusters.keys():
        sources = ground_truth_clusters.get(ground_truth_tags)
        ## Find factor of category sources length to document number
        category_factor = float(len(sources)) / float(no_of_sources)
        max_recall = 0.0
        ## Find max precision out of all clusters j given category i
        for cluster in clusters:
            intersection_length = float(len(set(sources) &
                                            set(cluster.sources)))

            recall = intersection_length / float(len(sources))

            if recall > max_recall:
                max_recall = recall

        overall_recall += category_factor * max_recall

    return overall_recall


def calc_overall_fmeasure(ground_truth_clusters,
                          clusters,
                          no_of_sources,
                          f_beta_constant):
    """Calculate F-measure of clusters given ground truth clusters

    This method implements the formula for the overall F-Measure
    described in the article: http://dx.doi.org/10.1145/1242572.1242590

    :type ground_truth_clusters: dict
    :param ground_truth_clusters: mapping tags to source list
    :type: list
    :param clusters: cluster objects
    :type no_of_sources: int
    :param no_of_sources: the number of sources in the collection
    :rtype: float
    :return: the f-measure of the cluster result
    """
    overall_f_measure = 0.0
    ## For each category (gtctags) in groundTruthClusters
    for ground_truth_tags in ground_truth_clusters.keys():
        sources = ground_truth_clusters.get(ground_truth_tags)
        ## Find factor of category sources length to document number
        category_factor = float(len(sources)) / float(no_of_sources)
        max_f_measure = 0.0
        ## Find max precision out of all clusters j given category i
        for cluster in clusters:
            intersectionLength = float(len(set(sources) &
                                           set(cluster.sources)))

            precision = intersectionLength / float(len(cluster.sources))

            recall = intersectionLength / float(len(sources))

            f_measure = 0.0
            f_beta_constant = math.pow(f_beta_constant, 2)
            fMeasureNum = (f_beta_constant + 1) * precision * recall
            fMeasureDen = (f_beta_constant * precision) + recall

            if not fMeasureDen == 0:
                f_measure = fMeasureNum / fMeasureDen
            if f_measure > max_f_measure:
                max_f_measure = f_measure

        overall_f_measure += category_factor * max_f_measure

    return overall_f_measure


def list_contains_list(list1, list2):
    """
    See if list 2 is contained within list 1
    :type list1: list
    :param list1: first list
    :type list2: list
    :param list2: second list
    :return: True if list1 contains list 2, else False
    """
    for element in list2:
        if element not in list1:
            return False
    return True