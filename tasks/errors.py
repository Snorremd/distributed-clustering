class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class NoTasksError(Error):

    """Exception raised for errors in the input.

    :type msg: str
    :param msg: the message to insert in error object
    """
    def __init__(self, msg):
        Error.__init__(self, msg)


class TaskExecutionError(Error):

    """Exception raised if task execution errors occurs

    :type msg: str
    :param msg: the message to insert in error object
    :type task: task.Task
    """
    def __init__(self, msg, task):
        Error.__init__(self, msg)
        self.task = task
