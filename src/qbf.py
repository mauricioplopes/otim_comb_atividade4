"""
Quadratic Binary Function (QBF) problem implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.evaluator import Evaluator
from src.solution import Solution

class QBF(Evaluator):
    """
    Quadratic Binary Function evaluator.
    Evaluates f(x) = x'.A.x where x is a binary vector and A is a coefficient matrix.
    """
    
    def __init__(self, filename):
        """
        Initialize QBF from instance file.
        
        Args:
            filename: Path to the QBF instance file
        """
        self.size = None
        self.A = None
        self.variables = None
        
        self.size = self._read_input(filename)
        self.variables = self._allocate_variables()
    
    def _read_input(self, filename):
        """
        Read QBF instance from file.
        Expected format:
        - First line: dimension n
        - Following lines: upper triangular matrix A
        
        Args:
            filename: Path to instance file
            
        Returns:
            int: Problem dimension
        """
        with open(filename, 'r') as f:
            tokens = []
            for line in f:
                tokens.extend(line.strip().split())
        
        idx = 0
        size = int(tokens[idx])
        idx += 1
        
        self.A = [[0.0 for _ in range(size)] for _ in range(size)]
        
        for i in range(size):
            for j in range(i, size):
                self.A[i][j] = float(tokens[idx])
                idx += 1
                if j > i:
                    self.A[j][i] = 0.0
        
        return size
    
    def _allocate_variables(self):
        """
        Allocate array for domain variables.
        
        Returns:
            list: Array of zeros for variables
        """
        return [0.0] * self.size
    
    def reset_variables(self):
        """Reset all variables to zero."""
        self.variables = [0.0] * self.size
    
    def set_variables(self, sol):
        """
        Set variables from solution.
        
        Args:
            sol: Solution object containing selected elements
        """
        self.reset_variables()
        if sol:
            for elem in sol:
                self.variables[elem] = 1.0
    
    def get_domain_size(self):
        """
        Get problem dimension.
        
        Returns:
            int: Number of variables
        """
        return self.size
    
    def evaluate(self, sol):
        """
        Evaluate solution by computing x'.A.x
        
        Args:
            sol: Solution to evaluate
            
        Returns:
            float: QBF value
        """
        self.set_variables(sol)
        sol.cost = self.evaluate_qbf()
        return sol.cost
    
    def evaluate_qbf(self):
        """
        Compute QBF value f(x) = x'.A.x
        
        Returns:
            float: QBF evaluation
        """
        total = 0.0
        
        for i in range(self.size):
            aux = 0.0
            for j in range(self.size):
                aux += self.variables[j] * self.A[i][j]
            total += aux * self.variables[i]
        
        return total
    
    def evaluate_insertion_cost(self, elem, sol):
        """
        Evaluate cost of inserting element.
        
        Args:
            elem: Element index to insert
            sol: Current solution
            
        Returns:
            float: Cost variation
        """
        self.set_variables(sol)
        return self.evaluate_insertion_qbf(elem)
    
    def evaluate_insertion_qbf(self, i):
        """
        Compute insertion cost for element i.
        
        Args:
            i: Element index
            
        Returns:
            float: Cost variation
        """
        if self.variables[i] == 1:
            return 0.0
        
        return self._evaluate_contribution_qbf(i)
    
    def evaluate_removal_cost(self, elem, sol):
        """
        Evaluate cost of removing element.
        
        Args:
            elem: Element index to remove
            sol: Current solution
            
        Returns:
            float: Cost variation
        """
        self.set_variables(sol)
        return self.evaluate_removal_qbf(elem)
    
    def evaluate_removal_qbf(self, i):
        """
        Compute removal cost for element i.
        
        Args:
            i: Element index
            
        Returns:
            float: Cost variation
        """
        if self.variables[i] == 0:
            return 0.0
        
        return -self._evaluate_contribution_qbf(i)
    
    def evaluate_exchange_cost(self, elem_in, elem_out, sol):
        """
        Evaluate cost of exchanging elements.
        
        Args:
            elem_in: Element to insert
            elem_out: Element to remove
            sol: Current solution
            
        Returns:
            float: Cost variation
        """
        self.set_variables(sol)
        return self.evaluate_exchange_qbf(elem_in, elem_out)
    
    def evaluate_exchange_qbf(self, elem_in, elem_out):
        """
        Compute exchange cost.
        
        Args:
            elem_in: Element to insert
            elem_out: Element to remove
            
        Returns:
            float: Cost variation
        """
        if elem_in == elem_out:
            return 0.0
        
        if self.variables[elem_in] == 1:
            return self.evaluate_removal_qbf(elem_out)
        
        if self.variables[elem_out] == 0:
            return self.evaluate_insertion_qbf(elem_in)
        
        total = 0.0
        total += self._evaluate_contribution_qbf(elem_in)
        total -= self._evaluate_contribution_qbf(elem_out)
        total -= (self.A[elem_in][elem_out] + self.A[elem_out][elem_in])
        
        return total
    
    def _evaluate_contribution_qbf(self, i):
        """
        Compute contribution of element i to QBF.
        
        Args:
            i: Element index
            
        Returns:
            float: Contribution value
        """
        total = 0.0
        
        for j in range(self.size):
            if i != j:
                total += self.variables[j] * (self.A[i][j] + self.A[j][i])
        
        total += self.A[i][i]
        
        return total
    
    def print_matrix(self):
        """Print coefficient matrix A."""
        for i in range(self.size):
            for j in range(i, self.size):
                print(f"{self.A[i][j]} ", end="")
            print()
