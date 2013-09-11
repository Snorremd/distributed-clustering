#
#  Compact Trie 
#
#  Richard E. Moe
#  11.05.2011


from text.phrases import emptyphrase, firstword, getCommonStartSegment
from guppy import hpy
heapy = hpy()

class CompactTrie:
    '''
    A class that models a compact trie.
    '''
    # phrase = []     list of words
    # parent = None   reference to CompactTrie-node
    # sources = []    list of document names
    # subtrees = {}   dictionary of firstword:CompactTrie pairs

    def __init__(self):
        '''
        Constructor for CompactTrie.
        '''
        self.phrase = []
        self.parent = None
        self.sources = {}
        self.subtrees = {}

    def nodelabel(self):
        '''Returns the concatenated nodelabel array of self and parent'''
        if self.parent == None: return self.phrase
        else: return self.parent.nodelabel() + self.phrase

    def display(self): printCTindent(self, 0)

    def addSources(self, sourceDictionary):
        for x in sourceDictionary:
            if not x in self.sources:
                self.sources[x] = 1
            else:
                self.sources[x] = self.sources[x] + 1

    def insert(self, Phrase, Sources):
        '''
        Insert a phrase/source-pair into the compact trie structure.
        If phrases is empty, the method terminates.
        '''
        if Phrase == []: return None  ## do nothing on empty phrase
        sources = Sources[:]  #make copies of the parameters
        phrase = Phrase[:]  #(perhaps not necessary for Phrase?)
        first = firstword(phrase)
        if not self.subtrees.has_key(first):
            ## Branch does not exist, create a new branch
            newBranch = CompactTrie()
            newBranch.phrase = phrase
            newBranch.parent = self
            newBranch.addSources(sources)
            newBranch.subtrees = {}
            self.subtrees[first] = newBranch
        else:
            ## Branch exist (a subtree with first word in phrase found)
            branch = self.subtrees[first]
            if branch.phrase == phrase:
                ## If phrase equals branch phrase, no new branches should be added
                branch.addSources(sources)
            else:
                ## branch has different phrase. Find common start segment (sub-phrase)
                (commonStartSegment, branchRest, phraseRest) = getCommonStartSegment(branch.phrase, phrase)
                if phraseRest == []:
                    ## If phrase "rest" is empty, make new compact trie
                    newNode = CompactTrie()
                    newNode.phrase = commonStartSegment
                    newNode.parent = self
                    newNode.addSources(sources)
                    newNode.subtrees = {firstword(branchRest):branch}  # Make branch a subtree of newNode
                    branch.phrase = branchRest
                    branch.parent = newNode  # Make newNode a parent of branch
                    self.subtrees[first] = newNode  # Make newNode a subtree of self (this trie)"
                elif branchRest == []:
                    branch.insert(phraseRest, sources)  # Insert rest of phrase into branch (recursivly)
                else:  # phraseRest and branchRest are nonempty and start with different words
                    ## First create a new trie for the common start segment
                    commonStartSegmentNode = CompactTrie()
                    commonStartSegmentNode.phrase = commonStartSegment
                    commonStartSegmentNode.parent = self
                    commonStartSegmentNode.addSources(sources)
                    ## Then create a new compact trie for the rest of the phrase
                    phraseRestNode = CompactTrie()
                    phraseRestNode.phrase = phraseRest
                    phraseRestNode.parent = commonStartSegmentNode
                    phraseRestNode.addSources(sources)
                    phraseRestNode.subtrees = {}
                    ## Make branchRest and phraseRest children of the commonStartSegment trie
                    commonStartSegmentNode.subtrees = {firstword(branchRest):branch,
                                        firstword(phraseRest):phraseRestNode}

                    ## Update branch trie and self (this object)
                    branch.phrase = branchRest
                    branch.parent = commonStartSegmentNode
                    self.subtrees[first] = commonStartSegmentNode




#Build a compact trie for a list of phrase+source pairs

def phraseTree(phrases):
    '''
    Builds a compact trie from a list of phrase source-pairs.
    '''
    tree = CompactTrie()
    for (p, s) in phrases:
        tree.insert(p, s)
    print "MEMORY USAGE PHRASETREE"
    print heapy.heap()
    return tree



###################
## auxillilaries ## 
###################
def printCTindent(ct, indent):  ## prints a compact trie ct with indentation
    i = 0
    dots = ""
    while i < indent:
        dots = dots + "...."
        i = i + 1
    print dots,
    print ct.phrase,
    print ": ",
    print ct.sources
    #print " (",
    #print ct.nodelabel(),
    #print ") "
    #print "\n"
    for s in ct.subtrees.values(): printCTindent(s, indent + 1)
