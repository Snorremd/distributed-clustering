"""
Created on Apr 2, 2013

@author: Snorre
"""
import os
from datetime import datetime
from random import random, randint
import math as math

from .chromosome import create_random_chromosome, crossChromosomes
from geneticalgorithm.result import GenerationResult
from tasks.task import CompactTrieClusteringTask
from easylogging.configLogger import get_logger_for_file
from cluster.clusterSettings import ClusterSettings
from corpora.corpus import Corpus


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
    """ A class implementing the genetic algorithm
    """
    ## Define class constants
    ROULETTEWHEEL = 0

    def __init__(self, taskOrganizer, dbHandler, corpus, populationSize,
                 maxNumOfGenerations, selectionType, selectionRate, mutationRate,
                 gaVerbosity, cluster_settings):
        """Constructor of the GeneticAlgorithm class

        Args:
            populationSize (int): the max number of individuals/chromosomes
            noOfGenerations (int): the upper limit on the no of generations
            selectionType (int): the type of selection to use for mating
            mutationRate (float): the ratio at which mutations occurs
            clusterSettings (ClusterSettings): an object wrapping info and
                                               settings to use for clustering
            gaVerbosity (int): wether to write to file or output to terminal
        """
        self.logger = get_logger_for_file("GeneticAlgorithm")
        self.dbHandler = dbHandler

        self.taskOrganizer = taskOrganizer
        self.taskOrganizer.attach(self)  # Get notified when tasks done
        self.gaVerbosity = gaVerbosity
        self.populationSize = populationSize
        self.maxNumOfGenerations = maxNumOfGenerations
        self.selectionType = selectionType
        self.selectionRate = selectionRate
        self.keepSize = int(2 * math.ceil(self.populationSize *
                                          self.selectionRate / 2))
        self.mutationRate = mutationRate
        self.population = []
        self.selectionProbabilities = []
        self.currentGeneration = 0

        self.convergence_count = 0
        self.highest_fitness = 0

        self.clusterSettings = cluster_settings
        self.corpus = corpus

        self.logger.info("Generate initial population")
        self.generateInitialPopulation()
        self.logger.info("Add population to task organizer")
        self.taskOrganizer.add_tasks(self.make_clustering_tasks(self.population))
        self.population = []

    def generateInitialPopulation(self):
        """Generates n number of initial chromosomes

        This method generates a number of initial chromosomes
        given the population size defined in self. The properties
        of the chromosome are given random values.
        """
        for _ in range(self.populationSize):
            chromosome = create_random_chromosome()
            self.population.append(chromosome)

    def update(self):
        """
        Call this method from notify method in TaskOrganizer instance.
        This instance is an observer of the TaskOrganizer instance.
        """
        self.logger.info("Received results from task organizer")
        results = self.taskOrganizer.get_all_results()

        for result in results:
            self.population.append(result.chromosome)
        self.sortPopulation()
        self.evolve()

    def evolve(self):
        """Starts the evolution of the population

        Implements the evolution step in the genetic algorithm. The method
        currently use a predetermined limit on the number of generations to
        run. This can be changed to a dynamically determined limit based on
        a cutoff criteria like population convergence or lack of change in
        fitness over several generations...
        """
        self.logger.info("Calculate data for generation {0}".format(self.currentGeneration))
        generationData = self.calcGenerationData()
        ## self.log_generation_data(generationData)
        ## self.results_to_avg_file(generationData[1:])
        ## self.results_to_top_file(generationData[0])

        ## Insert results into database
        self.dbHandler.insert_generation(self.algorithm_as_dict(generationData))
        self.dbHandler.insert_top_chromosomes(generationData.topChromosomes,
                                              self.currentGeneration)
        self.dbHandler.insert_worst_chromosomes(generationData
                                                .worstChromosomes,
                                                self.currentGeneration)
        self.dbHandler.insert_median_chromosomes(
            generationData.medianChromosomes, self.currentGeneration)

        self.dbHandler.drop_saved_population_table()
        self.dbHandler.create_saved_population_table()
        self.dbHandler.insert_chromosomes_saved_population(self.population)

        highest_fitness = generationData.topChromosomes[0].fitness
        if highest_fitness <= self.highest_fitness:
            self.convergence_count += 1
        elif highest_fitness > self.highest_fitness:
            self.convergence_count = 0
            self.highest_fitness = highest_fitness

        if not (self.currentGeneration > self.maxNumOfGenerations or self.convergence_count > 10):
            self.currentGeneration += 1
            self.logger.info(
                "Create generation {0}"
                .format(self.currentGeneration)
            )
            changed = self.generationStep()
            self.taskOrganizer.add_tasks(self.make_clustering_tasks(changed))

    def log_generation_data(self, generationData):
        topChromosome = generationData.topChromosomes[0]
        outputText = ""
        outputText += "#######################################\n"
        outputText += "Generation {0} \n".format(self.currentGeneration)
        outputText += "_________________________________\n"
        outputText += "Top chromosome: " + str(
            topChromosome.genes_as_tuple()) + "\n"
        outputText += "Fitness: %.4f" % (topChromosome.fitness,) + "\n"
        outputText += "Precisions: %.4f, %.4f, %.4f, %.4f, %.4f, %.4f" % \
                      topChromosome.get_precisions() + "\n"
        outputText += "Recalls: %.4f, %.4f, %.4f, %.4f, %.4f, %.4f" % \
                      topChromosome.get_recalls() + "\n"
        outputText += "FMeasures: %.4f, %.4f, %.4f, %.4f, %.4f, %.4f" % \
                      topChromosome.get_fmeasures() + "\n"
        outputText += "Time, no. clusters, no. baseclusters: " + \
                      str(topChromosome.get_time_number_clusters()) + "\n\n"

        outputText += "Average fitness: %.4f" % (generationData.averageFitness,
        ) + "\n"
        outputText += "Average precision0: %.4f" % (
            generationData.averagePrecisions[0],) + "\n"
        outputText += "Average precision1: %.4f" % (
            generationData.averagePrecisions[1],) + "\n"
        outputText += "Average recall0: %.4f" % (generationData.averageRecalls[
                                                     0],) + "\n"
        outputText += "Average recall1: %.4f" % (generationData.averageRecalls[
                                                     1],) + "\n\n"

        outputText += "-----------------------\n"
        outputText += "Top 1 - 10 chromosomes:\n"
        outputText += "Fitness, gt0  , gt1   , gtr0 , gtr1  - chromosome:\n"
        for i in range(10):
            outputText += "%.4f, %.4f, %.4f, %.4f, %.4f" % \
                          (self.population[i].fitness,
                           self.population[i].get_precisions()[0],
                           self.population[i].get_precisions()[1],
                           self.population[i].get_recalls()[0],
                           self.population[i].get_recalls()[1])
            outputText += str(self.population[i].genes_as_tuple())
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
        """Simulates one generational step in the evolution of the population

        This method takes the population and sort it by fitness.
        The bottom half of the generation gets discarded. Then the
        algorithm mate pairs of individuals till the population size
        match the original population size. A random number of child
        chromosomes have their chromosome randomly mutated.
        """
        ##  Keep the selection rate top fraction of chromosomes
        self.population = self.population[:self.keepSize]
        offspring = self.produceOffspring()
        changed = self.mutateChromosomes(offspring)
        return offspring + changed

    def sortPopulation(self):
        """Sort all the chromosomes in the population
        """

        def fitness_inverse(chromosome):
            return - chromosome.fitness

        # Use fitness as sorting key
        self.population = sorted(self.population, key=fitness_inverse)
        print("Sorted population by fitness: ")
        for individual in self.population:
            print(individual.fitness, str(individual.genes_as_tuple()))

    def produceOffspring(self):
        """Produce new chromosomes as offspring from the previous
        generation's survivors.

        This method supports Roulette Wheel selection

        """
        ## Make a copy of the population:
        parents = ()
        offspring = []
        if self.selectionType == GeneticAlgorithm.ROULETTEWHEEL:
            parents = self.rouletteWheelSelection()
        # noinspection PyArgumentList
        for i in range(0, len(parents), 2):
            parent1 = parents[i]
            parent2 = parents[i + 1]
            offsprings = crossChromosomes(parent1, parent2)
            offspring.extend([offsprings[0], offsprings[1]])
            print(".", end=' ')
        print("")
        return offspring
        ## No need to sort here as population is sorted at beginning
        ## of each generation step

    def rouletteWheelSelection(self):
        """A roulette wheel selection method using ranked selection

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
        """
        ## If the selection probability list is empty, calculate probabilities:
        if len(self.selectionProbabilities) == 0:
            self.calculateRankingProbabilities()
        ## Always include best chromosome
        parents = [self.population[0]]
        ## While the number of parents AND chromosomes to keep are less than
        ## the population size we need parents to breed new offspring. Two
        ## parents produce two offspring.
        while len(parents) + self.keepSize < self.populationSize:
            randomProbability = random()
            # noinspection PyArgumentList
            for i in range(0, len(self.selectionProbabilities)):
                ## O(1) on avg
                if self.selectionProbabilities[i][1] < randomProbability:
                    ## Need two different parents
                    if not self.population[i] == parents[-1]:
                        parents.append(self.population[i])
                        break
        return parents

    def calculateRankingProbabilities(self):
        """
        Calculate the ranking probabilities of each position
        in the population.

        This method takes the population and calculate the probability
        rank and accumulated probability rank of each member. These ranks
        can be used to randomly select (in roulette wheel selection for ex.)
        the individuals of a population for crossing.

        See http://dx.doi.org/10.1002/0471671746.ch1 for explanation.
        """
        print("Calculate ranking probabilities")
        sumOfRanks = 0
        # noinspection PyArgumentList
        for rank in range(1, self.keepSize):
            sumOfRanks += rank
        accumulatedProbability = 0
        # noinspection PyArgumentList
        for position in range(0, self.keepSize):
            probabilityNumerator = self.keepSize - position + 1
            probability = probabilityNumerator / sumOfRanks
            accumulatedProbability += probability
            self.selectionProbabilities.append(
                (probability, accumulatedProbability))

    def mutateChromosomes(self, offspring):
        """Mutates a random gene in a random selection of chromosomes

        This method first calculate the number of mutations by using
        the mutation rate provided by the user. It then selects a random
        number of chromosomes (by index) and mutates a random gene in that
        chromosome by a random amount.
        """
        chromosomeSize = len(self.population[0].genes_as_tuple())
        noOfMutations = int(math.ceil((len(offspring) - 1)
                                      * self.mutationRate * chromosomeSize))
        for _ in range(noOfMutations):
            randomChromosome = randint(0, len(offspring) - 1)
            offspring[randomChromosome].mutate()  # Mutates a random chromosome

        noOfMutations = int(math.ceil((len(self.population) - 1)
                                      * self.mutationRate * chromosomeSize))

        changed = []
        for _ in range(noOfMutations):
            randomChromosome = self.population[randint(0, len(self.population) - 1)]
            for chromosome in self.population:
                if chromosome.id == randomChromosome.id:
                    self.population.remove(chromosome)
            randomChromosome.mutate()
            changed.append(randomChromosome)

        return changed

    def calcGenerationData(self):
        """Calculate average fitness etc.
        """
        topChromosomes = self.population[0:10]
        worstChromosomes = self.population[-10:]
        medianChromosomes = self.get_median_chromosomes()
        averageNumTime = self.calc_average_num_time()
        averageFitness = self.calc_average_fitness()
        averagePrecision = self.calc_average_precision()
        averageRecall = self.calc_average_recall()
        averageFMeasure = self.calc_average_fmeasure()
        averageTagAccuracies = self.calc_average_tag_accuracies()
        averagePrecisions = self.calc_average_precisions()
        averageRecalls = self.calc_average_recalls()
        averageFMeasures = self.calc_average_fmeasures()

        generationResult = GenerationResult(averageFitness,
                                            averageNumTime[2],
                                            averageNumTime[1],
                                            averageNumTime[0],
                                            averagePrecision,
                                            averageRecall,
                                            averageFMeasure,
                                            averageTagAccuracies,
                                            averagePrecisions,
                                            averageRecalls,
                                            averageFMeasures,
                                            topChromosomes,
                                            medianChromosomes,
                                            worstChromosomes)

        return generationResult

    def calc_average_num_time(self):
        avgTime, noOfClusters, noBaseClusters = 0.0, 0.0, 0.0
        for chromosome in self.population:
            numTime = chromosome.get_time_number_clusters()
            avgTime += numTime[0]
            noOfClusters += numTime[1]
            noBaseClusters += numTime[2]
        avgTime /= self.populationSize
        noOfClusters /= self.populationSize
        noBaseClusters /= self.populationSize
        return [avgTime, noOfClusters, noBaseClusters]

    def calc_average_precision(self):
        avgPrecision = 0.0
        for chromosome in self.population:
            avgPrecision += chromosome.get_precision()
        return avgPrecision / self.populationSize

    def calc_average_recall(self):
        avgRecall = 0.0
        for chromosome in self.population:
            avgRecall += chromosome.get_recall()
        return avgRecall / self.populationSize

    def calc_average_fmeasure(self):
        avgFMeasure = 0.0
        for chromosome in self.population:
            avgFMeasure += chromosome.get_fmeasure()
        return avgFMeasure / self.populationSize

    def calc_average_tag_accuracies(self):
        avg_tag_accuracies = []
        for i in range(6):
            avg_tag_accuracy = 0.0
            for chromosome in self.population:
                avg_tag_accuracy += chromosome.get_tag_accuracies()[i]
            avg_tag_accuracies.append(avg_tag_accuracy / self.populationSize)
        return avg_tag_accuracies

    def calc_average_precisions(self):
        avgPrecisions = []
        for i in range(6):
            avgPrecision = 0.0
            for chromosome in self.population:
                avgPrecision += chromosome.get_precisions()[i]
            avgPrecisions.append(avgPrecision / self.populationSize)
        return avgPrecisions

    def calc_average_recalls(self):
        avgRecalls = []
        for i in range(6):
            avgRecall = 0.0
            for chromosome in self.population:
                avgRecall += chromosome.get_recalls()[i]
            avgRecalls.append(avgRecall / self.populationSize)
        return avgRecalls

    def calc_average_fmeasures(self):
        avgFMeasures = []
        for i in range(6):
            avgFMeasure = 0.0
            for chromosome in self.population:
                avgFMeasure += chromosome.get_fmeasures()[i]
            avgFMeasures.append(avgFMeasure / self.populationSize)
        return avgFMeasures

    def calc_average_fitness(self):
        avgFitness = 0.0
        for chromosome in self.population:
            avgFitness += chromosome.fitness
        return avgFitness / self.populationSize

    def get_median_chromosomes(self):
        medianChromosomes = []
        if len(self.population) % 2 == 0:
            firstMedian = int(math.floor(len(self.population)/2))-1
            secondMedian = firstMedian + 1
            medianChromosomes.extend([self.population[firstMedian],
                                      self.population[secondMedian]])
        else:
            medianChromosomes.append(
                self.population[int(self.populationSize/2)-1]
            )

        return medianChromosomes

    def make_clustering_tasks(self, chromosomes):
        tasks = []
        for chromosome in chromosomes:
            tasks.append(CompactTrieClusteringTask(chromosome))
        return tasks

    def algorithm_as_dict(self, generationResult):
        dictValues = {
            "generation": self.currentGeneration,
            "fitness_avg": generationResult.averageFitness,
            "fmeasure_avg": generationResult.averageFMeasure,
            "precision_avg": generationResult.averagePrecision,
            "recall_avg": generationResult.averageRecall,
            "time_avg": generationResult.averageTime,
            "number_of_clusters_avg": generationResult.averageClusters,
            "number_of_base_clusters_avg": generationResult
            .averageBaseClusters}

        accuracy_string = "tag_accuracy_avg_{0}"
        precisionString = "precision_avg_{0}"
        recallString = "recall_avg_{0}"
        fMeasureString = "fmeasure_avg_{0}"
        for i in range(6):
            dictValues[accuracy_string.format(i)] = \
                generationResult.averageTagAccuracies[i]

            dictValues[precisionString.format(i)] = \
                generationResult.averagePrecisions[i]

            dictValues[recallString.format(i)] = \
                generationResult.averageRecalls[i]

            dictValues[fMeasureString.format(i)] = \
                generationResult.averageFMeasures[i]

        return dictValues


def writeToFile(filename, textToWrite):
    with open(filename, "a") as outputFile:
        outputFile.write(textToWrite + "\n")

