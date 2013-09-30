"""
configLogger modile implements an easy way to get either a file logger or
console logger. This functionality is implemented through two functions,
getLoggerForStdOut and getLoggerForFile.
"""

import logging
import os
import sys
import time

import __main__


def get_logger_for_stdout(nameForLogger):
    """
    Get logger for stdout (console/terminal)

    :type nameForLogger: str
    :param nameForLogger: what to name the logger
    :rtype: Logger
    :return: the logger with specified name (with timestamp)
    """
    logger = logging.getLogger(nameForLogger + str(time.time()))
    logger.level = logging.DEBUG
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler = logging.StreamHandler(sys.stdout)
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    return logger


def get_logger_for_file(nameForLogger):
    """
    Get logger for file (console/terminal)

    :type nameForLogger: str
    :param nameForLogger: what to name the logger
    :rtype: Logger
    :return: the logger with specified name (with timestamp)
    """
    logger = logging.getLogger(nameForLogger + str(time.time()))
    logger.level = logging.INFO
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    mainPath = os.path.dirname(__main__.__file__)
    fileHandler = logging.FileHandler(
        os.path.join(mainPath, "logs", nameForLogger + ".log"))
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    return logger
