"""
Solution class for representing optimization problem solutions.
"""

class Solution(list):
    """
    Solution class that extends list to store solution elements.
    Maintains a cost attribute for the solution evaluation.
    """
    
    def __init__(self, elements=None):
        """
        Initialize a solution.
        
        Args:
            elements: Initial elements to add to the solution (optional)
        """
        super().__init__()
        self.cost = float('inf')
        
        if elements is not None:
            self.extend(elements)
    
    def copy(self):
        """
        Create a deep copy of the solution.
        
        Returns:
            A new Solution object with the same elements and cost
        """
        new_sol = Solution(list(self))
        new_sol.cost = self.cost
        return new_sol
    
    def __str__(self):
        """
        String representation of the solution.
        
        Returns:
            Formatted string with cost, size, and elements
        """
        return f"Solution: cost=[{self.cost}], size=[{len(self)}], elements={list(self)}"
    
    def __repr__(self):
        return self.__str__()
