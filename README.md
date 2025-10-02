# Framework de Algoritmo Genético para QBF em Python

Este é um framework de Algoritmo Genético (GA) para resolver o problema de Função Binária Quadrática (QBF), convertido do framework Java original mantendo a mesma estrutura e funcionalidades.

## Estrutura do Projeto

```
projeto/
│
├── src/
│   ├── solution.py          # Classe Solution para representar soluções
│   ├── evaluator.py         # Interface abstrata Evaluator
│   ├── qbf.py              # Implementação do problema QBF
│   ├── qbf_inverse.py      # QBF inverso para minimização
│   ├── abstract_ga.py      # Framework abstrato do GA
│   └── ga_qbf.py           # GA específico para QBF
│
├── instances/
│   └── qbf/
│       ├── qbf020          # Instâncias QBF
│       ├── qbf040
│       ├── qbf060
│       ├── qbf080
│       └── qbf100
│
└── main_qbf.py             # Script principal de execução
```


## Uso

### Execução Básica

```bash
python main_qbf.py instances/qbf/qbf020
```

### Execução com Parâmetros Customizados

```bash
python main_qbf.py instances/qbf/qbf040 1000 100 0.01
```

Onde:
- **1000**: número de gerações
- **100**: tamanho da população
- **0.01**: taxa de mutação

### Parâmetros Padrão

Se não especificados, os valores padrão são:
- Gerações: 1000
- Tamanho da população: 100
- Taxa de mutação: 0.01 (1/100)

## Componentes Principais

### 1. Solution (solution.py)
Classe que representa uma solução do problema:
- Estende `list` para armazenar elementos da solução
- Mantém atributo `cost` com o valor da solução
- Métodos: `copy()`, `__str__()`

### 2. Evaluator (evaluator.py)
Interface abstrata para avaliadores de problemas:
- `get_domain_size()`: retorna tamanho do domínio
- `evaluate()`: avalia solução completa
- `evaluate_insertion_cost()`: avalia inserção de elemento
- `evaluate_removal_cost()`: avalia remoção de elemento
- `evaluate_exchange_cost()`: avalia troca de elementos

### 3. QBF (qbf.py)
Implementação do problema QBF:
- Lê instâncias de arquivo
- Avalia f(x) = x'.A.x
- Métodos eficientes para avaliação incremental

### 4. AbstractGA (abstract_ga.py)
Framework abstrato do Algoritmo Genético:
- Implementa loop evolutivo principal
- Seleção por torneio
- Crossover de 2 pontos
- Mutação com taxa configurável
- Elitismo para preservar melhor solução

### 5. GA_QBF (ga_qbf.py)
Implementação específica do GA para QBF:
- Cromossomos binários (0 ou 1)
- Decodificação: genes com valor 1 são incluídos na solução
- Mutação: inversão de bit (flip)
- Fitness: valor da função QBF

## Formato das Instâncias

As instâncias QBF devem seguir o formato:

```
n
a11 a12 a13 ... a1n
a22 a23 ... a2n
...
ann
```

Onde:
- **n**: dimensão do problema (número de variáveis)
- **aij**: matriz triangular superior de coeficientes

Exemplo (qbf020):
```
20
5 9 -3 -5 -4 -6 -4 10 2 8 -6 -2 4 4 -9 -9 -2 -4 5 -2
-1 -7 -9 3 0 3 -3 8 9 -9 1 2 -7 5 -3 -9 2 2 -2
...
```

## Exemplo de Saída

```
============================================================
Genetic Algorithm for QBF Problem
============================================================
Instance:      instances/qbf/qbf020
Generations:   1000
Pop Size:      100
Mutation Rate: 0.01
============================================================

(Gen. 0) BestSol = Solution: cost=[145.0], size=[12], elements=[0, 2, 4, ...]
(Gen. 15) BestSol = Solution: cost=[178.0], size=[10], elements=[1, 3, 5, ...]
(Gen. 42) BestSol = Solution: cost=[203.0], size=[11], elements=[0, 2, 3, ...]
...

============================================================
Results
============================================================
Best Solution: Solution: cost=[234.0], size=[9], elements=[0, 1, 4, 7, 8, 11, 13, 15, 18]
Time: 45.23 seconds
============================================================
```

## Funcionalidades Implementadas

### Operadores Genéticos

1. **Inicialização**: População aleatória com genes binários
2. **Seleção**: Torneio binário entre dois indivíduos
3. **Crossover**: 2-point crossover
4. **Mutação**: Bit flip com probabilidade configurável
5. **Substituição**: Elitismo - preserva melhor indivíduo

### Avaliação Eficiente

O framework implementa métodos eficientes para:
- Avaliação completa: O(n²)
- Avaliação de inserção: O(n)
- Avaliação de remoção: O(n)
- Avaliação de troca: O(n)

