## Compact Trie Clustering
##  XML-handling of snippets
## Richard Moe
## 20.10.2010

## Parsing a snippet-collection (XML) using Element Trees

#from xml.etree.ElementTree import *
from lxml.etree import *
##P = XMLParser(encoding='utf-8')
 
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
    tree = parse(filename)
    ##tree = parse(filename, parser=P)
    Snippets = []
    for s in tree.findall("snippet"):
        for x in s.findall("snip"):
            Snippets.append((x.text, [s.get("source")], x.get("type")))
            ##Snippets.append((x.text.encode('latin-1'),[s.get("source")]))
    return Snippets


def make_tag_index(filename):
    tree = parse(filename)
    Index = {}
    for s in tree.findall("snippet"):
        Index[s.get("source")] = s.get("tags")
    return Index


def make_groundtruth_clusters(filename):
    tree = parse(filename)
    Index = {}
    for snippet in tree.findall("snippet"):
        tags = snippet.get("tags")
        if Index.has_key(tags):
            Index[tags].append(snippet.get("source"))
        else: Index[tags] = [snippet.get("source")] 
    return Index
