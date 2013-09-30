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

    def __init__(self, timeoutSeconds, tasks):
        """Initialize StringCounterServer
        """
        Subject.__init__(self)
        self.logger = get_logger_for_stdout("TaskOrganizer")
        self.taskLength = 0
        self.pendingTasks = deque(tasks)
        self.activeTasks = {}
        self.results = {}
        self.timeout = timeoutSeconds

    def add_tasks(self, tasks):
        """Add all elements of tasks to pending tasks
        """
        self.pendingTasks.extend(tasks)
        self.taskLength = len(tasks)

    def get_task(self):
        """Get first remaning Task if any

        Returns:
            A Task id and first available Task object.
            If none available, raise NoTasksError.
        """
        try:
            task = self.pendingTasks.popleft()
        except IndexError:
            raise NoTasksError("There are no remaining tasks in" +
                               " pendingTasks deque")
        else:  # No exceptions raised
            self.make_task_active(task)
            return task

    def get_tasks(self, noOfTasks):
        """Get n number of tasks from Task list

        Args:
            noOfTasks (int): number of tasks to get

        Returns:
            a dict containing taskId, Task pairs
        """
        tasks = []
        for _ in range(noOfTasks):
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
        '''Add a Task to the active jobs dictionary

        Args:
            Task (Task): The Task to make active

        Returns:
            currentTime (object) of when Task was created
        '''
        currentTime = datetime.now()
        self.activeTasks[task.taskId] = (task, currentTime)
        return currentTime

    def check_active_tasks(self):
        '''Check active tasks for timeouts

        For each Task in active tasks, check if the
        Task has timed out, and if so reinsert into
        pendingTasks deque and remove from active tasks dict.
        '''
        currentTime = datetime.now()
        for taskId, taskTuple in list(self.activeTasks.items()):
            timestamp = taskTuple[1]
            difference = currentTime - timestamp
            if difference.seconds > self.timeout:
                self.pendingTasks.append(self.activeTasks[taskId][0])
                del self.activeTasks[taskId]

    def task_active(self, taskId):
        '''Check if a Task is still active

        Args:
            taskId (object): the id of the Task to be checked

        Returns:
            True if Task still active, False if not
        '''
        if taskId in self.activeTasks:
            return True
        else:
            return False

    def finish_task(self, result):
        '''Finish Task

        Args:
            taskId (object): the idTaskthe task to finish
            result (Result): the finished result
        '''
        self.results[result.taskId] = result
        del self.activeTasks[result.taskId]

    def finish_tasks(self, results):
        '''Finish the identified tasks with the given results

        Args:
            results (list): result objects with task id and result
        '''
        for result in results:
            if self.task_active(result.taskId):
                self.finish_task(result)
        if self.tasks_finished():
            self.notify()

    def tasks_finished(self):
        '''Check if results are finished
        '''
        if len(self.pendingTasks) == 0 and \
           len(self.activeTasks) == 0 and \
           len(self.results) == self.taskLength:
            return True
        else:
            return False

    def get_all_results(self):
        allResults = list(self.results.values())
        self.results = {}
        return allResults
