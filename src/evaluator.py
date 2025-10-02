"""
Evaluator interface for optimization problems.
"""

from abc import ABC, abstractmethod

class Evaluator(ABC):
    """
    Abstract interface for problem evaluators.
    Provides methods to evaluate solutions and incremental cost variations.
    """
    
    @abstractmethod
    def get_domain_size(self):
        """
        Get the size of the problem domain.
        
        Returns:
            int: Number of decision variables
        """
        pass
    
    @abstractmethod
    def evaluate(self, sol):
        """
        Evaluate a complete solution.
        
        Args:
            sol: Solution object to evaluate
            
        Returns:
            float: Evaluation cost/value of the solution
        """
        pass
    
    @abstractmethod
    def evaluate_insertion_cost(self, elem, sol):
        """
        Evaluate the cost variation of inserting an element.
        
        Args:
            elem: Element to insert
            sol: Current solution
            
        Returns:
            float: Cost variation from insertion
        """
        pass
    
    @abstractmethod
    def evaluate_removal_cost(self, elem, sol):
        """
        Evaluate the cost variation of removing an element.
        
        Args:
            elem: Element to remove
            sol: Current solution
            
        Returns:
            float: Cost variation from removal
        """
        pass
    
    @abstractmethod
    def evaluate_exchange_cost(self, elem_in, elem_out, sol):
        """
        Evaluate the cost variation of exchanging elements.
        
        Args:
            elem_in: Element to insert
            elem_out: Element to remove
            sol: Current solution
            
        Returns:
            float: Cost variation from exchange
        """
        pass
