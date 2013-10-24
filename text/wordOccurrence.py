from math import log
from text.phrases import string_to_phrase


def count_sources(compactTrie):
    """
    :type compactTrie: CompactTrieNode
    :param compactTrie: compact trie node to count sources in
    :rtype: int
    :return: number of sources
    """
    return len(collect_sources(compactTrie))


def collect_sources(compactTrie):
    """

    :type compactTrie: CompactTrieNode
    :param compactTrie: compact trie node to collect sources from
    :return: source dictionary
    """
    sources = compactTrie.sources.copy()

    for subtree in compactTrie.subtrees.values():
        for source in subtree.sources.copy():
            if not source in sources:
                sources.append(source)
    return sources


def get_word_sources(compactTrie):
    """

    :type compactTrie: CompactTrieNode
    :param compactTrie: compact trie node to collect word sources from
    :return:
    """
    word_dict = {}

    for word in compactTrie.phrase:
        word_dict[word] = compactTrie.sources[:]

    for subtree in compactTrie.subtrees.values():
        sources = collect_sources(subtree)
        for source in sources:
            for word in compactTrie.phrase:
                if not source in word_dict[word]:
                    word_dict[word].append(source)
        merge_dictionaries(word_dict, get_word_sources(subtree))

    return word_dict


def merge_dictionaries(dict1, dict2):
    """
    Takes two dictionaries; dict 1, and dict 2, and merges dict 2 into dict 1
    . Each dictionary contains phrases as keys where each phrase maps to a list
    of sources. Dict 2 is merged into dict 1 by including all sources from dict
    2 into dict 1.

    :type dict1: dict
    :param dict1: first dict of phrase -> source list pairs
    :type dict2: dict
    :param dict2: second dict of phrase -> source list pairs to merge into dict1
    :return: the merged dictionary
    """
    for phrase in dict2.keys():
        if phrase in dict1:
            for source in dict2[phrase]:
                if not source in dict1[phrase]:
                    dict1[phrase].append(source)
        else:
            dict1[phrase] = dict2[phrase]
    return dict1


def get_word_frequencies(snippet_collection, corpus_size):
    """
    Original author: Richard Elling Moe
    """
    corpus_frequency = dict()
    raw_frequency = dict()
    document_frequency = dict()
    for (snippet_type, snippets) in snippet_collection.items():
        for (snippet, [source]) in snippets:
            word_list = string_to_phrase(snippet)

            for word in word_list:
                ## CORPUS FREQUENCY
                if word in corpus_frequency:
                    corpus_frequency[word] += 1
                else:
                    corpus_frequency[word] = 1

                ## RAW FREQUENCY
                if word in raw_frequency:
                    if source in raw_frequency[word]:
                        raw_frequency[word][source] += 1
                    else:
                        raw_frequency[word][source] = 1
                else:
                    raw_frequency[word] = {source: 1}

                ## DOCUMENT FREQUENCY
                if word in document_frequency:
                    if source not in document_frequency[word]:
                        document_frequency[word].append(source)
                else:
                    document_frequency[word] = [source]

    #most_frequent = []
    #for (word, frequency) in corpus_frequency.items():
    #    if frequency > 100:
    #        most_frequent.append((word, frequency))
    #
    #print("Most frequent word is {0} with frequency {1}".format(most_frequent[0], most_frequent[1]))

    return corpus_frequency, raw_frequency, document_frequency