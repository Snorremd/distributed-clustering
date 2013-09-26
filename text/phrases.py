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