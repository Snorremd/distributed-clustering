"""
The main client module used to start the client worker.
"""
from easylogging.configLogger import getLoggerForStdOut
from client.client import Client
import asyncore
import socket
from time import sleep
import sys
from inputOutput.output import show_info_dialog, show_input_dialog, show_option_dialog


if __name__ == '__main__':

    choice = show_option_dialog("Do you want to use default options?", ["yes",
                                                                   "no"])
    if(choice == "yes"):
        client = Client(("localhost",9876), "lol", "snorre")
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

        mainLogger = getLoggerForStdOut("Main")
        address = (hostAddress, int(port))
        client = None
        try:
            client = Client(address, programId, username)
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
