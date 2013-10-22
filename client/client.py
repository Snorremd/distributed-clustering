'''
Created on Apr 12, 2013

@author: snorre
'''

import asynchat
import socket

from easylogging.configLogger import get_logger_for_stdout
from time import sleep

from tasks import taskExecutor
from tasks.errors import TaskExecutionError

from messaging.message import *
from messaging.pickling import serialize_message, deserialize_message
from pickle import PickleError
from tasks.taskExecutor import ClusteringTaskExecutor


class Client(asynchat.async_chat):
    """
    Counts the length of strings received from server
    """

    def __init__(self, address, programId, username):
        """
        Constructor of Client class
        """
        asynchat.async_chat.__init__(self)

        self.logger = get_logger_for_stdout("Client")
        self.address = address

        self.programId = programId
        self.username = username
        self.set_terminator(str.encode('</' + programId + '>'))
        self.receivedData = []
        self.noOfCompletedTasks = 0

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4, TCP
        self.logger.debug('Connecting to %s, %s' % address)
        self.connect(address)
        return

    def handle_connect(self):
        """
        Push command to server to authenticate
        """
        self.logger.debug("Connected to server, push authentication data")
        authMessage = AuthenticationMessage("Connecting", self.programId,
                                            self.username)
        self.send_message(authMessage)
        return

    def handle_error(self):
        asynchat.async_chat.handle_error(self)
        self.logger.debug("Either Connection to server with address {0} and "
                          "port {1} failed or server broke connection. Please"
                          " try to restart clientMain script...".format(
                          *self.address))
        self.close()
        return

    def handle_expt(self):
        """
        Connection to server failed, handle exception
        """
        # connection failed
        self.logger.debug("Either Connection to server with address {0} and "
                          "port {1} failed or server broke connection. Please"
                          " try to restart clientMain script..."
                          .format(*self.address))
        self.close()
        return

    def disconnect(self, disconnectInfo):
        """
        Disconnect from server and close connection
        """
        message = DisconnectMessage("Client disconnected",
                                    disconnectInfo)
        self.send_message(message)
        self.close_when_done()
        self.logger.debug("Disconnected from server")
        return

    def collect_incoming_data(self, data):
        self.receivedData.append(data)
        return

    def found_terminator(self):
        self.process_message()
        return

    def process_message(self):
        receivedBytes = b''.join(self.receivedData)

        try:
            message = deserialize_message(receivedBytes)
        except PickleError:
            self.logger.debug("Could not deserialise message")
        else:
            if isinstance(message, TaskMessage):
                self.process_tasks(message)
            elif isinstance(message, TaskAuthenticationError):
                self.logger.debug("Tasks were not authenticated")
            elif isinstance(message, NoTasksMessage):
                self.logger.debug("Server returned NoTasksError " + \
                                  "with reason:\n" + message.noTasksInfo)
                sleep(10)
                self.send_task_request()
            elif isinstance(message, ScoreMessage):
                self.logger.debug("Received scores")
                self.output_scores(message)
                self.send_task_request()
            elif isinstance(message, AuthErrorMessage):
                self.logger.debug("Server returned AuthErrorMessage " + \
                                  "for tasks:\n" + str(message.taskIds))
                self.logger.debug("Could not authenticate with program id: " +
                                  self.programId + ". Closing client")
                self.close_when_done()
            elif isinstance(message, AuthenticationMessage):
                self.logger.debug("Successfully authenticated")
                self.send_task_request()

        self.receivedData = []
        return

    def send_message(self, messageObj):
        '''Serialize message and send to server
        '''
        try:
            message = serialize_message(messageObj)
        except PickleError:
            self.logger.debug("Could not serialize/pickle message")
            ##self.send_task_request()  # Ask for new Task
        else:
            self.push(message + self.get_terminator())
        return

    def send_task_request(self):
        '''Sends a Task request message to server
        '''
        message = RequestMessage("Request Task")
        self.send_message(message)
        return

    def process_tasks(self, message):
        '''Process n tasks and sends a results message to server

        Args:
            tasks (list): a map of taskIds and task objects

        '''
        self.logger.info("Process tasks received from server")
        if isinstance(message, ClusterTaskMessage):
            task_executor = ClusteringTaskExecutor(message)
            try:
                results = task_executor.execute_tasks()
            except TaskExecutionError as error:
                self.logger.debug("Could not execute task: {0}".format(error.task))

                self.disconnect("Could not execute tasks")
                self.logger.debug("Client disconnected from the server as " + \
                                  "it could not execute given tasks.")
            else:
                self.logger.debug("Send results to server\n\n\n\n")
                self.send_task_results(results)
                self.noOfCompletedTasks += len(results)
        return

    def send_task_results(self, results):
        '''Sends task results to the server

        Args:
            results (dict): a map of taskIds and results
        '''
        message = ResultMessage("Result", results)
        self.send_message(message)
        return

    def output_scores(self, score_message):
        """
        Outputs scores to the logger defined in self
        """
        score_output = \
            ("\n"
             "#####################################\n"
             "Total Tasks: {0}\n"
             "Tasks remaining: {1}    Tasks done: {2}\n"
             "#################\n"
             "Your score: {3}\n"
             "{4}\n")

        top_scores = self.get_scoreboard_string(score_message.topScores)
        score_output = score_output.format(score_message.tasks_total, score_message.tasks_remaining,
                                           score_message.tasks_done, score_message.userScore,
                                           top_scores)
        self.logger.debug(score_output + "\n\n\n")

    def get_scoreboard_string(self, top_scores):
        no_of_scores = len(top_scores)
        score_board_string = "Top " + str(no_of_scores) + " users:\n"
        for user, score in top_scores:
            score_board_string += "{0:15} : {1}\n".format(user, score)
        return score_board_string
