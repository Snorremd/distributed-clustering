#
#  Compact Trie - Auxilliary
#  Phrases = Lists of words
#
#  Richard E. Moe
#   08.10.2010
#

emptyphrase = []

def firstword(Phrase): return Phrase[0]


def getCommonStartSegment(Phrase1, Phrase2):
    '''
    Find a common start segment (word) if any.
    @return: (getCommonStartSegment, p1, p2)
    
    getCommonStartSegment = ["common", "words", "in", "phrases"]
    p1/p2 = ["unique", "words", "in", "phrase1/phrase2"]
    '''
    getCommonStartSegment = []
    p1 = Phrase1[:] # copy Phrases
    p2 = Phrase2[:] 
    for word in Phrase1:
        if p1==[] or p2 ==[]: break
        elif word == p2[0]:
            getCommonStartSegment.append(word)
            del p1[0]
            del p2[0]
        else: break
    return (getCommonStartSegment, p1, p2)


def stringToPhrase(string):
    '''
    Takes a string in the form of:
    "word1 word2 word3 ... wordn"
    and returns a list in the form
    ["word1", "word2", "word3", ..., "wordn"]
    '''
    if string=='' or string.isspace(): return []
    string=string.strip()+' '#need a trailing blank for the last letter
    phrase = []
    length = len(string)
    i=0
    pos=0
    while i<length and pos > -1:
        pos = string.find(' ', i, length)
        phrase.append(string[i:pos])
        i = pos+1
    return phrase


#def stringsToPhrases(List):  #List of strings
#    return map(stringToPhrase, List)



def stringSourceToPhraseSource(Pair): #Pair = (String, Source)
    (x,y)=Pair
    return(stringToPhrase(x), y)


def phraseToString(Phrase):
    String = ""
    for x in Phrase: String = String+" "+x
    return String.strip()
