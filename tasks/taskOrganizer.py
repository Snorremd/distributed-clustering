from collections import deque
from .errors import NoTasksError
from datetime import datetime
from easylogging.configLogger import get_logger_for_stdout


class Subject:
    """Subject in observer pattern

    Source: http://code.activestate.com/recipes/131499-observer-pattern/
    """
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if not observer in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update()


class TaskOrganizer(Subject):

    """Handles tasks and results

    Params:
        taskLength (int): current no of tasks to execute
        pendingTasks (deque): a task deque of pending tasks
        activeTasks (dict): a dict of taskids and tasks for active tasks
        results (dict): a dict of taskids and corresponding results
        timeout (int): task timeout-limit in seconds
    """

    def __init__(self, timeout_seconds, tasks):
        """Initialize StringCounterServer
        """
        Subject.__init__(self)
        self.logger = get_logger_for_stdout("TaskOrganizer")
        self.task_length = 0
        self.pending_tasks = deque(tasks)
        self.active_tasks = {}
        self.results = {}
        self.timeout = timeout_seconds

    def add_tasks(self, tasks):
        """Add all elements of tasks to pending tasks
        """
        self.pending_tasks.extend(tasks)
        self.task_length = len(tasks)

    def get_task(self):
        """Get first remaning Task if any

        Returns:
            A Task id and first available Task object.
            If none available, raise NoTasksError.
        """
        try:
            task = self.pending_tasks.popleft()
        except IndexError:
            raise NoTasksError("There are no remaining tasks in" +
                               " pendingTasks deque")
        else:  # No exceptions raised
            self.make_task_active(task)
            return task

    def get_tasks(self, no_of_tasks):
        """Get n number of tasks from Task list

        Args:
            noOfTasks (int): number of tasks to get

        Returns:
            a dict containing taskId, Task pairs
        """
        tasks = []
        for _ in range(no_of_tasks):
            try:
                task = self.get_task()
            except NoTasksError:
                break
            else:
                tasks.append(task)
        if not len(tasks) == 0:
            return tasks
        else:
            raise NoTasksError("There are no remaining tasks in" +
                               " pendingTasks deque")

    def make_task_active(self, task):
        """Add a Task to the active jobs dictionary

        Args:
            Task (Task): The Task to make active

        Returns:
            currentTime (object) of when Task was created
        """
        current_time = datetime.now()
        self.active_tasks[task.taskId] = (task, current_time)
        return current_time

    def check_active_tasks(self):
        """Check active tasks for timeouts

        For each Task in active tasks, check if the
        Task has timed out, and if so reinsert into
        pendingTasks deque and remove from active tasks dict.
        """
        current_time = datetime.now()
        for taskId, taskTuple in list(self.active_tasks.items()):
            timestamp = taskTuple[1]
            difference = current_time - timestamp
            if difference.seconds > self.timeout:
                self.pending_tasks.append(self.active_tasks[taskId][0])
                del self.active_tasks[taskId]

    def task_active(self, task_id):
        """
        Check if a Task is still active

        Args:
            taskId (object): the id of the Task to be checked

        Returns:
            True if Task still active, False if not
        """
        if task_id in self.active_tasks:
            return True
        else:
            return False

    def finish_task(self, result):
        """
        Finish Task

        Args:
            taskId (object): the idTaskthe task to finish
            result (Result): the finished result
        """
        self.results[result.taskId] = result
        del self.active_tasks[result.taskId]

    def finish_tasks(self, results):
        """
        Finish the identified tasks with the given results

        Args:
            results (list): result objects with task id and result
        """
        for result in results:
            if self.task_active(result.taskId):
                self.finish_task(result)
        if self.tasks_finished():
            self.notify()
        self.logger.debug("{0} out of {1} tasks completed!"\
            .format(self.get_no_completed_tasks(), self.task_length))


    def tasks_finished(self):
        """
        Check if results are finished
        """
        if len(self.pending_tasks) == 0 and \
           len(self.active_tasks) == 0 and \
           len(self.results) == self.task_length:
            return True
        else:
            return False

    def get_all_results(self):
        """
        Get all results from task TaskOrganizer
        :rtype: list
        :return: task results
        """
        all_results = list(self.results.values())
        self.results = {}
        return all_results

    def get_no_remaining_tasks(self):
        """
        Find the number of remaining tasks
        :rtype: int
        :return: number of remaining tasks|
        """
        return len(self.pending_tasks)

    def get_no_completed_tasks(self):
        """
        Get the number of completed tasks
        :rtype: int
        :return: number of completed tasks
        """
        return len(self.results)