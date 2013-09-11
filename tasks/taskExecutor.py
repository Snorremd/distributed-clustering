'''
Created on May 13, 2013

@author: snorre
'''
## from memory_profiler import profile
from tasks.task import Task
from tasks.errors import TaskExecutionError
from cluster.clustering import CompactTrieClusterer


class TaskExecutor:

    def __init__(self, message):
        self.message = message

    def execute_tasks(self):
        '''Return results for tasks list

        Args:
            tasks (list): tasks to execute

        Returns:
            a list containing results

        Raises:
            TaskExecutionError if task value is of wrong type

        '''
        try:
            results = []
            for task in self.message.tasks:
                results.append(self.execute_task(task))
            return results
        except TaskExecutionError:
            raise

    def execute_task(self, task, *args):
        '''Executes a task and returns the given result

        Args:
            task (Task): the task to execute

        Returns:
            result from of executing task

        Raises:
            TypeError if task value is not of type Task (or subclass)
        '''
        if hasattr(task, "execute"):
            return task.execute(*args)
        else:
            raise TaskExecutionError("task has to have execution " + \
                                     "method", task)


class ClusteringTaskExecutor(TaskExecutor):

    def __init__(self, message):
        TaskExecutor.__init__(self, message)
        self.clusterer = CompactTrieClusterer(message.corpus,
                                              message.settings)

    def execute_task(self, task):
        return TaskExecutor.execute_task(self, task, self.clusterer)
