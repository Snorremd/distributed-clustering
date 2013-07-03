"""
This module contain result classes to model different types of results.
"""


class Result(object):
    """
    The Result class act as a base class and specifies a single attribute
    taskId. This attribute is needed to uniquely identify a result.
    """

    def __init__(self, taskId):
        """
        Result constructor

        :type taskId: str
        :param taskId: the taskId to which the result belong
        """
        self.taskId = taskId


class CompactTrieClusteringResult(Result):

    """
    Class for giving clustering results and fitness
    """

    def __init__(self, taskId, chromosome):
        """
        :type taskId: datetime
        :param taskId: the taskId to which the result belong
        :type chromosome: geneticAlgorithm.chromosome.Chromosome
        :param chromosome: the chromosome with the resulting fitness
        """
        Result.__init__(self, taskId)
        self.chromosome = chromosome
