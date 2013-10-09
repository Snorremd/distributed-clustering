__author__ = 'snorre'

class GenerationResult(object):

    def __init__(self, averageFitness=None, averageBaseClusters=None,
                 averageClusters=None, averageTime=None, averagePrecision=None,
                 averageRecall=None, averageFMeasure=None,
                 averageTagAccuracies = None,
                 averagePrecisions=None, averageRecalls=None,
                 averageFMeasures=None, topChromosomes=None,
                 medianChromosomes=None, worstChromosomes=None):
        self.averageFitness = averageFitness
        self.averageBaseClusters = averageBaseClusters
        self.averageClusters = averageClusters
        self.averageTime = averageTime
        self.averagePrecision = averagePrecision
        self.averageRecall = averageRecall
        self.averageFMeasure = averageFMeasure
        self.averageTagAccuracies = averageTagAccuracies
        self.averagePrecisions = averagePrecisions
        self.averageRecalls = averageRecalls
        self.averageFMeasures = averageFMeasures
        self.topChromosomes = topChromosomes
        self.medianChromosomes = medianChromosomes
        self.worstChromosomes = worstChromosomes