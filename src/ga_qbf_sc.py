"""
Genetic Algorithm implementation for QBF with Set Cover problem.
"""

import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.abstract_ga import AbstractGA
from src.qbf_sc import QBF_SC
from src.solution import Solution

class GA_QBF_SC(AbstractGA):
    """
    Genetic Algorithm for QBF with Set Cover constraints.
    Ensures all generated solutions satisfy coverage constraints.
    MAXIMIZA f(x) = x' * A * x (valores POSITIVOS)
    """
    
    def __init__(self, generations, pop_size, mutation_rate, filename, seed=0, 
                 population_strategy='random', adaptive_mutation=False):
        """
        Initialize GA for QBF-SC.
        
        Args:
            generations: Number of generations
            pop_size: Population size
            mutation_rate: Mutation probability (base rate if adaptive)
            filename: QBF-SC instance file
            seed: Random seed
            population_strategy: Strategy for population initialization
                - 'random': Completely random (PADRÃO)
                - 'lhc': Latin Hypercube Sampling (EVOL1)
                - 'greedy': Greedy + randomization
            adaptive_mutation: If True, use adaptive mutation rate (EVOL2)
        """
        qbf_sc = QBF_SC(filename) 
        super().__init__(qbf_sc, generations, pop_size, mutation_rate, seed)
        
        # Store reference to QBF-SC for constraint checking
        self.qbf_sc = qbf_sc
        
        # Store population strategy
        self.population_strategy = population_strategy.lower()
        
        # Store adaptive mutation flag
        self.adaptive_mutation = adaptive_mutation
        
        # Validate strategy
        valid_strategies = ['random', 'lhc', 'greedy']
        if self.population_strategy not in valid_strategies:
            raise ValueError(f"Invalid population_strategy: {self.population_strategy}. "
                           f"Must be one of: {valid_strategies}")
    
    # ========================================================================
    # Abstract methods implementation (required by AbstractGA)
    # ========================================================================
    
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
        Generate random feasible chromosome (PADRÃO method).
        Uses 50% probability and repairs to feasibility.
        
        Returns:
            list: Random feasible binary chromosome
        """
        # Generate chromosome with 50% probability for each bit
        chromosome = [random.randint(0, 1) for _ in range(self.chromosome_size)]
        
        # Repair to ensure feasibility
        self.repair_chromosome(chromosome)
        
        return chromosome
    
    def fitness(self, chromosome):
        """
        Evaluate chromosome fitness.
        
        IMPORTANTE: QBF_Inverse retorna valores NEGATIVOS.
        Para maximização: valores MENOS negativos são MELHORES.
        
        Args:
            chromosome: Chromosome to evaluate
            
        Returns:
            float: Fitness value (penalized if infeasible)
        """
        sol = self.decode(chromosome)
        
        # Check feasibility
        if not self.qbf_sc.is_feasible(sol):
            # Heavy penalty for infeasible solutions
            uncovered = self.qbf_sc.get_uncovered_elements(sol)
            penalty = len(uncovered) * 10000.0  # Penalidade muito alta
            return sol.cost - penalty
        
        return sol.cost
    
    def mutate_gene(self, chromosome, locus):
        """
        Flip bit at given locus and repair if needed.
        
        Args:
            chromosome: Chromosome to mutate
            locus: Gene position to mutate
        """
        # Flip the bit
        chromosome[locus] = 1 - chromosome[locus]
        
        # If we turned it off, we might need to repair
        if chromosome[locus] == 0:
            # Check if repair is needed
            sol = self.decode(chromosome)
            if not self.qbf_sc.is_feasible(sol):
                self.repair_chromosome(chromosome)
    
    # ========================================================================
    # Population initialization strategies
    # ========================================================================
    
    def initialize_population(self):
        """
        Generate initial population using selected strategy.
        
        Returns:
            list: Population of chromosomes
        """
        if self.population_strategy == 'lhc':
            return self.initialize_population_lhc()
        elif self.population_strategy == 'greedy':
            return self.initialize_population_greedy()
        else:  # 'random' (PADRÃO)
            return self.initialize_population_random()
    
    def initialize_population_random(self):
        """
        Generate initial random population (PADRÃO).
        Each chromosome is generated with 50% probability and then repaired.
        
        Returns:
            list: Population of chromosomes
        """
        population = []
        for _ in range(self.pop_size):
            population.append(self.generate_random_chromosome())
        return population
    
    def initialize_population_lhc(self):
        """
        Generate initial population using Latin Hypercube Sampling (EVOL1).
        Ensures better coverage of the solution space.
        
        Returns:
            list: Population of chromosomes
        """
        population = []
        
        # For each individual in population
        for i in range(self.pop_size):
            chromosome = [0] * self.chromosome_size
            
            # For each variable (gene)
            for j in range(self.chromosome_size):
                # Calculate stratum for this variable in this individual
                stratum_index = (i + j * self.pop_size) % self.pop_size
                
                # Probability threshold based on stratum
                threshold = (stratum_index + random.random()) / self.pop_size
                
                chromosome[j] = 1 if threshold > 0.5 else 0
            
            # Repair to ensure feasibility
            self.repair_chromosome(chromosome)
            population.append(chromosome)
        
        return population
    
    def initialize_population_greedy(self):
        """
        Generate initial population using greedy + randomization.
        Each chromosome starts with a greedy feasible solution.
        
        Returns:
            list: Population of chromosomes
        """
        population = []
        for _ in range(self.pop_size):
            population.append(self.generate_greedy_random_chromosome())
        return population
    
    # ========================================================================
    # Helper methods
    # ========================================================================
    
    def generate_greedy_random_chromosome(self):
        """
        Generate chromosome using greedy initialization + randomization.
        Uses greedy approach to ensure coverage, then randomly adds variables.
        
        Returns:
            list: Feasible binary chromosome
        """
        # Start with a greedy feasible solution
        chromosome = [0] * self.chromosome_size
        
        # Build minimal covering set greedily
        uncovered = self.qbf_sc.universe.copy()
        
        while uncovered:
            # Find variable that covers most uncovered elements
            best_var = None
            best_count = 0
            
            for var_idx in range(self.chromosome_size):
                if chromosome[var_idx] == 1:
                    continue
                
                count = len(self.qbf_sc.sets[var_idx] & uncovered)
                if count > best_count:
                    best_count = count
                    best_var = var_idx
            
            if best_var is None:
                break
            
            chromosome[best_var] = 1
            uncovered -= self.qbf_sc.sets[best_var]
        
        # Randomly add additional variables (30% chance)
        for var_idx in range(self.chromosome_size):
            if chromosome[var_idx] == 0 and random.random() < 0.3:
                chromosome[var_idx] = 1
        
        return chromosome
    
    def repair_chromosome(self, chromosome):
        """
        Repair chromosome to make it feasible.
        Adds missing coverage using greedy approach.
        
        Args:
            chromosome: Binary chromosome that may be infeasible
        """
        # Find uncovered elements
        covered = set()
        for var_idx in range(self.chromosome_size):
            if chromosome[var_idx] == 1:
                covered.update(self.qbf_sc.sets[var_idx])
        
        uncovered = self.qbf_sc.universe - covered
        
        # Add variables to cover missing elements (greedy by coverage)
        while uncovered:
            best_var = None
            best_count = 0
            
            for var_idx in range(self.chromosome_size):
                if chromosome[var_idx] == 1:
                    continue
                
                count = len(self.qbf_sc.sets[var_idx] & uncovered)
                if count > best_count:
                    best_count = count
                    best_var = var_idx
            
            if best_var is None:
                break
            
            chromosome[best_var] = 1
            uncovered -= self.qbf_sc.sets[best_var]
    
    # ========================================================================
    # Adaptive Mutation (EVOL2)
    # ========================================================================
    
    def get_mutation_rate(self, generation):
        """
        Calculate mutation rate for current generation.
        
        Args:
            generation: Current generation number
            
        Returns:
            float: Mutation rate for this generation
        """
        if not self.adaptive_mutation:
            return self.mutation_rate
        
        # Adaptive mutation: high at start, low at end
        initial_rate = 0.1
        final_rate = 0.001
        
        # Linear decay
        progress = generation / self.generations if self.generations > 0 else 0
        current_rate = initial_rate * (1 - progress) + final_rate * progress
        
        return current_rate
    
    def mutate(self, offsprings, generation=None):
        """
        Apply mutation to offspring population.
        
        Args:
            offsprings: List of offspring chromosomes
            generation: Current generation (for adaptive mutation)
            
        Returns:
            list: Mutated offspring
        """
        # Get current mutation rate
        if generation is not None and self.adaptive_mutation:
            mutation_rate = self.get_mutation_rate(generation)
        else:
            mutation_rate = self.mutation_rate
        
        # Apply mutation
        for chromosome in offsprings:
            for locus in range(self.chromosome_size):
                if random.random() < mutation_rate:
                    self.mutate_gene(chromosome, locus)
        
        return offsprings
    
    # ========================================================================
    # Genetic operators with feasibility maintenance
    # ========================================================================
    
    def crossover(self, parents):
        """
        Perform 2-point crossover on parents with feasibility repair.
        
        Args:
            parents: List of parent chromosomes
            
        Returns:
            list: Offspring chromosomes (all feasible)
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
            
            # Repair offspring if needed
            self.repair_chromosome(offspring1)
            self.repair_chromosome(offspring2)
            
            offsprings.append(offspring1)
            offsprings.append(offspring2)
        
        return offsprings
    
    def solve(self):
        """
        Main GA loop with feasibility tracking.
        
        Returns:
            Solution: Best feasible solution found
        """
        # Initialize population using selected strategy
        population = self.initialize_population()
        
        self.best_chromosome = self.get_best_chromosome(population)
        self.best_sol = self.decode(self.best_chromosome)
        
        if self.verbose:
            actual_cost = -self.best_sol.cost
            print(f"(Gen. 0) BestSol = cost={actual_cost:.1f}, size={len(self.best_sol)}")
            print(f"         Feasible: {self.qbf_sc.is_feasible(self.best_sol)}")
            print(f"         Strategy: {self.population_strategy.upper()}")
            if self.adaptive_mutation:
                print(f"         Adaptive Mutation: ENABLED (rate: {self.get_mutation_rate(0):.4f})")
            else:
                print(f"         Mutation Rate: {self.mutation_rate:.4f} (fixed)")
        
        # Main evolutionary loop
        for g in range(1, self.generations + 1):
            parents = self.select_parents(population)
            offsprings = self.crossover(parents)
            mutants = self.mutate(offsprings, generation=g)
            population = self.select_population(mutants)
            
            best_chromosome = self.get_best_chromosome(population)
            
            # IMPORTANTE: Como QBF_Inverse retorna negativos,
            # fitness MAIOR (menos negativo) é MELHOR
            if self.fitness(best_chromosome) > self.fitness(self.best_chromosome):
                self.best_chromosome = best_chromosome
                self.best_sol = self.decode(best_chromosome)
                
                if self.verbose:
                    is_feasible = self.qbf_sc.is_feasible(self.best_sol)
                    actual_cost = -self.best_sol.cost
                    print(f"(Gen. {g}) BestSol = cost={actual_cost:.1f}, size={len(self.best_sol)}")
                    print(f"         Feasible: {is_feasible}")
                    if self.adaptive_mutation:
                        print(f"         Mutation Rate: {self.get_mutation_rate(g):.4f}")
        
        return self.best_sol
