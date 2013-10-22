"""
The server module contains two classes, Server and ClientHandler,
needed to serve and receive tasks and results. The Server class use asynchat
to handle incoming connections and creates ClientHandler objects to
communicate with clients.
"""

import socket
import asynchat
import asyncore
from pickle import PickleError
from easylogging.configLogger import get_logger_for_stdout
from tasks.errors import NoTasksError
from messaging.message import *
from scores.scoreBoard import ScoreBoard
from messaging.pickling import serialize_message, deserialize_message


class Server(asyncore.dispatcher):
    """
    Receive connections and establish handlers for each client
    """

    def __init__(self, address, programId, timeoutSeconds, taskOrganizer,
                 gAlgorithm, batchSize):
        """
        Initialize Server class

        :type address: tuple
        :param address: the ip/domain:socket pair the server should listen to
        :type timeoutSeconds: int
        :param timeoutSeconds: number of seconds until a task time out
        :type TaskOrganizer: tasks.taskOrganizer.TaskOrganizer
        :param TaskOrganizer: the object responsible for organizing tasks
        :type gAlgorithm: geneticalgorithm.geneticAlgorithm.GeneticAlgorithm
        :param gAlgorithm: the genetic algorithm responsible for evolution
        :type batchSize: int
        :param batchSize: the number of tasks to send to client in one batch
        """
        asyncore.dispatcher.__init__(self)

        self.logger = get_logger_for_stdout("Server")

        self.programId = programId
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

    def initiate_send(self):
        self.sending.acquire()
        asynchat.async_chat.initiate_send(self)
        self.sending.release()

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
        self.logger = get_logger_for_stdout("ClientHandler")
        asynchat.async_chat.__init__(self, sock=clientSock)
        self.server_socket = serverSocket

        self.logger.debug("Create ClientHandler")

        self.clientId = clientAddress
        self.username = "Unspecified"
        self.program_id = serverSocket.programId
        self.batchSize = serverSocket.batchSize

        self.taskOrganizer = serverSocket.taskOrganizer
        self.current_tasks = {}

        self.gAlgorithm = serverSocket.gAlgorithm

        self.scoreBoard = scoreBoard

        self.authorized = False

        self.received_data = []  # Byte data from user

        self.set_terminator(str.encode('</' + self.program_id + '>'))

        return

    def collect_incoming_data(self, data):
        """
        Collect data from incoming network stream and insert into data list

        :type data: byte
        :param data: incoming data
        """
        self.received_data.append(data)

    def found_terminator(self):
        """
        Found the terminator in the input from the client
        """
        self.process_message()

    def process_message(self):
        """
        Received all command input from client. Send back data
        """
        byte_input = b''.join(self.received_data)  # Complete data from client
        self.taskOrganizer.check_active_tasks()

        try:
            message = deserialize_message(byte_input)
        except PickleError:
            error_message = ErrorMessage("Could not deserialize message",
                                        "Deserialization error")
            self.send_message(error_message)
        else:
            if isinstance(message, RequestMessage):
                self.send_client_tasks()
            elif isinstance(message, ResultMessage):
                self.handle_client_results(message)
            elif isinstance(message, AuthenticationMessage):
                self.authenticate_client(message)
            elif isinstance(message, DisconnectMessage):
                self.disconnect_client(message)
        self.received_data = []

    def send_message(self, message):
        """
        Sends a message object to a client

        :type message: messaging.message.Message
        :param message: Message (or subclass) object to send to client
        """
        pickled_message = serialize_message(message)
        self.push(pickled_message + self.get_terminator())

    def authenticate_client(self, message_obj):
        """
        Authenticate client by checking messages auth data against program id.
        If successful send an positive auth-message, if not send an negative
        AuthenticationErrorMessage.

        :type message_obj: messaging.message.AuthenticationMessage
        :param message_obj: the auth message containing auth info
        """
        if message_obj.authData == self.program_id:
            self.authorized = True
            self.username = message_obj.username
            self.scoreBoard.increase_user_score(self.username, 0)
            auth_message = AuthenticationMessage("Authentication succeeded",
                                                 "Authentication data was "
                                                 "correct", self.username)
            self.logger.debug("Client with username {0} and id {1} "
                              "successfully authenticated!"
                              .format(self.username, self.clientId))
            self.send_message(auth_message)

        else:
            error_message = AuthErrorMessage("Authentification failed",
                                             message_obj.authData,
                                             "Auth data was not correct")
            self.send_message(error_message)
            self.server_socket.remove_client(self.clientId)
            self.close_when_done()

    def disconnect_client(self, message):
        """
        Disconnect client, close socket and send the client's disconnect
        message to client handler log.

        :type message: messaging.message.DisonnectMessage
        :param message: message from client
        """
        self.server_socket.remove_client(self.clientId)
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
            error_message = NoTasksMessage("No tasks error",
                                          "Currently no tasks to execute")
            self.send_message(error_message)
        else:
            self.set_current_tasks(tasks)
            task_message = ClusterTaskMessage("Task:", tasks,
                                             self.gAlgorithm.corpus,
                                             self.gAlgorithm.clusterSettings)
            self.send_message(task_message)

    def set_current_tasks(self, tasks):
        """
        Stores the tasks currently being worked on by the client in a
        dictionary. taskId used as key.

        :type tasks: list
        :param tasks: task objects being worked on
        """
        self.current_tasks = {}  # Just in case
        for task in tasks:
            self.current_tasks[task.taskId] = task

    def handle_client_results(self, result_message):
        """
        Checks authenticity of results in result message and sends results to
         the task organizer. Also updates the user's score.

        :type result_message: messaging.message.ResultMessage
        :param result_message: message containing tasks results
        """
        results = result_message.results
        if self.check_result_authenticity(results):
            self.logger.debug("{0} tasks authenticated".format(len(results)))
            self.taskOrganizer.finish_tasks(results)
            self.scoreBoard.increase_user_score(self.username, len(results))
            self.send_client_scores()
        else:
            self.logger.debug("Client tasks not authenticated")
            message = TaskAuthenticationError("Task authentication error",
                                              list(results.keys()))
            self.send_message(message)
        self.current_tasks = {}

    def check_result_authenticity(self, results):
        """
        Check if results from client match current task ids

        :type results: list
        :param results: results from client
        :rtype: bool
        :return: if taskIds match with activeTasks
        """
        if all(result.taskId in self.current_tasks for result in results):
            return True
        else:
            return False

    def send_client_scores(self):
        """
        Send clients score and top 100 scores to client
        """
        user_score = self.scoreBoard.get_user_score(self.username)
        scores = list(self.scoreBoard.get_user_ranks().items())[:10]
        tasks_total = self.taskOrganizer.task_length
        tasks_done = self.taskOrganizer.get_no_completed_tasks()
        tasks_remaining = self.taskOrganizer.get_no_remaining_tasks()
        score_message = ScoreMessage("Scores", user_score, scores, tasks_done, tasks_total, tasks_remaining)
        self.send_message(score_message)
