"""
Abstract Genetic Algorithm framework for optimization problems.
"""

import random
from abc import ABC, abstractmethod

class AbstractGA(ABC):
    """
    Abstract Genetic Algorithm implementation for maximization problems.
    Uses chromosome-based representation and evolutionary operators.
    
    IMPORTANTE: Este GA sempre MAXIMIZA o fitness.
    Se usar QBF_Inverse (valores negativos), valores MENOS negativos são MELHORES.
    """
    
    # Class variable for random number generation
    verbose = True
    
    def __init__(self, obj_function, generations, pop_size, mutation_rate, seed=0):
        """
        Initialize Genetic Algorithm.
        
        Args:
            obj_function: Evaluator object for the problem
            generations: Maximum number of generations
            pop_size: Population size
            mutation_rate: Probability of mutation
            seed: Random seed for reproducibility
        """
        self.obj_function = obj_function
        self.generations = generations
        self.pop_size = pop_size
        self.chromosome_size = obj_function.get_domain_size()
        self.mutation_rate = mutation_rate
        
        self.best_cost = None
        self.best_sol = None
        self.best_chromosome = None
        
        # Set random seed
        random.seed(seed)
    
    @abstractmethod
    def create_empty_sol(self):
        """
        Create an empty solution.
        
        Returns:
            Solution: Empty solution object
        """
        pass
    
    @abstractmethod
    def decode(self, chromosome):
        """
        Decode chromosome to solution (genotype to phenotype).
        
        Args:
            chromosome: List representing the genotype
            
        Returns:
            Solution: Decoded solution
        """
        pass
    
    @abstractmethod
    def generate_random_chromosome(self):
        """
        Generate a random chromosome.
        
        Returns:
            list: Random chromosome
        """
        pass
    
    @abstractmethod
    def fitness(self, chromosome):
        """
        Evaluate chromosome fitness.
        
        Args:
            chromosome: Chromosome to evaluate
            
        Returns:
            float: Fitness value (HIGHER is BETTER)
        """
        pass
    
    @abstractmethod
    def mutate_gene(self, chromosome, locus):
        """
        Mutate a gene at given locus.
        
        Args:
            chromosome: Chromosome to mutate
            locus: Position to mutate
        """
        pass
    
    def solve(self):
        """
        Main GA loop.
        
        Returns:
            Solution: Best solution found
        """
        # Initialize population
        population = self.initialize_population()
        
        self.best_chromosome = self.get_best_chromosome(population)
        self.best_sol = self.decode(self.best_chromosome)
        print(f"(Gen. 0) BestSol = {self.best_sol}")
        
        # Main evolutionary loop
        for g in range(1, self.generations + 1):
            parents = self.select_parents(population)
            offsprings = self.crossover(parents)
            mutants = self.mutate(offsprings)
            population = self.select_population(mutants)
            
            best_chromosome = self.get_best_chromosome(population)
            
            # fitness MAIOR é MELHOR (mesmo para valores negativos)
            if self.fitness(best_chromosome) > self.fitness(self.best_chromosome):
                self.best_chromosome = best_chromosome
                self.best_sol = self.decode(best_chromosome)
                if self.verbose:
                    print(f"(Gen. {g}) BestSol = {self.best_sol}")
        
        return self.best_sol
    
    def initialize_population(self):
        """
        Generate initial random population.
        
        Returns:
            list: Population of chromosomes
        """
        population = []
        for _ in range(self.pop_size):
            population.append(self.generate_random_chromosome())
        return population
    
    def get_best_chromosome(self, population):
        """
        Find best chromosome in population.
        CORRIGIDO: Agora procura por MAIOR fitness (maximização).
        
        Args:
            population: List of chromosomes
            
        Returns:
            list: Best chromosome
        """
        best_fitness = float('-inf')  # Começa com -infinito
        best_chromosome = None
        
        for chromosome in population:
            fit = self.fitness(chromosome)
            # MAIOR fitness é MELHOR
            if fit > best_fitness:
                best_fitness = fit
                best_chromosome = chromosome
        
        return best_chromosome
    
    def get_worse_chromosome(self, population):
        """
        Find worst chromosome in population.
        CORRIGIDO: Agora procura por MENOR fitness (pior para maximização).
        
        Args:
            population: List of chromosomes
            
        Returns:
            list: Worst chromosome
        """
        worse_fitness = float('inf')  # Começa com +infinito
        worse_chromosome = None
        
        for chromosome in population:
            fit = self.fitness(chromosome)
            # MENOR fitness é PIOR
            if fit < worse_fitness:
                worse_fitness = fit
                worse_chromosome = chromosome
        
        return worse_chromosome
    
    def select_parents(self, population):
        """
        Select parents using tournament selection.
        
        Args:
            population: Current population
            
        Returns:
            list: Selected parents
        """
        parents = []
        
        for _ in range(self.pop_size):
            idx1 = random.randint(0, self.pop_size - 1)
            parent1 = population[idx1]
            idx2 = random.randint(0, self.pop_size - 1)
            parent2 = population[idx2]
            
            # Seleciona o de MAIOR fitness
            if self.fitness(parent1) > self.fitness(parent2):
                parents.append(parent1[:])  # Copy
            else:
                parents.append(parent2[:])  # Copy
        
        return parents
    
    def crossover(self, parents):
        """
        Perform 2-point crossover on parents.
        
        Args:
            parents: List of parent chromosomes
            
        Returns:
            list: Offspring chromosomes
        """
        offsprings = []
        
        for i in range(0, self.pop_size, 2):
            parent1 = parents[i]
            parent2 = parents[i + 1]
            
            crosspoint1 = random.randint(0, self.chromosome_size)
            crosspoint2 = crosspoint1 + random.randint(0, self.chromosome_size - crosspoint1)
            
            offspring1 = []
            offspring2 = []
            
            for j in range(self.chromosome_size):
                if j >= crosspoint1 and j < crosspoint2:
                    offspring1.append(parent2[j])
                    offspring2.append(parent1[j])
                else:
                    offspring1.append(parent1[j])
                    offspring2.append(parent2[j])
            
            offsprings.append(offspring1)
            offsprings.append(offspring2)
        
        return offsprings
    
    def mutate(self, offsprings):
        """
        Apply mutation to offspring population.
        
        Args:
            offsprings: List of offspring chromosomes
            
        Returns:
            list: Mutated offspring
        """
        for chromosome in offsprings:
            for locus in range(self.chromosome_size):
                if random.random() < self.mutation_rate:
                    self.mutate_gene(chromosome, locus)
        
        return offsprings
    
    def select_population(self, offsprings):
        """
        Select population for next generation using elitism.
        CORRIGIDO: Agora substitui o PIOR offspring pelo MELHOR histórico.
        
        Args:
            offsprings: Offspring population
            
        Returns:
            list: New population
        """
        worse = self.get_worse_chromosome(offsprings)
        
        # Se o pior offspring é PIOR que o melhor histórico, substitui
        if self.fitness(worse) < self.fitness(self.best_chromosome):
            offsprings.remove(worse)
            offsprings.append(self.best_chromosome[:])
        
        return offsprings
