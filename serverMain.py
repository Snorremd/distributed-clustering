"""
The server module allows you to run the genetic algorithm and asynchat server.
"""
from easylogging.configLogger import getLoggerForStdOut
from server.server import Server
from tasks.task import StringTask
import geneticalgorithm.geneticAlgorithm as geneticAlgorithm
from geneticalgorithm.geneticAlgorithm import GeneticAlgorithm

import asyncore
from tasks.taskOrganizer import TaskOrganizer

if __name__ == '__main__':
    mainLogger = getLoggerForStdOut('Main')
    mainLogger.debug("Create genetic algorithm object and initial population")
    taskOrganizer = TaskOrganizer(200, [])
    gAlgorithm = GeneticAlgorithm(taskOrganizer, 20, 3,
                                  GeneticAlgorithm.ROULETTEWHEEL,
                                  0.5, 0.10, geneticAlgorithm.VERBOSEFILE)
    mainLogger.debug("Attach ga to task organizer")
    taskOrganizer.attach(gAlgorithm)

    server = Server(("localhost", 9874), 200, taskOrganizer, gAlgorithm, 10)
    mainLogger.debug("Created server to listen on %s:%s" %
                     server.address)
    mainLogger.debug("Start asyncore loop")
    asyncore.loop()
