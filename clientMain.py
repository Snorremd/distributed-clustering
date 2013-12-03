#!/usr/bin/python
"""
The main client module used to start the client worker.
"""
from easylogging.configLogger import get_logger_for_stdout
from client.client import Client
import asyncore
import socket
from time import sleep
import sys
from inputOutput.filehandling import get_client_config
from inputOutput.output import show_info_dialog, show_input_dialog, show_option_dialog


if __name__ == '__main__':

    choice = show_option_dialog("Do you want to use config file?",
                                ["yes", "no"])
    if choice == "yes":
        address, port, programId, username, timeout = get_client_config()
        client = Client((address, int(port)), programId, username, int(timeout))
        asyncore.loop()
    else:
        show_info_dialog("This client is intended to run on one processor core "
                         "and calculates results from clustering documents given "
                         "a set of parameters (received from server). If you want"
                         " to use more cores, run additional clients. You can "
                         "exit the client at any time by pressing ctrl + c.\n")

        hostAddress = show_input_dialog("Please type in the ip address or domain "
                                        "name of the host on the form '0.0.0.0' "
                                        "or 'domain.com': ")

        port = show_input_dialog("Please input the port the server listens to: ")

        programId = show_input_dialog("Please specify programId: ")

        username = show_input_dialog("Please input a wanted username: ")

        timeout = show_input_dialog("Please input a timeout of at least 30 seconds (how long to"
                                    " wait when no tasks are available): ")

        mainLogger = get_logger_for_stdout("Main")
        address = (hostAddress, int(port))
        client = None
        try:
            client = Client(address, programId, username, int(timeout))
            asyncore.loop()
        except socket.error:
            # Server probably busy
            mainLogger.debug("Could not connect to server with address {0} and "
                             "port {1}. Please restart script"
                             .format(hostAddress, port))
        except KeyboardInterrupt:
            try:
                if client:
                    mainLogger.debug("Attempting to disconnect from server.\n" +
                                     "Press ctrl + C again to force close script.")
                    client.disconnect("User cancelled script")
            except KeyboardInterrupt:
                sys.exit(0)
