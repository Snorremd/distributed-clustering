from math import floor, ceil
from text.phrases import string_to_phrase


def make_mid_slice_tree(snippetCollection):
    """

    :type snippetCollection: list
    :param snippetCollection: to extract slices from
    :return:
    """
    slices = []
    for snippet, source in snippetCollection:
        phrase = string_to_phrase(snippet)
        for midSlice in extract_mid_slices(phrase):
            slices.append((midSlice, source))
    return slices


def make_n_slice_tree(snippetCollection, n):
    """

    :param snippetCollection:
    :return:
    """
    slices = []
    for snippet, source in snippetCollection:
        phrase = string_to_phrase(snippet)
        if n > len(phrase):
            n = len(phrase)
        for slice in extract_n_slices(phrase, n):
            slices.append((slice, source))
    return slices


def make_range_slice_tree(snippetCollection, rangeMin=.5, rangeMax=.6):
    """

    :type snippetCollection: list
    :param snippetCollection: to extract slices from
    :param rangeMin:
    :param rangeMax:
    :return:
    """
    slices = []
    for snippet, source in snippetCollection:
        phrase = string_to_phrase(snippet)

        ## Find min and max in ranges
        min = int(floor(len(phrase) * rangeMin))
        if min == 0:
            min = 1
        max = int(ceil(len(phrase) * rangeMax))

        for slice in extract_range_slices(phrase, min, max):
            slices.append((slice, source))
    return slices



def extract_mid_slices(phrase):
    """
    :type phrase: list
    :param phrase: to extract slices from
    :rtype: list
    :return: list of suffixes expanded from snippet
    """
    mid = int((len(phrase) + 1) / 2)
    return extract_n_slices(phrase, mid)


def extract_n_slices(phrase, n):
    """

    :param phrase:
    :type n: int
    :param n: size of slices, assumed n <= len(phrase)
    :rtype: list
    :return: list of suffixes expanded from snippet
    """
    if not phrase:
        return []
    slices = []
    slice = phrase[:]
    while len(slice) >= n:
        slices.append(slice[:n])
        del slice[0]
    return slices


def extract_range_slices(phrase, min, max):
    """
    :type phrase: list
    :param phrase: to extract range slices from
    :type min: int
    :param min: lower bound
    :type max: int
    :param max: upper bound
    :rtype: list
    :return: list of suffixes expanded from snippet
    """
    slices = []
    for n in range(min, max + 1):
        slices = slices + extract_n_slices(phrase, n)
    return slices