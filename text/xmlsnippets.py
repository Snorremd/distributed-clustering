from xml.etree.ElementTree import iterparse, parse


def get_snippet_collection(snippetFilePath):
    """
    :type snippetFilePath: str
    :param snippetFilePath: path to snippet file
    :rtype: dict
    :return: a dict on the form {"texttype" -> [("snippet", ["source"]),
    ...], ...}
    """
    ##tree = parse(filename)
    snippetDict = {}
    ## documents = tree.findall("snippet")
    for event, element in iterparse(snippetFilePath):
        if event == 'end':
            if element.tag == 'snippet':
                source = element.get("source")
                for textType in element:
                    snippets = []
                    for snippet in textType:
                        snippets.append((snippet.text[:], [source]))
                    if not textType.tag in snippetDict:
                        snippetDict[textType.tag] = snippets
                    else:
                        snippetDict[textType.tag].extend(snippets)
                element.clear()
    return snippetDict


def make_tag_index(snippetFilePath):
    """

    :type snippetFilePath: str
    :param snippetFilePath: path to snippet file
    :rtype: dict
    :return; a dict on the form {source: ["tag1-tag2-tag3"], ...}
    """
    tagIndex = {}
    for event, element in iterparse(snippetFilePath):
        if event == 'end':
            if element.tag == 'snippet':
                tagIndex[element.get("source")] = element.get("tags")
        element.clear()
    return tagIndex


def make_ground_truth_clusters(snippetFilePath):
    """

    :type snippetFilePath: str
    :param snippetFilePath:
    :return: groundTruthIndex on the form {"tag1-tag2-...-tag5": ["source1",
    "source2", "...", "sourcex"], ...}
    """
    groundTruthIndex = {}
    for event, element in iterparse(snippetFilePath):
        if event == "end":
            if element.tag == "snippet":
                tags = element.get("tags")
                if tags in groundTruthIndex:
                    groundTruthIndex[tags].append(element.get("source"))
                else:
                    groundTruthIndex[tags] = [element.get("source")]
            element.clear()
    return groundTruthIndex