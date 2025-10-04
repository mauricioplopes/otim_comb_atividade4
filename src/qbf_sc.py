"""
Quadratic Binary Function with Set Cover constraints (QBF-SC).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.qbf import QBF 
from typing import List, Set

class QBF_SC(QBF):
    """
    QBF with Set Cover constraints for MAXIMIZATION.
    Extends QBF to handle set cover constraints where all elements must be covered.
    
    Universe to cover: N = {1, 2, ..., n}
    Sets: S = {S1, S2, ..., Sn} where each Si ⊆ N
    Decision variables: x1, x2, ..., xn (binary)
    
    Constraint: For all k ∈ N, there exists at least one Si such that k ∈ Si and xi = 1
    Objective: MAXIMIZE f(x) = x' * A * x
    """
    
    def __init__(self, filename):
        """
        Initialize QBF-SC from instance file.
        
        Args:
            filename: Path to QBF-SC instance file
        """
        self.sets = []  # List of sets, where sets[i] contains elements covered by variable i
        self.universe = set()  # Universe of elements to cover
        super().__init__(filename)
    
    def _read_input(self, filename):
        """
        Read QBF-SC instance from file.
        
        Expected format:
        - Line 1: n (number of variables)
        - Line 2: s1 s2 ... sn (OPTIONAL - set sizes)
        - Lines 3 to n+2: elements covered by each set Si (1-indexed in file)
        - Remaining lines: upper triangular matrix A
        
        Args:
            filename: Path to instance file
            
        Returns:
            int: Problem dimension
        """
        try:
            with open(filename, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
            
            if not lines:
                raise ValueError("Empty file")
            
            # Read dimension
            n = int(lines[0])
            
            # Initialize matrix A
            self.A = [[0.0 for _ in range(n)] for _ in range(n)]
            
            # Detect format: check if line 1 has n integers (set sizes)
            line1_tokens = lines[1].split()
            line1_values = [int(x) for x in line1_tokens]
            
            # Se a linha 1 tem exatamente n valores pequenos (tamanhos), pula ela
            if len(line1_values) == n and all(v <= n for v in line1_values):
                set_start_line = 2
            else:
                set_start_line = 1
            
            # Read set cover constraints (n sets)
            self.sets = []
            self.universe = set(range(1, n + 1))  # Universe is {1, 2, ..., n}
            
            line_idx = set_start_line
            for i in range(n):
                if line_idx >= len(lines):
                    raise ValueError(f"Missing set definition for variable {i}")
                
                # Read elements in set i (1-indexed)
                elements_str = lines[line_idx].split()
                if elements_str:
                    elements = set(int(elem) for elem in elements_str)
                    if not elements.issubset(self.universe):
                        invalid = elements - self.universe
                        raise ValueError(f"Set {i} contains invalid elements: {invalid}")
                    self.sets.append(elements)
                else:
                    self.sets.append(set())
                
                line_idx += 1
            
            # Read upper triangular matrix A
            for i in range(n):
                if line_idx >= len(lines):
                    raise ValueError(f"Missing matrix row {i}")
                
                values = list(map(float, lines[line_idx].split()))
                expected_elements = n - i
                
                if len(values) != expected_elements:
                    raise ValueError(
                        f"Row {i}: expected {expected_elements} elements, got {len(values)}"
                    )
                
                # Fill upper triangular part
                for j, val in enumerate(values):
                    col_idx = i + j
                    self.A[i][col_idx] = val
                    # Lower triangular part stays zero (asymmetric)
                    if col_idx != i:
                        self.A[col_idx][i] = 0.0
                
                line_idx += 1
            
            return n
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Instance file '{filename}' not found")
        except Exception as e:
            raise ValueError(f"Error reading file {filename}: {e}")
    
    def is_feasible(self, sol) -> bool:
        """
        Check if solution satisfies set cover constraints.
        All elements from universe {1, 2, ..., n} must be covered by at least one selected set.
        
        Args:
            sol: Solution object (contains indices of selected variables)
            
        Returns:
            bool: True if solution is feasible
        """
        covered = set()
        for var_idx in sol:
            if 0 <= var_idx < len(self.sets):
                covered.update(self.sets[var_idx])
        
        return self.universe.issubset(covered)
    
    def get_uncovered_elements(self, sol) -> Set[int]:
        """
        Get elements from universe that are not covered by current solution.
        
        Args:
            sol: Solution object
            
        Returns:
            set: Uncovered elements (1-indexed)
        """
        covered = set()
        for var_idx in sol:
            if 0 <= var_idx < len(self.sets):
                covered.update(self.sets[var_idx])
        
        return self.universe - covered
    
    def get_coverage_count(self, sol) -> dict:
        """
        Count how many times each element in universe is covered.
        
        Args:
            sol: Solution object
            
        Returns:
            dict: Mapping from element (1-indexed) to coverage count
        """
        coverage = {elem: 0 for elem in self.universe}
        
        for var_idx in sol:
            if 0 <= var_idx < len(self.sets):
                for elem in self.sets[var_idx]:
                    if elem in coverage:
                        coverage[elem] += 1
        
        return coverage
    
    def get_removable_variables(self, sol) -> List[int]:
        """
        Get variables that can be removed without violating coverage constraints.
        
        Args:
            sol: Solution object
            
        Returns:
            list: Indices of variables that can be safely removed
        """
        if not self.is_feasible(sol):
            return []
        
        coverage = self.get_coverage_count(sol)
        
        removable = []
        for var_idx in sol:
            if var_idx >= len(self.sets):
                continue
            
            can_remove = True
            for elem in self.sets[var_idx]:
                if coverage.get(elem, 0) <= 1:
                    can_remove = False
                    break
            
            if can_remove:
                removable.append(var_idx)
        
        return removable
    
    def print_coverage_info(self, sol):
        """
        Print coverage information for debugging.
        
        Args:
            sol: Solution object
        """
        coverage = self.get_coverage_count(sol)
        uncovered = self.get_uncovered_elements(sol)
        
        print(f"Solution size: {len(sol)}")
        print(f"Universe size: {len(self.universe)}")
        print(f"Feasible: {self.is_feasible(sol)}")
        
        if uncovered:
            print(f"Uncovered elements ({len(uncovered)}): {sorted(list(uncovered)[:10])}...")
        else:
            print(f"All elements covered!")
        
        if coverage:
            coverage_values = list(coverage.values())
            covered_count = sum(1 for c in coverage_values if c > 0)
            print(f"Coverage statistics:")
            print(f"  - Elements covered: {covered_count}/{len(self.universe)}")
            print(f"  - Max coverage: {max(coverage_values)}")
    
    def validate_instance(self):
        """
        Validate that the instance is well-formed.
        
        Returns:
            tuple: (is_valid, message)
        """
        all_coverable = set()
        for s in self.sets:
            all_coverable.update(s)
        
        missing = self.universe - all_coverable
        if missing:
            return False, f"Elements {missing} cannot be covered by any set"
        
        return True, "Instance is valid"
