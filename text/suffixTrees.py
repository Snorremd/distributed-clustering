##
##
##  Suffix Trees
##  Richard Moe
##  08.11.2010
##

from cluster.compactTrie.compactTrie import *
from phrases import *
from xmlsnippets import *

def suffixes(p):
    phrase = p[:]
    suffixlist = []
    while phrase:
        suffixlist.append(phrase[:])  #copy p to avoid mutilating side-effects
        del phrase[0]
    return suffixlist

    
def suffixTree(strings):  # build suffix tree from a list of string+source pairs
    suffs = []
    for (x, y) in strings:
        for s in suffixes(stringToPhrase(x)):
            suffs.append((s, y))
    totalLength = 0
    for slice in suffs:
        for snip in slice[0]:
            totalLength += len(snip)
    print "Total length: ", totalLength
    print "Number of suffixes: ", len(suffs)
    return phraseTree(suffs)



def makeSuffixTree(filename):  #read from an XML SnippetCollection
    return suffixTree(get_snippet_collection(filename))

