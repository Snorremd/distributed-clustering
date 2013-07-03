'''
Created on Apr 2, 2013

@author: snorre
'''
import os
from datetime import datetime
from random import random, randint
import math as math

from chromosome import createRandomChromosome, crossChromosomes
import __main__
from tasks.task import CompactTrieClusteringTask
from easylogging.configLogger import getLoggerForFile
from cluster.clusterSettings import ClusterSettings
from text.corpora import Corpus


## Define module constants:
NONVERBOSE, VERBOSE, VERBOSEFILE = (0, 1, 2)
COLUMNHEADERS = ["Generation", "Fitness", "Time", "No. Clusters",
                 "No. base clusters",
                 "Precision 0", "Precision 1", "Precision 2", "Precision 3",
                 "Precision 4", "Precision 5",
                 "Recall 0", "Recall 1", "Recall 2", "Recall 3", "Recall 4",
                 "Recall 5",
                 "FMeasure 0", "FMeasure 1", "FMeasure 2", "FMeasure 3",
                 "FMeasure 4", "FMeasure 5"]

CHROMOSOMEHEADERS = ["Treetype", "top bc amount",
                     "min term occurrence", "max term occurrence",
                     "min limit bc score", "max limit bc score",
                     "drop singleton bc", "drop one word clusters"]


class GeneticAlgorithm:
    ''' A class implementing the genetic algorithm
    '''
    ## Define class constants
    ROULETTEWHEEL = 0

    def __init__(self, taskOrganizer, populationSize, noOfGenerations,
                 selectionType, selectionRate, mutationRate,
                 gaVerbosity):
        '''Constructor of the GeneticAlgorithm class

        Args:
            populationSize (int): the max number of individuals/chromosomes
            noOfGenerations (int): the upper limit on the no of generations
            selectionType (int): the type of selection to use for mating
            mutationRate (float): the ratio at which mutations occurs
            clusterSettings (ClusterSettings): an object wrapping info and
                                               settings to use for clustering
            gaVerbosity (int): wether to write to file or output to terminal
        '''
        self.logger = getLoggerForFile("GeneticAlgorithm")

        self.taskOrganizer = taskOrganizer
        self.taskOrganizer.attach(self)  # Get notified when tasks done
        self.gaVerbosity = gaVerbosity
        self.populationSize = populationSize
        self.noOfGenerations = noOfGenerations
        self.selectionType = selectionType
        self.selectionRate = selectionRate
        self.keepSize = int(2 * math.ceil(self.populationSize *
                                          self.selectionRate / 2))
        self.mutationRate = mutationRate
        self.population = []
        self.selectionProbabilities = []
        self.currentGeneration = 0

        self.clusterSettings = ClusterSettings(True, 1.0)
        self.corpus = Corpus("klimauken", "klimaukenOBTsnippets.xml",
                             "klimauken", True)

        timeNow = str(datetime.now())
        pathToMain = os.path.dirname(__main__.__file__)
        resultPath = os.path.join(pathToMain, "results",
                                  self.corpus.directory,
                                  self.corpus.name + timeNow)
        self.topFile = resultPath + "_top.csv"
        self.avgFile = resultPath + "_avg.csv"
        if self.gaVerbosity == VERBOSEFILE:
            writeToFile(self.topFile, ";".join(COLUMNHEADERS + \
                                               CHROMOSOMEHEADERS))
            writeToFile(self.avgFile, ";".join(COLUMNHEADERS))

        self.logger.info("Generate initial population")
        self.generateInitialPopulation()
        self.logger.info("Add population to task organizer")
        self.taskOrganizer.add_tasks(self.make_clustering_tasks())

    def generateInitialPopulation(self):
        '''Generates n number of initial chromosomes

        This method generates a number of initial chromosomes
        given the population size defined in self. The properties
        of the chromosome are given random values.
        '''
        for _ in range(self.populationSize):
            chromosome = createRandomChromosome()
            self.population.append(chromosome)

    def update(self):
        self.logger.info("Received results from task organizer")
        results = self.taskOrganizer.get_all_results()
        self.population = []
        for result in results:
            self.population.append(result.chromosome)
        self.sortPopulation()
        self.evolve()

    def evolve(self):
        '''Starts the evolution of the population

        Implements the evolution step in the genetic algorithm. The method
        currently use a predetermined limit on the number of generations to
        run. This can be changed to a dynamically determined limit based on
        a cutoff criteria like population convergence or lack of change in
        fitness over several generations...
        '''
        self.logger.info("Calculate data for generation " + \
                         str(self.currentGeneration))
        generationData = self.calcGenerationData()
        self.log_generation_data(generationData)
        self.results_to_avg_file(generationData[1:])
        self.results_to_top_file(generationData[0])

        if self.currentGeneration < self.noOfGenerations:
            self.currentGeneration += 1
            self.logger.info("Create generation {0}".format(self.currentGeneration))
            self.generationStep()
            self.taskOrganizer.add_tasks(self.make_clustering_tasks())

    def log_generation_data(self, generationData):
        topChromosome = generationData[0]
        outputText = ""
        outputText += "#######################################\n"
        outputText += "Generation {0} \n".format(self.currentGeneration)
        outputText += "_________________________________\n"
        outputText += "Top chromosome: " + str(topChromosome.genesAsTuple()) + "\n"
        outputText += "Fitness: %.4f" % (topChromosome.fitness,) + "\n"
        outputText += "Precisions: %.4f, %.4f, %.4f, %.4f, %.4f, %.4f" % \
                      topChromosome.get_precision() + "\n"
        outputText += "Recalls: %.4f, %.4f, %.4f, %.4f, %.4f, %.4f" % \
                      topChromosome.get_recall() + "\n"
        outputText += "FMeasures: %.4f, %.4f, %.4f, %.4f, %.4f, %.4f" % \
                      topChromosome.get_fmeasure() + "\n"
        outputText += "Time, no. clusters, no. baseclusters: " + \
                      str(topChromosome.get_time_number_clusters()) + "\n\n"

        outputText += "Average fitness: %.4f" % (generationData[1],) + "\n"
        outputText += "Average precision0: %.4f" % (generationData[3][0],) + "\n"
        outputText += "Average precision1: %.4f" % (generationData[3][1],) + "\n"
        outputText += "Average recall0: %.4f" % (generationData[4][0],) + "\n"
        outputText += "Average recall1: %.4f" % (generationData[4][1],) + "\n\n"

        outputText += "-----------------------\n"
        outputText += "Top 1 - 10 chromosomes:\n"
        outputText += "Fitness, gt0  , gt1   , gtr0 , gtr1  - chromosome:\n"
        for i in xrange(10):
            outputText += "%.4f, %.4f, %.4f, %.4f, %.4f" % \
                          (self.population[i].fitness,
                           self.population[i].get_precision()[0],
                           self.population[i].get_precision()[1],
                           self.population[i].get_recall()[0],
                           self.population[i].get_recall()[1])
            outputText += str(self.population[i].genesAsTuple())
            outputText += "\n"

    def results_to_avg_file(self, generationData):
        if self.gaVerbosity == VERBOSEFILE:
            stringsToJoin = [str(self.currentGeneration)]
            for value in generationData:
                if isinstance(value, list):
                    stringsToJoin.append(";".join(str(value)))
                else:
                    stringsToJoin.append(str(value))
            stringToWrite = ";".join(stringsToJoin)
            writeToFile(self.avgFile, stringToWrite)

    def results_to_top_file(self, topChromosome):
        stringsToJoin = [str(self.currentGeneration)]
        chromosomeResults = topChromosome.result
        for result in chromosomeResults:
            for value in result:
                stringsToJoin.append(str(value))
        stringToWrite = ";".join(stringsToJoin)
        writeToFile(self.topFile, stringToWrite)

    def generationStep(self):
        '''Simulates one generational step in the evolution of the population

        This method takes the population and sort it by fitness.
        The bottom half of the generation gets discarded. Then the
        algorithm mate pairs of individuals till the population size
        match the original population size. A random number of inidividuals
        have their chromosome randomly mutated.
        '''
        ##  Keep the selection rate top fraction of chromosomes
        self.population = self.population[:self.keepSize]
        self.produceOffspring()
        self.mutateChromosomes()

    def sortPopulation(self):
        """Sort all the chromosomes in the population
        """
        self.population = sorted(self.population, key=lambda chromosome:
        - chromosome.fitness)  # Use fitness as sorting key
        print "Sorted population by fitness: "
        for individual in self.population:
            print individual.fitness, str(individual.genesAsTuple())

    def produceOffspring(self):
        '''Produce new chromosomes as offspring from the previous
        generation's survivors.

        This method supports several types of selection:
        Roulette wheel

        '''
        ## Make a copy of the population:
        parents = ()
        if self.selectionType == GeneticAlgorithm.ROULETTEWHEEL:
            parents = self.rouletteWheelSelection()
        for i in xrange(0, len(parents), 2):
            parent1 = parents[i]
            parent2 = parents[i + 1]
            offsprings = crossChromosomes(parent1, parent2)
            self.population.append(offsprings[0])
            self.population.append(offsprings[1])
            print ".",
        print ""
        ## No need to sort here as population is sorted at beginning
        ## of each generation step

    def rouletteWheelSelection(self):
        '''A roulette wheel selection method using ranked selection

        The method is implemented based on the description in:
        http://dx.doi.org/10.1002/0471671746.ch1

        It calculates the probability of a chromosome being selected
        for pairing as a function of its rank (i.e. position in the population).
        It use a rank probability measure to increase performance.
        The possibility of duplicates is ignored as it should not have a drastic
        outcome on the genetic algorithm's performance.

        Returns:
            a set of indexes of which chromosomes in the population to
            use as parents in the crossing stage of the algorithm.
        '''
        ## If the selection probability list is empty, calculate probabilities:
        if len(self.selectionProbabilities) == 0:
            self.calculateRankingProbabilities()
        parents = []
        parents.append(self.population[0])  # Always include the best chromosome once
        ## While the number of parents AND chromosomes to keep are less than
        ## the population size we need parents to breed new offspring. Two
        ## parents produce two offspring.
        while len(parents) + self.keepSize < self.populationSize:
            randomProbability = random()
            for i in xrange(0, len(self.selectionProbabilities)):
                if (self.selectionProbabilities[i][1] < randomProbability):  # O(1) on avg
                    if not self.population[i] == parents[-1]:  # Need two different parents
                        parents.append(self.population[i])
                        break
        return parents

    def calculateRankingProbabilities(self):
        '''Calculate the ranking probabilities of each position
        in the population.

        This method takes the population and calculate the probability
        rank and accumulated probability rank of each member. These ranks
        can be used to randomly select (in roulette wheel selection for ex.)
        the inidividuals of a population for crossing.

        See http://dx.doi.org/10.1002/0471671746.ch1 for explanation.
        '''
        print "Calculate ranking probabilities"
        sumOfRanks = 0
        for rank in xrange(1, self.keepSize):
            sumOfRanks += rank
        accumulatedProbability = 0
        for position in xrange(0, self.keepSize):
            probabilityNumerator = self.keepSize - position + 1
            probability = probabilityNumerator / sumOfRanks
            accumulatedProbability += probability
            self.selectionProbabilities.append((probability, accumulatedProbability))

    def mutateChromosomes(self):
        '''Mutates a random gene in a random selection of chromosomes

        This method first calculate the number of mutations by using
        the mutation rate provided by the user. It then selects a random
        number of chromosomes (by index) and mutates a random gene in that
        chromosome by a random amount.
        '''
        chromosomeSize = len(self.population[0].genesAsTuple())
        noOfMutations = int(math.ceil((self.populationSize - 1)
                                      * self.mutationRate * chromosomeSize))
        for _ in xrange(noOfMutations):
            randomChromosome = randint(0, self.populationSize - 1)
            self.population[randomChromosome].mutate()  # Mutates a random chromosome

    def calcGenerationData(self):
        '''Calculate average fitness etc.
        '''
        topChromosome = self.population[0]
        averageNumTime = self.calc_average_num_time()
        averageFitness = self.calc_average_fitness()
        averagePrecisions = self.calc_average_precisions()
        averageRecalls = self.calc_average_recalls()
        averageFMeasures = self.calc_average_fmeasures()

        return (topChromosome,
                averageFitness,
                averageNumTime,
                averagePrecisions,
                averageRecalls,
                averageFMeasures)

    def calc_average_num_time(self):
        avgTime, noOfClusters, noBaseClusters = 0, 0, 0
        for chromosome in self.population:
            numTime = chromosome.get_time_number_clusters()
            avgTime += numTime[0]
            noOfClusters += numTime[1]
            noBaseClusters += numTime[2]
        avgTime /= self.populationSize
        noOfClusters /= self.populationSize
        noBaseClusters /= self.populationSize
        return [avgTime, noOfClusters, noBaseClusters]

    def calc_average_precisions(self):
        avgPrecisions = []
        for i in xrange(6):
            avgPrecision = 0
            for chromosome in self.population:
                avgPrecision += chromosome.get_precision()[i]
            avgPrecisions.append(avgPrecision / self.populationSize)
        return avgPrecisions

    def calc_average_recalls(self):
        avgRecalls = []
        for i in xrange(6):
            avgRecall = 0
            for chromosome in self.population:
                avgRecall += chromosome.get_precision()[i]
            avgRecalls.append(avgRecall / self.populationSize)
        return avgRecalls

    def calc_average_fmeasures(self):
        avgFMeasures = []
        for i in xrange(6):
            avgFMeasure = 0
            for chromosome in self.population:
                avgFMeasure += chromosome.get_precision()[i]
            avgFMeasures.append(avgFMeasure / self.populationSize)
        return avgFMeasures

    def calc_average_fitness(self):
        avgFitness = 0
        for chromosome in self.population:
            avgFitness += chromosome.fitness
        return avgFitness / self.populationSize

    def make_clustering_tasks(self):
        tasks = []
        for chromosome in self.population:
            tasks.append(CompactTrieClusteringTask(chromosome))
        return tasks


def writeToFile(filename, textToWrite):
    with open(filename, "a") as outputFile:
        outputFile.write(textToWrite + "\n")
