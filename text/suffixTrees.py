import gc
from text.phrases import string_to_phrase


def make_suffix_tree(snippetCollection):
    suffixes = []
    for snippet, source in snippetCollection:
        phrase = string_to_phrase(snippet)
        for suffix in make_suffixes(phrase):
            suffixes.append((suffix, source))
    return suffixes


def make_suffixes(snippet):
    """

    :type snippet": list
    :param snippet: to expand into suffixes
    :rtype: list
    :return: list of suffixes expanded from snippet
    """
    phrase = snippet[:]
    suffixList = list()

    while phrase:
        suffixList.append(phrase[:])
        del phrase[0]
    return suffixList