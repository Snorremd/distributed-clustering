from collections import OrderedDict
from xml.etree.ElementTree import iterparse


def get_snippet_collection(snippetFilePath):
    """
    :type snippetFilePath: str
    :param snippetFilePath: path to snippet file
    :rtype: dict
    :return: a dict on the form {"texttype" -> [("snippet", ["source"]),
    ...], ...}
    """
    ##tree = parse(filename)
    snippetDict = OrderedDict()
    no_of_documnets = 0
    for event, element in iterparse(snippetFilePath):
        if event == 'end':
            if element.tag == 'snippet':
                no_of_documnets += 1
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
                del element
                del event
    return snippetDict, no_of_documnets


def make_tag_index(snippetFilePath):
    """

    :type snippetFilePath: str
    :param snippetFilePath: path to snippet file
    :rtype: dict
    :return; a dict on the form {source: ["tag1-tag2-tag3"], ...}
    """
    tagIndex = dict()
    for event, element in iterparse(snippetFilePath):
        if event == 'end':
            if element.tag == 'snippet':
                tagIndex[element.get("source")] = element.get("tags")
        element.clear()
        del element
        del event
    return tagIndex


def make_ground_truth_clusters(snippetFilePath):
    """

    :type snippetFilePath: str
    :param snippetFilePath:
    :return: groundTruthIndex on the form {"tag1-tag2-...-tag5": ["source1",
    "source2", "...", "sourcex"], ...}
    """
    groundTruthIndex = dict()
    for event, element in iterparse(snippetFilePath):
        if event == "end":
            tag = element.tag
            if tag == "snippet":
                tags = element.get("tags")
                if tags in groundTruthIndex:
                    groundTruthIndex[tags].append(element.get("source")[:])
                else:
                    source = element.get("source")
                    groundTruthIndex[tags] = [source]
            element.clear()
            del element
            del event
    return groundTruthIndex