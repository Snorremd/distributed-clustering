#
#  Compact Trie
#
#  Richard E. Moe
#  11.05.2011
from time import sleep
import gc
import weakref
from easylogging import configLogger

from text.phrases import firstword, getCommonStartSegment

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
        if self.parent is None:
            return self.phrase
        else:
            return self.parent().nodelabel() + self.phrase

    def display(self):
        printCTindent(self, 0)

    def addSources(self, sourceDictionary):
        for x in sourceDictionary:
            if not x in self.sources:
                self.sources[x] = 1
            else:
                self.sources[x] += 1

    def insert(self, Phrase, Sources):
        '''
        Insert a phrase/source-pair into the compact trie structure.
        If phrases is empty, the method terminates.
        '''
        if not Phrase:
            return None  ## do nothing on empty phrase
        sources = Sources[:]  #make copies of the parameters
        phrase = Phrase[:]  #(perhaps not necessary for Phrase?)
        first = firstword(phrase)
        if not first in self.subtrees:
            ## Branch does not exist, create a new branch
            newBranch = CompactTrie()
            newBranch.phrase = phrase
            newBranch.parent = weakref.ref(self) if self else None
            newBranch.addSources(sources)
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
                if not phraseRest:
                    ## If phrase "rest" is empty, make new compact trie
                    newNode = CompactTrie()
                    newNode.phrase = commonStartSegment
                    newNode.parent = weakref.ref(self)  if self else None
                    newNode.addSources(sources)
                    newNode.subtrees = {firstword(branchRest):branch}  # Make branch a subtree of newNode
                    branch.phrase = branchRest
                    branch.parent = weakref.ref(newNode) if newNode else None
                     # Make newNode a
                    # parent of branch
                    self.subtrees[first] = newNode  # Make newNode a subtree of self (this trie)"
                elif not branchRest:
                    branch.insert(phraseRest, sources)  # Insert rest of phrase into branch (recursivly)
                else:  # phraseRest and branchRest are nonempty and start with different words
                    ## First create a new trie for the common start segment
                    commonStartSegmentNode = CompactTrie()
                    commonStartSegmentNode.phrase = commonStartSegment
                    commonStartSegmentNode.parent = weakref.ref(self) if self else None
                    commonStartSegmentNode.addSources(sources)
                    ## Then create a new compact trie for the rest of the phrase
                    phraseRestNode = CompactTrie()
                    phraseRestNode.phrase = phraseRest
                    phraseRestNode.parent = weakref.ref(
                        commonStartSegmentNode) if commonStartSegmentNode \
                        else None
                    phraseRestNode.addSources(sources)
                    phraseRestNode.subtrees = {}
                    ## Make branchRest and phraseRest children of the commonStartSegment trie
                    commonStartSegmentNode.subtrees = {firstword(branchRest):branch,
                                        firstword(phraseRest):phraseRestNode}

                    ## Update branch trie and self (this object)
                    branch.phrase = branchRest
                    branch.parent = weakref.ref(commonStartSegmentNode) if \
                        commonStartSegmentNode else None
                    self.subtrees[first] = commonStartSegmentNode




#Build a compact trie for a list of phrase+source pairs

def phraseTree(phrases):
    '''
    Builds a compact trie from a list of phrase source-pairs.
    '''
    logger = configLogger.getLoggerForStdOut("compactTrie")
    logger.debug("Building Phrase tree")
    tree = CompactTrie()
    for (p, s) in phrases:
        tree.insert(p, s)
        del p
        del s

    logger.debug("Finished building phrase tree")
    return tree



###################
## auxillilaries ##
###################
def printCTindent(ct, indent):  ## prints a compact trie ct with indentation
    i = 0
    dots = ""
    while i < indent:
        dots += "...."
        i += 1
    print dots,
    print ct.phrase,
    print ": ",
    print ct.sources
    #print " (",
    #print ct.nodelabel(),
    #print ") "
    #print "\n"
    for s in ct.subtrees.values():
        printCTindent(s, indent + 1)
