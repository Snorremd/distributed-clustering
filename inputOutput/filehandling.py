__author__ = 'Snorre Magnus Davøen'

import sys
import os
import ntpath


def get_root_path():
    return os.path.dirname(sys.modules['__main__'].__file__)


def sep_file_and_path(path):

    """Handle paths with ending slash
    :type path: str
    :param path: the path to separate
    :return: filename and path tuple
    :rtype: tuple
    """
    head, tail = ntpath.split(path)
    return head, tail or ntpath.split(head)
