"""
The server module contains two classes, Server and ClientHandler,
needed to serve and receive tasks and results. The Server class use asynchat
to handle incoming connections and creates ClientHandler objects to
communicate with clients.
"""

from _socket import socket
import asynchat
import asyncore
from pickle import PickleError
from easylogging.configLogger import getLoggerForStdOut
from tasks.errors import NoTasksError
from messaging.message import *
from scores.scoreBoard import ScoreBoard
from messaging.pickling import serialize_message, deserialize_message


class Server(asyncore.dispatcher):
    """
    Receive connections and establish handlers for each client
    """

    def __init__(self, address, timeoutSeconds, taskOrganizer,
                 gAlgorithm, batchSize):
        """
        Initialize Server class

        :type address: tuple
        :param address: the ip/domain:socket pair the server should listen to
        :type timeoutSeconds: int
        :param timeoutSeconds: number of seconds until a task time out
        :type taskOrganizer: tasks.taskOrganizer.TaskOrganizer
        :param taskOrganizer: the object responsible for organizing tasks
        :type gAlgorithm: geneticalgorithm.geneticAlgorithm.GeneticAlgorithm
        :param gAlgorithm: the genetic algorithm responsible for evolution
        :type batchSize: int
        :param batchSize: the number of tasks to send to client in one batch
        """
        asyncore.dispatcher.__init__(self)

        self.logger = getLoggerForStdOut("Server")

        self.programId = "StringCounter"
        self.timeoutSeconds = timeoutSeconds  # REMOVE THIS!
        self.batchSize = batchSize
        self.clientSockets = {}

        self.taskOrganizer = taskOrganizer
        self.scoreBoard = ScoreBoard()

        self.gAlgorithm = gAlgorithm

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4, TCP
        self.bind(address)
        self.address = self.socket.getsockname()
        self.logger.debug("Created server socket at " + str(self.address))
        self.listen(50)
        return

    #    def initiate_send(self):
    #        self.sending.acquire()
    #        asynchat.async_chat.initiate_send(self)
    #        self.sending.release()

    def handle_accept(self):
        """
        Handle incoming calls from client
        """
        clientInfo = self.accept()  # Should return socket and address
        client = ClientHandler(clientInfo[0], clientInfo[1], self,
                               self.scoreBoard)
        self.clientSockets[client.clientId] = client  # Add with unique id

    def handle_close(self):
        """
        Close server socket
        """
        self.logger.debug("Server closing server socket")
        self.close()

    def remove_client(self, clientId):
        """
        Remove the identified client from the list

        :type clientId: str
        :param clientId: id of client to be removed
        """
        del self.clientSockets[clientId]


class ClientHandler(asynchat.async_chat):
    """
    Handle communication with single client socket
    """
    # Use default buffer size of 4096 bytes (4kb)
    def __init__(self, clientSock, clientAddress, serverSocket, scoreBoard):
        """
        Initialize class

        :type clientSock: _socket.socket
        :param clientSock: socket with which server communicate with client
        :type clientAddress: str
        :param clientAddress: the address of client's connection
        :type serverSocket: Server
        :param serverSocket: the Server instance
        :type scoreBoard: scores.scoreBoard.ScoreBoard
        :param scoreBoard: an object that keeps track of scores
        """
        self.logger = getLoggerForStdOut("ClientHandler")
        asynchat.async_chat.__init__(self, sock=clientSock)
        self.serverSocket = serverSocket

        self.clientId = clientAddress
        self.username = "Unspecified"
        self.programId = serverSocket.programId
        self.batchSize = serverSocket.batchSize

        self.taskOrganizer = serverSocket.taskOrganizer
        self.currentTasks = {}

        self.gAlgorithm = serverSocket.gAlgorithm

        self.scoreBoard = scoreBoard

        self.authorized = False

        self.receivedData = []  # String data from client

        self.set_terminator('</' + self.programId + '>')
        return

    def collect_incoming_data(self, data):
        """
        Collect data from incoming network stream and insert into data list

        :type data: str
        :param data: incoming data
        """
        self.receivedData.append(data)

    def found_terminator(self):
        """
        Found the terminator in the input from the client
        """
        self.process_message()

    def process_message(self):
        """
        Received all command input from client. Send back data
        """
        stringInput = ''.join(self.receivedData)  # Complete data from client
        self.taskOrganizer.check_active_tasks()
        # self.logger.debug('Process command: %s', command)
        try:
            message = deserialize_message(stringInput)
        except PickleError:
            errorMessage = ErrorMessage("Could not deserialize message",
                                        "Deserialization error")
            self.send_message(errorMessage)
        else:
            if isinstance(message, RequestMessage):
                self.send_client_tasks()
            elif isinstance(message, ResultMessage):
                self.handle_client_results(message)
            elif isinstance(message, AuthenticationMessage):
                self.authenticate_client(message)
            elif isinstance(message, DisconnectMessage):
                self.disconnect_client(message)
        self.receivedData = []

    def send_message(self, message):
        """
        Sends a message object to a client

        :type message: messaging.message.Message
        :param message: Message (or subclass) object to send to client
        """
        pickledMessage = serialize_message(message)
        self.push(pickledMessage + self.get_terminator())

    def authenticate_client(self, messageObj):
        """
        Authenticate client by checking messages auth data against program id.
        If successful send an positive auth-message, if not send an negative
        AuthenticationErrorMessage.

        :type messageObj: messaging.message.AuthenticationMessage
        :param messageObj: the auth message containing auth info
        """
        if messageObj.authData == self.programId:
            self.authorized = True
            self.username = messageObj.username
            self.scoreBoard.increase_user_score(self.username, 0)
            authMessage = AuthenticationMessage("Authentification suceeded",
                                                "Authentification data was "
                                                "correct", None)
            self.send_message(authMessage)

        else:
            errorMessage = AuthErrorMessage("Authentification failed",
                                            messageObj.authData,
                                            "Auth data was not correct")
            self.send_message(errorMessage)
            self.serverSocket.remove_client(self.clientId)
            self.close_when_done()

    def disconnect_client(self, message):
        """
        Disconnect client, close socket and send the client's disconnect
        message to client handler log.

        :type message: messaging.message.DisonnectMessage
        :param message: message from client
        """
        self.serverSocket.remove_client(self.clientId)
        self.close_when_done()
        self.logger.debug("Client disconnected (id: " + str(self.clientId) +
                          " ), because " + message.disconnectInfo)

    def send_client_tasks(self):
        """
        Send tasks from task organizer to client if any left. If no tasks
        remains, send error message to client.
        """
        try:
            tasks = self.taskOrganizer.get_tasks(self.batchSize)
        except NoTasksError:
            errorMessage = NoTasksMessage("No tasks error",
                                          "Currently no tasks to execute")
            self.send_message(errorMessage)
        else:
            self.set_current_tasks(tasks)
            taskMessage = ClusterTaskMessage("Task:", tasks,
                                             self.gAlgorithm.corpus,
                                             self.gAlgorithm.clusterSettings)
            self.send_message(taskMessage)

    def set_current_tasks(self, tasks):
        """
        Stores the tasks currently being worked on by the client in a
        dictionary. taskId used as key.

        :type tasks: list
        :param tasks: task objects being worked on
        """
        self.currentTasks = {}  # Just in case
        for task in tasks:
            self.currentTasks[task.taskId] = task

    def handle_client_results(self, resultMessage):
        """
        Checks authenticity of results in result message and sends results to
         the task organizer. Also updates the user's score.

        :type resultMessage: messaging.message.ResultMessage
        :param resultMessage: message containing tasks results
        """
        results = resultMessage.results
        if self.check_result_authenticity(results):
            self.logger.debug("Tasks authenticated")
            self.taskOrganizer.finish_tasks(results)
            self.scoreBoard.increase_user_score(self.username, len(results))
            self.send_client_scores()
        else:
            self.logger.debug("Client tasks not authenticated")
            message = TaskAuthenticationError("Task authentication error",
                                              results.keys())
            self.send_message(message)
        self.currentTasks = {}

    def check_result_authenticity(self, results):
        """
        Check if results from client match current task ids

        :type results: list
        :param results: results from client
        :rtype: bool
        :return: if taskIds match with activeTasks
        """
        if all(result.taskId in self.currentTasks for result in results):
            return True
        else:
            return False

    def send_client_scores(self):
        """
        Send clients score and top 100 scores to client
        """
        userScore = self.scoreBoard.get_user_score(self.username)
        scores = self.scoreBoard.get_user_ranks().items()[:100]
        scoreMessage = ScoreMessage("Scores", userScore, scores)
        self.send_message(scoreMessage)
