class Message(object):
    """
    Base class for message that can be sent between server and client
    """

    def __init__(self, message):
        """
        Initialize class
        :type message: str
        :param message: message to send
        """
        self.message = message


class AuthenticationMessage(Message):
    """
    Message containing authentication data
    """
    def __init__(self, message, authData, username):
        """
        Initialize class
        :type message: str
        :param message: message to send
        :type authData: str
        :param authData: program id
        :type username: str
        :param username: name of user
        """
        Message.__init__(self, message)
        self.authData = authData
        self.username = username


class AuthErrorMessage(AuthenticationMessage):
    """
    Message containing auth error data
    """

    def __init__(self, message, authData, error):
        """
        Initialize class
        :type message: str
        :param message: message to send
        :type authData: str
        :param authData: program id
        :type error: str
        :param error: error message related to authentication
        """
        AuthenticationMessage.__init__(self, message, authData)
        self.error = error


class TaskMessage(Message):
    """
    Message containing task to execute
    """
    def __init__(self, message, tasks):
        """
        Initialize class
        :type message: str
        :param message: message to send
        :type tasks: list
        :param tasks: the tasks the client should execute
        """
        Message.__init__(self, message)
        self.tasks = tasks


class ClusterTaskMessage(TaskMessage):
    """
    Contains clustering task
    """
    def __init__(self, message, tasks, corpus, settings):
        TaskMessage.__init__(self, message, tasks)
        self.corpus = corpus
        self.settings = settings


class NoTasksMessage(Message):
    """
    Message containing "no task info"
    """
    def __init__(self, message, noTasksInfo):
        """
        Class initializer
        :type message: str
        :param message: message to send
        :type noTasksInfo: str
        :param noTasksInfo: info about task organizer status
        """
        Message.__init__(self, message)
        self.noTasksInfo = noTasksInfo


class TaskAuthenticationError(Message):
    """
    Message containing task auth error
    """
    def __init__(self, message, taskIds):
        """
        :type message: str
        :param message: message to send
        :type taskIds: list
        :param taskIds: the id of tasks that could not be authenticated
        """
        Message.__init__(self, message)
        self.taskids = taskIds


class ResultMessage(Message):
    """
    Message containing results from client
    """
    def __init__(self, message, results):
        Message.__init__(self, message)
        self.results = results


class RequestMessage(Message):
    """
    Message containing a task request
    """
    def __init__(self, message):
        """
        Class initializer
        :type message: str
        :param message: message to send
        """
        Message.__init__(self, message)


class ErrorMessage(Message):
    """
    Message containing error message
    """
    def __init__(self, message, error):
        """
        Class initializer
        :type message: str
        :param message: message to send
        :type error: str
        :param error: the error message
        """
        Message.__init__(self, message)
        self.error = error


class ScoreMessage(Message):
    """
    Message containing scoreboard info
    """
    def __init__(self, message, userScore, topScores):
        """
        :type message: str
        :param message: message to send
        :type userScore: int
        :param userScore: the score of the user
        :type topScores: set
        :param topScores: the n top users with scores
        """
        Message.__init__(self, message)
        self.userScore = userScore
        self.topScores = topScores


class DisconnectMessage(Message):
    """
    Disconnection message for client or server
    """
    def __init__(self, message, disconnectInfo):
        """
        :type message: str
        :param message: message to send
        :type disconnectInfo: str
        :param disconnectInfo: info about the disconnect
        """
        Message.__init__(self, message)
        self.disconnectInfo = disconnectInfo
