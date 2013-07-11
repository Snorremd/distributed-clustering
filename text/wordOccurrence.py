##
##  Compact Trie clustering
##    word frequencies in compact tries
##  Richard Moe
##  05.05.11
##

#from cluster.compactTrie.compactTrie import CompactTrie  # CompactTrie, nodelabel

def mergeDictionaries(D1, D2):
    for phrase in D2.keys():
        if D1.has_key(phrase):
            for sourceDictKey in D2[phrase]:
                if not sourceDictKey in D1[phrase]:
                    D1[phrase][sourceDictKey] = D2[phrase][sourceDictKey]
        else: D1[phrase] = D2[phrase]
    return D1

def collectSources(compactTrie):
    sourceDictionary = compactTrie.sources.copy()
    ## L = compactTrie.sources[:]
    for s in compactTrie.subtrees.values():
        for x in s.sources:
            if not x in sourceDictionary:
                sourceDictionary[x] = s.sources[x]
    return sourceDictionary
    

def getWordSources(compactTrie):

    wordDict = {}
                    
    for w in compactTrie.phrase:
        wordDict[w] = compactTrie.sources.copy()
        
    for s in compactTrie.subtrees.values():
        sources = collectSources(s)
        for x in sources:
            for w in compactTrie.phrase:
                if not x in wordDict[w]:
                    wordSources = wordDict[w]
                    wordSources[x] = sources[x]
        mergeDictionaries(wordDict, getWordSources(s))
      
    return wordDict



def countSources(compactTrie):
    return len(collectSources(compactTrie))


    
    
