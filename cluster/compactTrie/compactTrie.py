## Tree types
from text.suffixTrees import make_suffix_tree

SUFFIX_TREE = 0
MID_SLICE = 1
RANGE_SLICE = 2
N_SLICE = 3

def generate_compact_trie(snippetCollection, treeTypeTuple):
    """

    :param treeTypeTuple:
    :param snippetCollection:
    :return:
    """
    (treeType, sliceLengthRangeMin, rangeMax) = treeTypeTuple  # Expand tuple
    if treeType == SUFFIX_TREE:
        return make_suffix_tree(snippetCollection)
    elif treeType == MID_SLICE:
        return make_mid_slice_tree(snippetCollection)
    elif treeType == RANGE_SLICE:
        pass
    elif treeType == N_SLICE:
        pass