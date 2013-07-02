__author__ = 'snorre'

import sys
import os
import ntpath


def get_root_path():
    return os.path.dirname(sys.modules['__main__'].__file__)


def sep_file_and_path(path):

    """Handle paths with ending slash
    :return: filename and path tuple
    :rtype: tuple
    """
    head, tail = ntpath.split(path)
    return head, tail or ntpath.split(head)
