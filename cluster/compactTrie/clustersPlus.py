##
##  Compact Trie clustering
##  - with various data added to clusters
##  Richard Moe
##  01.03.2012
##

# Given a Compact Trie of (sub-)phrases, in the form of lists of words,
# where each node representing a phrase initially inserted into the trie also
# has a list of sources where the phrase can be found.
# In such a trie, each node gives rise to a basecluster consisting of
# - a label made by concatenation of its phrase and the phrases of its ancestors.
# - the union of its sources and the sources of its subtrees

from compactTrie import CompactTrie  # CompactTrie, nodelabel
from text.phrases import phraseToString
from text.wordOccurrence import *
from time import time
import math


class basecluster:
    def __init__(self):
        self.label = ""
        self.sources = {}
        self.size = 0.0

    def addSources(self, sourceDictionary):
        for x in sourceDictionary:
            if not x in self.sources:
                self.sources[x] = sourceDictionary[x]  # append(x)
                self.size = self.size + 1.0

    def display(self):
         print self.label,
         print " : ",
         print self.sources

class component:
    def __init__(self):
        self.baseclusters = []
        self.next = None
        self.previous = None

    def delete(self):  ## assume first component never deleted.
        if self.previous != None:
            self.previous.next = self.next
            
        if self.next != None:
            self.next.previous = self.previous
## delete merely cuts out of the pointer-list, the object is not
## reclaimed  (worry about garbage-collection???)
        

class cluster:
    def __init__(self):
        self.label = []  # label for the cluster as a whole ?
        self.labels = []
        self.sources = {}
        self.numberOfSources = 0  #increment rather than post-merge-count
        self.wordFrequency = {}  #word frequency in the cluster
        self.numberOfWords = 0  #increment rather than post-merge-count?
        self.sourceOverlap = []  #shared-by-all sources
        self.labelOverlap = []  #shared-by-all words

    def addSources(self, sourceDict):
        for x in sourceDict:
            if not x in self.sources:
                self.sources[x] = sourceDict[x]  # .append(x)
                self.numberOfSources = self.numberOfSources + 1
        
   
    def collectWords(self, labelList):
        for x in labelList:
            if self.wordFrequency.has_key(x):
                self.wordFrequency[x] = self.wordFrequency[x] + 1
            else:
                self.wordFrequency[x] = 1
                self.numberOfWords = self.numberOfWords + 1

            
    def makeLabel(self):  # make label for the cluster as a whole:
        L = []
        #for x in self.wordFrequency.keys(): L.append((self.wordFrequency[x],x))
        for (x, y) in self.wordFrequency.items(): L.append((y, x))
        L.sort(reverse=True)
        for (x, y) in L: self.label.append(y)
## The label is (somewhat arbitrary) the list of words occurring in labels, 
## ordered by frequency.  Change to score-labels cf paper??
        
        
              
    def display(self):
        print "<", phraseToString(self.label), ">"
        print "labels:",
        for x in self.labels: print phraseToString(x), "|",
        print "\nsources:", self.sources  #, "(", self.numberOfSources, ")"
        print "label overlap:",
        for x in self.labelOverlap: print x + ", ",
        print "\nsource overlap: ", self.sourceOverlap
        #print self.wordFrequency, "(", self.numberOfWords, ")"
        print "\n"

 


#####################
### base clusters ###
#####################

def generateBaseClusters(Tree):
    baseClusters = []
    for subtree in Tree.subtrees.values():
        new = basecluster()
        new.label = subtree.nodelabel()
        new.addSources(subtree.sources)  # = subtree.sources[:]
        new.size = float(len(new.sources))
        bc = generateBaseClusters(subtree)
        for clusters in bc:
            new.addSources(clusters.sources)
            baseClusters.append(clusters)
        baseClusters.append(new)
    return baseClusters



def similarJaccard(BaseCluster1, BaseCluster2, jaccardLimit=0.5):
    '''
    Similarity measure based on the Jaccard coefficient.
    If both base clusters have a source overlap of >0.5
    they are regarded similar enough for inclusion in
    a component graph (final cluster).
    '''
    common = []
    for x in BaseCluster1.sources:
        if x in BaseCluster2.sources:
            common.append(x)
    sizeOverlap = float(len(common))
    return (sizeOverlap / BaseCluster1.size > jaccardLimit and
             sizeOverlap / BaseCluster2.size > jaccardLimit)

def similarCosineSim(BaseCluster1, BaseCluster2, cosineSimLimit=0.5):
    '''
    Similarity measure based on the cosine distance
    formula. If the cosine distance of BaseCluster1
    to BaseCluster2 is > 0.5, they are included in
    the component graph. 
    '''
    
    def calcWeights():
        '''
        A method that calculates the weight of a node for
        each document in that node. Algorithm derived from
        http://ieeexplore.ieee.org/lpdocs/epic03/wrapper.htm?arnumber=4459328
        '''
        documentFrequency1 = len(BaseCluster1.sources)  # Document frequency equal to no of sources in node
        documentFrequency2 = len(BaseCluster2.sources)
        commonSources = dict(BaseCluster1.sources.items() + BaseCluster2.sources.items())  ## Ignore value overwrites
        for source in commonSources:
            tfidf1 = 0.0
            tfidf2 = 0.0
            
            if source in BaseCluster1.sources:    
                termFrequency = BaseCluster1.sources[source]
                tfidf1 = (1 + math.log(termFrequency)) * math.log(1 + 6223 / documentFrequency1)
            if source in BaseCluster2.sources:    
                termFrequency = BaseCluster2.sources[source]
                tfidf2 = (termFrequency) * math.log(1 + 6223 / documentFrequency2)
                    
            commonSources[source] = (tfidf1, tfidf2)
        
        return commonSources
    ## Calculate tf-idf scores for each document->node pair
    weights = calcWeights()
    
    ## Use an inverted vector space model to calculate the
    ## similarity of the clusters (i.e. each document is a feature
    ## in the vector space and each node is a vector)
    dotProduct = 0
    squareSum1 = 0 
    squareSum2 = 0
    for source in weights:
        (weight1, weight2) = weights[source]
        dotProduct += weight1 * weight2
        
        squareSum1 += weight1 * weight1
        squareSum2 += weight2 * weight2
    
    normalizedLength = math.sqrt(squareSum1 * squareSum2)
    similarity = dotProduct / normalizedLength
    if similarity > 0.1:
        print "Similarity of clusters = ", similarity
    return similarity > 0.001
            
    
    
############################
#### base cluster score ####
############################

# Etzioni says: Words appearing in ... to few (3 or less) or too many
#(more than 40% of the collection) receive a score of 0.
# We assume that 'the collection' means the entire collection of documents
# rather than the documents local to the base cluster.
# 

    
def topBaseClusters(CompactTrie,
                    TopBaseClustersAmount=500,
                    MinNoInCollection=3,
                    MaxRatioInCollection=0.4,
                    minLimitForBaseClusterScore=1,
                    maxLimitForBaseClusterScore=6):  #Etziani-limits default
    '''
    Takes a compact trie structure and returns the TopBaseClustersAmount 
    number of base clusters, stop words removed.
    '''
    bc = generateBaseClusters(CompactTrie)
    num = countSources(CompactTrie)
    ws = getWordSources(CompactTrie)

    def score(baseCluster):

        def f(n):  ## limits taken from 'contextualized clustering..'-paper
            if n <= minLimitForBaseClusterScore:
                return 0
            elif n > maxLimitForBaseClusterScore:
                return 7
            else:
                return n

        def effectiveWords(label):
            n = 0
            for w in label:
                m = len(ws[w])
                if (m > MinNoInCollection and float(m) / float(num) <= MaxRatioInCollection):
                    n = n + 1
            return n

        return baseCluster.size * f(effectiveWords(baseCluster.label))

#    bb = dropSingletonBaseClusters(b)
    bc.sort(key=score)
    if TopBaseClustersAmount == 'all':
        return bc
    else:
        return bc[:TopBaseClustersAmount]


## filter out singleton source baseclusters from a list of baseclusters.
def dropSingletonBaseClusters(baseClusters):
    List = []
    for b in baseClusters:
        if b.size > 1: List.append(b)
    return List

#######################
### cluster merging ###
#######################

# We may think of the baseclusters and similarity measure as defining a similarity-graph
# where nodes are baseclusters and similar nodes are connected. Clusters corresponds to
# the connected components of the similarity graph.
#  
#  

 
def initialComponents(BaseClusters):
    ComponentIndex = []

    Head = component()  ## dummy head
    x = Head
    for b in BaseClusters:
        new = component()
        new.baseclusters = [b]
        new.previous = x
        x.next = new
        x = new
        ComponentIndex.append(new)
    Head.next.previous = None
    return ComponentIndex


def merge(Component1, Component2):
    for x in Component2.baseclusters:
        if x not in Component1.baseclusters:
            Component1.baseclusters.append(x)


def mergeComponents(BaseClusters):
    CI = initialComponents(BaseClusters)
    Components = []
    baseIndex = []
    count = 0

    for x in BaseClusters:
        baseIndex.append(count)
        count = count + 1

    i = 0
    while i < count:
        j = i + 1
        while  j < count:
            if similarJaccard(BaseClusters[i], BaseClusters[j]) and baseIndex[i] != baseIndex[j]:
                if baseIndex[i] < baseIndex[j]:
                    min = baseIndex[i]
                    max = baseIndex[j]
                else:
                    min = baseIndex[j]
                    max = baseIndex[i]
                merge(CI[min], CI[max])
                CI[max].delete()
                baseIndex[max] = baseIndex[min]
            j = j + 1
        i = i + 1
    #return CI[0]
    clusters = CI[0]
    while clusters != None:
        Components.append(clusters.baseclusters)
        clusters = clusters.next
    return Components




## A cluster is basically the union of sources of the baseclusters in a
## connected component in the similarity-graph.
## we add various extra parameters.

def makeClusters(ComponentList):
    Clusters = []
    for clusters in ComponentList:
        newCluster = cluster()
        for b in clusters:
            newCluster.addSources(b.sources)
            newCluster.labels.append(b.label)
            newCluster.collectWords(b.label)
        newCluster.sourceOverlap = common(map(lambda(x):x.sources, clusters))
        newCluster.labelOverlap = common(map(lambda(x):x.label, clusters))
        newCluster.makeLabel()  #arbitrary label, drop or fix to something interesting??
        Clusters.append(newCluster)
    return Clusters
        

def dropOneWordClusters(Clusters):
    result = []
    for x in Clusters:
        if len(x.labels) > 1 or len(x.labels[0]) > 1: result.append(x)
    return result


#####################
### auxiliaries   ###
#####################

def printClusters(ClusterList):
    for clusters in ClusterList: clusters.display()


def flatten(List):  # List of lists
    FlatList = []
    for x in List:
        for y in x: FlatList.append(y)
    return FlatList


def common(Lists):
    allElements = flatten(Lists) 
    Common = []
    for x in allElements:
        if not x in Common: Common.append(x)
    for x in Common[:]:
        for l in Lists:
            if not x in l:
                del Common[Common.index(x)]
                break
    return Common





        
    
