##
##
##  Suffix Trees
##  Richard Moe
##  08.11.2010
##

from cluster.compactTrie.compactTrie import *
from phrases import *
from xmlsnippets import *

def suffixes(phrase):
    p = phrase
    suffixlist = []
    while p != []:
        suffixlist.append(p[:])  #copy p to avoid mutilating side-effects
        del p[0]
    return suffixlist

    
def suffixTree(strings):  # build suffix tree from a list of string+source pairs
    suffs = []
    for (x, y) in strings:
        for s in suffixes(stringToPhrase(x)):
            suffs.append((s, y))
    return phraseTree(suffs)



def makeSuffixTree(filename):  #read from an XML SnippetCollection
    return suffixTree(get_snippet_collection(filename))

