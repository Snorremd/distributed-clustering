## Tree types
import weakref
from easylogging.configLogger import get_logger_for_stdout
from text.phrases import get_common_start_segment
from text.sliceTrees import make_mid_slice_tree, make_n_slice_tree, make_range_slice_tree
from text.suffixTrees import make_suffix_tree

SUFFIX_TREE = 0
MID_SLICE = 1
RANGE_SLICE = 2
N_SLICE = 3

logger = get_logger_for_stdout("compactTrieModule")


def generate_compact_trie(snippetCollection, treeTypeTuple):
    """

    :param treeTypeTuple:
    :param snippetCollection:
    :return:
    """
    (treeType, sliceLengthRangeMin, rangeMax) = treeTypeTuple  # Expand tuple
    if treeType == SUFFIX_TREE:
        logger.info("Creating suffix tree")
        return build_compact_trie(make_suffix_tree(snippetCollection))
    elif treeType == MID_SLICE:
        logger.info("Creating mid slice tree")
        return build_compact_trie(make_mid_slice_tree(snippetCollection))
    elif treeType == RANGE_SLICE:
        logger.info("Creating slice tree for min {0} -> max {1}".format(
            treeTypeTuple[1], treeTypeTuple[2]))
        return build_compact_trie(make_range_slice_tree(snippetCollection,
                                                        treeTypeTuple[1],
                                                        treeTypeTuple[2]))
    elif treeType == N_SLICE:
        logger.info("Creating n-slice tree for n = {0}".format(
            treeTypeTuple[1]))
        return build_compact_trie(make_n_slice_tree(snippetCollection,
                                                    treeTypeTuple[1]))


def build_compact_trie(phrases):
    tree = CompactTrie()
    for phrase, sources in phrases:
        tree.insert(phrase, sources)
    return tree


class CompactTrie(object):
    """
    Models a compact trie data structure. It contains a root compact trie
    node that holds all other compact trie nodes as subtrees.
    """

    def __init__(self):
        self.root = CompactTrieNode()

    def insert(self, phrase, sources):
        """
        Insert a phrase, sources pair into the tree
        :type phrase: list
        :param phrase: the phrase to insert
        :type sources: list
        :param sources: the sources to bind to the phrase
        """
        self.root.insert(phrase, sources)


class CompactTrieNode(object):
    """
    Class modeling a node in the compact trie data structure. Each node has a
     reference to the parent node, as well as a phrase, a dict containing
     sources with count, and last but importantly a dictionary containing
     references to all the subtrees of the node.
    """

    def __init__(self):
        self.phrase = []
        self.parent = None
        self.sources = {}
        self.subtrees = {}

    def add_sources(self, sources):
        """
        Adds a list of sources to a node mapping them to the phrase of node.
        If source already exist in node, add to counter to keep track of how
        many times the phrase occurs in the given document.
        :type sources: list
        :param sources: to add to phrase in node
        """
        for source in sources:
            if not source in self.sources:
                self.sources[source] = 1
            else:
                self.sources[source] += 1

    def insert(self, phrase, sources):
        """
        Insert phrase into node
        :type phrase: list
        :param phrase: the (sub)phrase to insert
        :type sources: list
        :param sources: sources for phrase
        :return:
        """
        if not phrase:
            return None

        sources = sources[:]
        phrase = phrase[:]
        firstWord = phrase[0]

        if not firstWord in self.subtrees:
            self.insert_new_branch(firstWord, phrase, sources)
        else:  # first word of phrase exists in subtree
            self.insert_branch(firstWord, phrase, sources)

    def insert_new_branch(self, firstWord, phrase, sources):
        """
        Phrase does not exist in any branch of compact trie node,
        insert phrase as new branch.
        :param firstWord:
        :param phrase:
        :param sources:
        :return:
        """
        ## Branch does not exist, create new branch
        newBranchNode = CompactTrieNode()
        newBranchNode.phrase = phrase
        ## Avoid cyclic references by using weakref
        newBranchNode.parent = weakref.ref(self) if self else None
        newBranchNode.add_sources(sources)
        self.subtrees[firstWord] = newBranchNode

    def insert_branch(self, firstWord, phrase, sources):
        """
        Phrase (or subphrase) exist as subtree in compact trie node. If all
         of phrase exists in compact trie node subtree, add sources to
         respective node. If part of phrase exist in subtree, insert common
         start segment as new subtree, and process existing subtree.
        :param firstWord:
        :param phrase:
        :param sources:
        :return:
        """
        branchNode = self.subtrees[firstWord]
        if branchNode.phrase == phrase:  # Phrase exists in tree, add sources
            branchNode.add_sources(sources)
        else:  # Find common start segment of partially matching phrases
            self.insert_common_start_segment(branchNode, phrase, firstWord,
                                             sources)

    def insert_common_start_segment(self, branchNode, phrase,
                                    firstWord, sources):
        """
        Phrase shares common start segment with a subtree node in compact
         trie node. If there is no phrase rest, replace branch with a new node
         (common start segment) and make branch rest it's subtree. If there
         is no branch reset, insert rest of phrase into branch node. If there
         is both a phrase rest and a branch rest make a new node for common
         start segment, and make branch rest and phrase rest subtrees of the
         new start segment node.
        :param branchNode:
        :param phrase:
        :param firstWord:
        :param sources:
        :return:
        """
        (commonStartSegment, branchRest, phraseRest) = \
            get_common_start_segment(branchNode.phrase, phrase)
        if not phraseRest:
            self.insert_new_node(branchNode, branchRest, commonStartSegment,
                                 firstWord, sources)
        elif not branchRest:  # Recursively insert phrase rest into branch
            branchNode.insert(phraseRest, sources)
        else:  # There is a phrase rest and branch rest
            self.insert_common_start_segment_node(branchNode, branchRest,
                                                  commonStartSegment, firstWord,
                                                  phraseRest, sources)

    def insert_new_node(self, branchNode, branchRest, commonStartSegment,
                        firstWord, sources):
        """
        Branch rest should be inserted as subtree node of new common start
         segment node. Common Start Segment node should replace branchNode as
         subtree node of current node.
        :type branchNode: CompactTrieNode
        :param branchNode:
        :type branchRest: list
        :param branchRest:
        :type commonStartSegment: CompactTrieNode
        :param commonStartSegment:
        :type firstWord: str
        :param firstWord:
        :type sources: list
        :param sources:
        :return:
        """
        ## phrase rest is empty, insert new node
        newNode = CompactTrieNode()
        newNode.phrase = commonStartSegment
        newNode.parent = weakref.ref(self) if self else None
        newNode.add_sources(sources)
        ## Make branch a subtree of new node-tree
        newNode.subtrees = {branchRest[0]: branchNode}
        branchNode.phrase = branchRest
        branchNode.parent = weakref.ref(newNode) if newNode else None
        ## Make newnode child node of self
        self.subtrees[firstWord] = newNode

    def insert_common_start_segment_node(self, branchNode, branchRest,
                                         commonStartSegment, firstWord,
                                         phraseRest, sources):
        """
        There is both a branch rest and a phrase rest. Replace current branch
         node with common start segment as new subtree node of current compact
         trie node. Make branch rest and phrase rest subtree nodes of common
         start segment node.
        :type branchNode: CompactTrieNode
        :param branchNode:
        :type branchRest: list
        :param branchRest:
        :type commonStartSegment: list
        :param commonStartSegment:
        :type firstWord: str
        :param firstWord:
        :type phraseRest: list
        :param phraseRest:
        :type sources: list
        :param sources:
        :return:
        """
        ## Create a new trie for common start segment
        commonStartSegmentNode = CompactTrieNode()
        commonStartSegmentNode.phrase = commonStartSegment
        commonStartSegmentNode.parent = weakref.ref(self) if self else None
        commonStartSegmentNode.add_sources(sources)
        ## Create a compact trie for phrase rest
        phraseRestNode = CompactTrieNode()
        phraseRestNode.phrase = phraseRest
        phraseRestNode.parent = weakref.ref(commonStartSegmentNode) if \
            commonStartSegmentNode else None
        phraseRestNode.add_sources(sources)
        phraseRestNode.subtrees = {}
        ## Make branchrest and phrase rest children of common start
        ## segment node
        commonStartSegmentNode.subtrees = {
            branchRest[0]: branchNode,
            phraseRest[0]: phraseRestNode}
        ## Update branch trie and self (this node)
        branchNode.phrase = branchRest
        branchNode.parent = weakref.ref(commonStartSegmentNode) if \
            commonStartSegmentNode else None
        self.subtrees[firstWord] = commonStartSegmentNode
