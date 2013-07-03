from datetime import datetime
from tasks.result import CompactTrieClusteringResult


class Task(object):

    """Class modelling one Task to execute.
    """

    def __init__(self):
        """
        Task class initializer
        """
        self.taskId = datetime.now()

    def is_timed_out(self, timeoutInSeconds):
        """
        Determine if a task has timed out

        :type timeoutInSeconds: int
        :param timeoutInSeconds: number of seconds before a task times out
        :rtype: bool
        :return: if task is timed out or not
        """
        currentTime = datetime.now()
        timeDifference = currentTime - self.taskId
        if timeDifference.seconds > timeoutInSeconds:
            return True
        else:
            return False

    def execute(self):
        """
        """
        return None


class CompactTrieClusteringTask(Task):

    """
    A class to do one clustering task
    """

    def __init__(self, chromosome):
        """
        Class initializer

        :type chromosome: geneticalgorithm.chromosome.Chromosome
        :param chromosome: the chromosome with parameters to use for clustering
        """
        Task.__init__(self)
        self.chromosome = chromosome

    def execute(self, *args):
        """
        Execute the compact trie clustering task

        :type args: list
        :param args: list of arguments
        """
        clusterer = args[0]
        self.chromosome.calc_fitness_score(clusterer)
        return CompactTrieClusteringResult(self.taskId, self.chromosome)
