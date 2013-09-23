'''
Compact Trie Clustering
Slice-clustering

@author: Richard Moe
@version: 12.05.11
'''
from time import sleep
from cluster.compactTrie.compactTrie import phraseTree
from phrases import stringToPhrase
from xmlsnippets import get_snippet_collection
from math import floor, ceil
from guppy import hpy


 

def n_slices(n, phrase):  # assuming n =< len(phrase)
    '''
    Returns a list of all slices of n length generated
    from a list of phrases where each phrase is a list
    ''' 
    if not phrase:
        return []
    Slices = []
    p = phrase[:]  ## make a copy
    while len(p) >= n:  
        Slices.append(p[0:n])
        del p[0]  #p = p[1:]
    return Slices


## Range Slice Tries

def rangeSlices(min, max, phrase):
    Slices = []
    for n in range(min, max + 1):
        Slices = Slices + n_slices(n, phrase[:])
    return Slices


def n_slice_tree(n, strings):
    slices = []
    for (x, y) in strings:
        x = x[:]
        phrase = stringToPhrase(x)
        if n > len(phrase):
            n = len(x)
        for nSlices in n_slices(n, phrase):
            slices.append((nSlices, y))
    return phraseTree(slices)


def rangeSliceTree(strings, rangeMin=.5, rangeMax=.7):  # build slice tree from a list of string+source pairs
    Slices = []
    for (x, y) in strings:
        x = x[:]
        y = y[:]
        string = stringToPhrase(x)
        min = int(floor(len(string) * rangeMin))
        if min == 0:
            min = 1
        max = int(ceil(len(string) * rangeMax))
        for s in rangeSlices(min, max, string):
            Slices.append((s, y))
    sleep(4)
    totalLength = 0
    for slice in Slices:
        for snip in slice[0]:
            totalLength += len(snip)
    print "Total length: ", totalLength
    print "Number of suffixes: ", len(Slices)
    return phraseTree(Slices)


def makeRangeSliceTree(filename):  #read from an XML SnippetCollection
    return rangeSliceTree(get_snippet_collection(filename))




## mid Slice Tries
## midSlice-tries would holds significtly fewer words than suffix-tries

def midSlices(phrase):
    mid = int((len(phrase) + 1) / 2)  ## = (len(phrase)+1)//2?
    return n_slices(mid, phrase)


def midSliceTree(strings):
    ''' Build a mSlice tree from a list of string -> source pair.'''
    Slices = []
    for (string, source) in strings:
        string = string[:]
        phrase = stringToPhrase(string)
        for mSlice in midSlices(phrase): 
            Slices.append((mSlice, source))
    return phraseTree(Slices)


def makeMidSliceTree(filename):
    '''
    Make a midsliceTree from a collection of snippets.
    read from an XML SnippetCollection
    '''
    return midSliceTree(get_snippet_collection(filename))