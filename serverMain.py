"""
The server module allows you to run the genetic algorithm and asynchat server.
"""
import asyncore
import os
import sys
from xml.etree import ElementTree as ET
from cluster.clusterSettings import ClusterSettings

from easylogging.configLogger import get_logger_for_stdout
from inputOutput.db import DbHandler
from inputOutput.filehandling import get_root_path, get_corpus_options, get_server_config, get_corpus_settings
from inputOutput.output import show_info_dialog, show_input_dialog, \
    show_option_dialog
from server.server import Server
import geneticalgorithm.geneticAlgorithm as geneticAlgorithm
from geneticalgorithm.geneticAlgorithm import GeneticAlgorithm
from tasks.taskOrganizer import TaskOrganizer

if __name__ == '__main__':
    show_info_dialog("This server runs a distributed genetic algorithm for "
                     "optimization of parameters for the compact trie "
                     "clustering algorithm. The server use a task organizer "
                     "to organize chromosomes for which to calculate fitness,"
                     " and the asynchat library to communicate with clients"
                     ".\n")

    choice = show_option_dialog("Do you want to use config file?",
                                ["y", "n"])
    if choice == "y":
        hostAddress, port, programId, batchSize, drop_singleton_gt,\
            timeout, populationSize, max_generations, corpusName,\
            dbhost, dbname, dbuser, dbpasswd = get_server_config()

    else:
        hostAddress = show_option_dialog("Please type in one of the two options "
                                         "for listening locally or externally: ",
                                         ['localhost', '0.0.0.0'])

        port = show_input_dialog("Please input the port the server should listen "
                                 "to: ")

        programId = show_input_dialog("Please specify a programId: ")

        batchSize = show_input_dialog("Please specify a batch size (should "
                                      "preferably take no more than 60 seconds to"
                                      " complete): ")

        drop_singleton_gt = show_option_dialog("Should we drop singleton ground truth clusters?", ["True", "False"])

        timeout = show_input_dialog("Specify task timeout in seconds (make this a"
                                    " multiple of task completion time and batch "
                                    "size): ")

        populationSize = show_input_dialog("Please specify a population size: ")

        max_generations = show_input_dialog("Please specify the max number of generations: ")

        corpusName = show_input_dialog("Specify one of the following corpora:",
                                   get_corpus_options())

        dbhost = show_input_dialog("Specify dbhost (localhost/X.X.X.X: ")

        dbname = show_input_dialog("Specify database: ")

        dbuser = show_input_dialog("Specify user: ")

        dbpasswd = show_input_dialog("Specify password: ")


    mainLogger = get_logger_for_stdout('Main')
    mainLogger.debug("Create genetic algorithm object and initial population")
    try:

        dbHandler = DbHandler(dbhost, dbname, dbuser, dbpasswd)
        if dbHandler.tables_exists():
            choice = show_option_dialog("Tables already exist, do you want to "
                                        "delete and create new ones?", ["yes",
                                        "no"])

            if choice == "yes":
                dbHandler.drop_tables()

            else:
                mainLogger.debug("Please remove/backup tables and recreate "
                                 "before restarting script.")
                exit(0)

        dbHandler.create_all_tables()


        corpus = get_corpus_settings(corpusName)

        cluster_settings = ClusterSettings(eval(drop_singleton_gt), 2.0, False)

        taskOrganizer = TaskOrganizer(int(timeout), [])
        gAlgorithm = GeneticAlgorithm(taskOrganizer, dbHandler,
                                      corpus, int(populationSize), int(max_generations),
                                      GeneticAlgorithm.ROULETTEWHEEL,
                                      0.8, 0.01, geneticAlgorithm.VERBOSEFILE,
                                      cluster_settings)

        ## Start server and asyncore loop
        server = Server((hostAddress, int(port)), programId, int(timeout),
                        taskOrganizer, gAlgorithm, int(batchSize))
        mainLogger.debug("Created server to listen on %s:%s" %
                         server.address)
        mainLogger.debug("Start asyncore loop")
        asyncore.loop()

    except KeyboardInterrupt:
            try:
                mainLogger.debug("Server might still be running, do you really want "
                                 "to end server process?\n" +
                                 "Press ctrl + C again to force close script.")
            except KeyboardInterrupt:
                sys.exit(0)