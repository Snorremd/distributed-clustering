

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
        word_dict[word] = compactTrie.sources.copy()

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
                    dict1[phrase].append(dict2[phrase])
        else:
            dict1[phrase] = dict2[phrase]
    return dict1