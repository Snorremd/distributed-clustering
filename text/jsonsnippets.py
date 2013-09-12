## Compact Trie Clustering
##  XML-handling of snippets
## Richard Moe
## 20.10.2010

## Parsing a snippet-collection using json
import json


def get_snippet_collection(filename):
    ''' Builds a list of snippet, source-tuples.
    Takes a XML snippet-file on the form:
    <snippet id="2009-12-07-aa-02"
     tags="Innenriks-kultur-aaretstroender-oppfordring-trondheim"
     source="http://www.adressa.no/tema/arets_tronder/article1419602.ece">
        <snip type="ArticleTitle"> Hvem burde troender</snip>
        <snip type="ArticleText"> sende forslag</snip>
    </snippet>
    and produce a list on the form:
    [("hvem burde troender", "http://www.adressa.no/tema/arets_tronder/article1419602.ece"), ("terms...", "source"), (..., ...)]
    '''
    snippetDict = {}
    sourceAndDocuments = get_documents_and_source(filename)
    documents = sourceAndDocuments["snippet"]

    ## Each document is a dictionary of key value pairs
    for document in documents:
        source = document["@source"]
        for key in document.keys():
            if not key.startswith("@"):  # Do not include attributes
                snippets = []
                if not document[key] is None:  # If text type is non-empty
                    for snippet in document[key]["snip"]:
                        snippets.append((snippet, [source]))
                if key not in snippetDict:
                    snippetDict[key] = snippets
                else:
                    snippetDict[key].extend(snippets)
    return snippetDict

    #for document in jsonTree.items:
    #    source = document.get("source")
    #    for textType in document:
    #        snippets = []
    #        for snippet in textType:
    #            snippets.append((snippet.text, [source]))
    #        snippetDict[textType] = snippets
    #return snippetDict

    ##tree = parse(filename, parser=P)
    #Snippets = []
    #for s in tree.findall("snippet"):
    #    for x in s.findall("snip"):
    #        Snippets.append((x.text, [s.get("source")], x.get("type")))
    #        ##Snippets.append((x.text.encode('latin-1'),[s.get("source")]))
    #return Snippets


def make_tag_index(filename):
    """
    Create a tag index based on corpus file
    :param filename: the json file to read
    :type filename: str
    :return: an index mapping sources to tags
    :rtype: dict
    """
    sourceAndDocuments = get_documents_and_source(filename)
    documents = sourceAndDocuments["snippet"]
    tagIndex = {}
    for document in documents:
        tagIndex[document["@source"]] = document["@tags"]
    return tagIndex


def make_groundtruth_clusters(filename):
    """
    Create ground truth clusters index
    :param filename: the json file to make ground truth clusters from
    :type filename: str
    :return: an index mapping tags to sources
    :rtype: dict
    """
    sourceAndDocuments = get_documents_and_source(filename)
    documents = sourceAndDocuments["snippet"]
    groundTruthIndex = {}
    for document in documents:
        tags = document["@tags"]
        if tags in groundTruthIndex:
            groundTruthIndex[tags].append(document["@source"])
        else:
            groundTruthIndex[tags] = [document["@source"]]
    return groundTruthIndex
    #for snippet in tree.findall("snippet"):
    #    tags = snippet.get("tags")
    #    if Index.has_key(tags):
    #        Index[tags].append(snippet.get("source"))
    #    else: Index[tags] = [snippet.get("source")]



def get_documents_and_source(filename):
    """
    Return the json data as a dict
    :param filename: the file to read
    :type filename: str
    :return: the json as dict
    :rtype: dict
    """
    jsonFile = open(filename)
    jsonTree = json.load(jsonFile)
    return jsonTree[jsonTree.keys()[0]]
