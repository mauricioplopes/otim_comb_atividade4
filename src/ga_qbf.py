"""
Genetic Algorithm implementation for QBF problem.
"""

import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.abstract_ga import AbstractGA
from src.qbf import QBF
from src.solution import Solution

class GA_QBF(AbstractGA):
    """
    Genetic Algorithm for Quadratic Binary Function optimization.
    """
    
    def __init__(self, generations, pop_size, mutation_rate, filename, seed=0):
        """
        Initialize GA for QBF.
        
        Args:
            generations: Number of generations
            pop_size: Population size
            mutation_rate: Mutation probability
            filename: QBF instance file
            seed: Random seed
        """
        qbf = QBF(filename)
        super().__init__(qbf, generations, pop_size, mutation_rate, seed)
    
    def create_empty_sol(self):
        """
        Create empty solution with zero cost.
        
        Returns:
            Solution: Empty solution
        """
        sol = Solution()
        sol.cost = 0.0
        return sol
    
    def decode(self, chromosome):
        """
        Decode binary chromosome to solution.
        
        Args:
            chromosome: Binary chromosome (list of 0s and 1s)
            
        Returns:
            Solution: Decoded solution
        """
        solution = self.create_empty_sol()
        
        for locus in range(len(chromosome)):
            if chromosome[locus] == 1:
                solution.append(locus)
        
        self.obj_function.evaluate(solution)
        return solution
    
    def generate_random_chromosome(self):
        """
        Generate random binary chromosome.
        
        Returns:
            list: Random binary chromosome
        """
        chromosome = []
        for _ in range(self.chromosome_size):
            chromosome.append(random.randint(0, 1))
        return chromosome
    
    def fitness(self, chromosome):
        """
        Evaluate chromosome fitness.
        
        Args:
            chromosome: Chromosome to evaluate
            
        Returns:
            float: Fitness (solution cost)
        """
        return self.decode(chromosome).cost
    
    def mutate_gene(self, chromosome, locus):
        """
        Flip bit at given locus.
        
        Args:
            chromosome: Chromosome to mutate
            locus: Gene position to mutate
        """
        chromosome[locus] = 1 - chromosome[locus]
