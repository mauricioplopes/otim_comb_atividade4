"""
Inverse QBF for minimization procedures.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.qbf import QBF

class QBF_Inverse(QBF):
    """
    Inverse Quadratic Binary Function.
    Returns negative values for use with minimization algorithms.
    """
    
    def __init__(self, filename):
        """
        Initialize inverse QBF.
        
        Args:
            filename: Path to QBF instance file
        """
        super().__init__(filename)
    
    def evaluate_qbf(self):
        """
        Evaluate QBF with negated result.
        
        Returns:
            float: Negative of QBF value
        """
        return -super().evaluate_qbf()
    
    def evaluate_insertion_qbf(self, i):
        """
        Evaluate insertion with negated result.
        
        Args:
            i: Element index
            
        Returns:
            float: Negative of insertion cost
        """
        return -super().evaluate_insertion_qbf(i)
    
    def evaluate_removal_qbf(self, i):
        """
        Evaluate removal with negated result.
        
        Args:
            i: Element index
            
        Returns:
            float: Negative of removal cost
        """
        return -super().evaluate_removal_qbf(i)
    
    def evaluate_exchange_qbf(self, elem_in, elem_out):
        """
        Evaluate exchange with negated result.
        
        Args:
            elem_in: Element to insert
            elem_out: Element to remove
            
        Returns:
            float: Negative of exchange cost
        """
        return -super().evaluate_exchange_qbf(elem_in, elem_out)
