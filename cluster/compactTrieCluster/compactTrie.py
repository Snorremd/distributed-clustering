## Tree types
from collections import OrderedDict
import weakref
from easylogging.configLogger import get_logger_for_stdout
from text.phrases import get_common_start_segment
from text.sliceTrees import make_mid_slice_tree, make_n_slice_tree, make_range_slice_tree
from text.suffixTrees import make_suffix_tree

## Constants for expansion techniques/tree types
SUFFIX_TREE = 0
MID_SLICE = 1
RANGE_SLICE = 2
N_SLICE = 3

logger = get_logger_for_stdout("compactTrieModule")


def generate_compact_trie(snippet_collection, tree_type_tuple):
    """
    Generate a compact trie over the snippet collection using the expansion
     technique given by tree_type_tuple.

    :type tree_type_tuple: tuple
    :param tree_type_tuple: tree type (expansion technique) to use for snippet expansion
    :type snippet_collection: list
    :param snippet_collection: list of snippet source pairs.

    :rtype: CompactTrie
    :return: compact trie generated from snippet collection
    """
    (tree_type, slice_length_range_min, range_max) = tree_type_tuple  # Expand tuple
    if tree_type == SUFFIX_TREE:
        logger.info("Creating suffix tree")
        return build_compact_trie(make_suffix_tree(snippet_collection))

    elif tree_type == MID_SLICE:
        logger.info("Creating mid slice tree")
        return build_compact_trie(make_mid_slice_tree(snippet_collection))

    elif tree_type == RANGE_SLICE:
        logger.info("Creating slice tree for min {0} -> max {1}".format(
            tree_type_tuple[1], tree_type_tuple[2]))
        return build_compact_trie(make_range_slice_tree(snippet_collection,
                                                        tree_type_tuple[1],
                                                        tree_type_tuple[2]))

    elif tree_type == N_SLICE:
        logger.info("Creating n-slice tree for n = {0}".format(
            tree_type_tuple[1]))
        return build_compact_trie(make_n_slice_tree(snippet_collection,
                                                    tree_type_tuple[1]))


def build_compact_trie(phrase_source_pairs):
    """
    Build a compact trie over a list of phrase source pairs expanded from the
     snippet source pairs from the snippet collection.

    :type phrase_source_pairs: list
    :param phrase_source_pairs: phrase source pairs to insert into compact trie structure

    :rtype: CompactTrie
    :return: compact trie built from phrase source pairs
    """
    tree = CompactTrie()
    for phrase, sources in phrase_source_pairs:
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
        self.sources = []
        self.sources_dict = {}
        self.subtrees = OrderedDict()

    def add_sources(self, sources):
        """
        Adds a list of sources to a node mapping them to the phrase of node.
        If source already exist in node, add to counter to keep track of how
        many times the phrase occurs in the given document.

        :type sources: list
        :param sources: to add to phrase in node
        """
        for source in sources:
            if not source in self.sources_dict:
                self.sources_dict[source] = 1
            else:
                self.sources_dict[source] += 1

            if source not in self.sources:
                self.sources.append(source)

    def generate_node_label(self):
        """
        Recursively generate a concatenated node label array of self and
        parents.
        """
        if self.parent is None:
            return self.phrase
        else:
            #noinspection PyCallingNonCallable
            return self.parent().generate_node_label() + self.phrase

    def insert(self, phrase, sources):
        """
        Insert phrase source pair into node

        :type phrase: list
        :param phrase: the (sub)phrase to insert
        :type sources: list
        :param sources: sources for phrase
        """
        if not phrase:
            return None

        sources = sources[:]
        phrase = phrase[:]
        first_word = phrase[0]

        if not first_word in self.subtrees:
            self.insert_new_branch(first_word, phrase, sources)
        else:  # first word of phrase exists in subtree
            self.insert_branch(first_word, phrase, sources)

    def insert_new_branch(self, first_word, phrase, sources):
        """
        Phrase does not exist in any branch of compact trie node,
        insert phrase as new branch.

        :type first_word: str
        :param first_word: of the phrase to insert
        :type phrase: list
        :param phrase: words to insert as new branch node
        :type sources: list
        :param sources: document to which phrase belong
        """
        ## Branch does not exist, create new branch
        new_branch_node = CompactTrieNode()
        new_branch_node.phrase = phrase
        ## Avoid cyclic references by using weakref
        new_branch_node.parent = weakref.ref(self) if self else None
        new_branch_node.add_sources(sources)
        self.subtrees[first_word] = new_branch_node

    def insert_branch(self, first_word, phrase, sources):
        """
        Phrase (or sub-phrase) exist as subtree in compact trie node. If all
         of phrase exists in compact trie node subtree, add sources to
         respective node. If part of phrase exist in subtree, insert common
         start segment as new subtree, and process existing subtree.

        :type first_word: str
        :param first_word: of the phrase to insert
        :type phrase: list
        :param phrase: words to insert as new branch node
        :type sources: list
        :param sources: document to which phrase belong
        """
        branch_node = self.subtrees[first_word]
        if branch_node.phrase == phrase:  # Phrase exists in tree, add sources
            branch_node.add_sources(sources)
        else:  # Find common start segment of partially matching phrases
            self.insert_common_start_segment(branch_node, phrase, first_word,
                                             sources)

    def insert_common_start_segment(self, branch_node, phrase,
                                    first_word, sources):
        """
        Phrase shares common start segment with a subtree node in compact
         trie node. If there is no phrase rest, replace branch with a new node
         (common start segment) and make branch rest it's subtree. If there
         is no branch reset, insert rest of phrase into branch node. If there
         is both a phrase rest and a branch rest make a new node for common
         start segment, and make branch rest and phrase rest subtrees of the
         new start segment node.

        :type branch_node: CompactTrieNode
        :param branch_node: the branch node to add phrase to
        :type first_word: str
        :param first_word: of the phrase to insert
        :type phrase: list
        :param phrase: words to insert as new branch node
        :type sources: list
        :param sources: document to which phrase belong
        """
        (common_start_segment, branch_rest, phrase_rest) = \
            get_common_start_segment(branch_node.phrase, phrase)
        if not phrase_rest:
            self.insert_new_node(branch_node, branch_rest, common_start_segment,
                                 first_word, sources)
        elif not branch_rest:  # Recursively insert phrase rest into branch
            branch_node.insert(phrase_rest, sources)
        else:  # There is a phrase rest and branch rest
            self.insert_common_start_segment_node(branch_node, branch_rest,
                                                  common_start_segment, first_word,
                                                  phrase_rest, sources)

    def insert_new_node(self, branch_node, branch_rest, common_start_segment,
                        first_word, sources):
        """
        Branch rest should be inserted as subtree node of new common start
         segment node. Common Start Segment node should replace branchNode as
         subtree node of current node.

        :type branch_node: CompactTrieNode
        :param branch_node: branch node to make a new child node of a new node
        :type branch_rest: list
        :param branch_rest: the end of branch node's phrase
        :type common_start_segment: list
        :param common_start_segment: the word common to phrase and branch
        :type first_word: str
        :param first_word: of the phrase to insert
        :type sources: list
        :param sources: document to which phrase belong
        """
        ## phrase rest is empty, insert new node
        new_node = CompactTrieNode()
        new_node.phrase = common_start_segment
        new_node.parent = weakref.ref(self) if self else None
        new_node.add_sources(sources)
        ## Make branch a subtree of new node-tree
        new_node.subtrees = OrderedDict({branch_rest[0]: branch_node})
        branch_node.phrase = branch_rest
        branch_node.parent = weakref.ref(new_node) if new_node else None
        ## Make new_node child node of self
        self.subtrees[first_word] = new_node

    def insert_common_start_segment_node(self, branch_node, branch_rest,
                                         common_start_segment, first_word,
                                         phrase_rest, sources):
        """
        There is both a branch rest and a phrase rest. Replace current branch
         node with common start segment as new subtree node of current compact
         trie node. Make branch rest and phrase rest subtree nodes of common
         start segment node.

        :type branch_node: CompactTrieNode
        :param branch_node: branch node to make child node of common start segment node
        :type branch_rest: list
        :param branch_rest: the end of branch node's phrase unique to branch phrase
        :type common_start_segment: list
        :param common_start_segment: the words common to branch node's phrase and phrase to insert
        :type first_word: str
        :param first_word: the first word of phrase
        :type phrase_rest: list
        :param phrase_rest: the end words of phrase unique to phrase
        :type sources: list
        :param sources: to insert into common start segment node
        """
        ## Create a new trie for common start segment
        common_start_segment_node = CompactTrieNode()
        common_start_segment_node.phrase = common_start_segment
        common_start_segment_node.parent = weakref.ref(self) if self else None
        common_start_segment_node.add_sources(sources)
        ## Create a compact trie for phrase rest
        phrase_rest_node = CompactTrieNode()
        phrase_rest_node.phrase = phrase_rest
        phrase_rest_node.parent = weakref.ref(common_start_segment_node) if \
            common_start_segment_node else None
        phrase_rest_node.add_sources(sources)
        phrase_rest_node.subtrees = OrderedDict()
        ## Make branch rest and phrase rest children of common start
        ## segment node
        common_start_segment_node.subtrees = OrderedDict({
            branch_rest[0]: branch_node,
            phrase_rest[0]: phrase_rest_node})
        ## Update branch trie and self (this node)
        branch_node.phrase = branch_rest
        branch_node.parent = weakref.ref(common_start_segment_node) if \
            common_start_segment_node else None
        self.subtrees[first_word] = common_start_segment_node
