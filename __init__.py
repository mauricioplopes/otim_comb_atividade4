"""
Framework de Algoritmo Genético para problema de otimização QBF.

Este pacote contém:
- solution: Classe para representar soluções
- evaluator: Interface para avaliadores de problemas
- qbf: Implementação do problema QBF
- qbf_inverse: QBF inverso para minimização
- abstract_ga: Framework abstrato de Algoritmo Genético
- ga_qbf: GA específico para QBF
"""

__version__ = "1.0.0"
__author__ = "Conversão de Java para Python"

from .solution import Solution
from .evaluator import Evaluator
from .qbf import QBF
from .qbf_inverse import QBF_Inverse
from .abstract_ga import AbstractGA
from .ga_qbf import GA_QBF

__all__ = [
    'Solution',
    'Evaluator',
    'QBF',
    'QBF_Inverse',
    'AbstractGA',
    'GA_QBF',
]
