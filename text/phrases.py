def string_to_phrase(phraseString):
    """
    :type phraseString: str
    :param phraseString: sentence/phrase to convert into list of words
    :rtype: list
    :return: a list of words in phrase
    """
    ## Empty strings equals empty phrase list
    if len(phraseString) == 0 or phraseString.isspace():
        return []
    ## Strip spaces to avoid empty list elements and get all words
    phraseString = phraseString.strip()
    return phraseString.split()


def phrase_to_string(phrase):
    """
    :type phrase: list
    :param phrase: the list of terms to convert
    :rtype: str
    :return: the concatenated string
    """
    return " ".join(phrase)


def get_common_start_segment(phrase1, phrase2):
    """
    :type phrase1: list
    :param phrase1: first phrase
    :type phrase2: list
    :param phrase2: second phrase
    :rtype: tuple
    :return: common start segment, phrase1 rest, phrase2 rest
    """
    commonStartSegment = []
    p1 = phrase1[:]
    p2 = phrase2[:]
    for term in phrase1:
        if not p1 or not p2:
            break
        elif term == p2[0]:
            commonStartSegment.append(term)
            del p1[0]
            del p2[0]
        else:
            break
    return commonStartSegment, p1, p2