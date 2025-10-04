# Algoritmo Genético para MAX-QBF com Set Cover

Implementação de um Algoritmo Genético (GA) para resolver o problema de maximização de uma Função Binária Quadrática com restrições de cobertura de conjuntos (MAX-SC-QBF).

## 📋 Sobre o Projeto

Este projeto foi desenvolvido como parte da **Atividade 4** da disciplina MO824/MC859 - Tópicos em Otimização Combinatória (2º semestre de 2025) na Unicamp.

### Problema MAX-SC-QBF

O MAX-SC-QBF combina dois problemas clássicos:

1. **Maximização de QBF**: Maximizar `f(x) = x' · A · x` onde `x` é um vetor binário e `A` é uma matriz de coeficientes
2. **Set Cover**: Garantir que todos os elementos do universo `N = {1, ..., n}` sejam cobertos por pelo menos um conjunto selecionado

**Formulação**:
- Variáveis de decisão: `x₁, x₂, ..., xₙ` (binárias)
- Objetivo: Maximizar `f(x) = Σᵢ Σⱼ aᵢⱼ · xᵢ · xⱼ`
- Restrição: Para todo `k ∈ N`, existe ao menos um `Sᵢ` tal que `k ∈ Sᵢ` e `xᵢ = 1`

## 🚀 Características

### Algoritmo Genético Base (PADRÃO)
- **Codificação**: Cromossomos binários (cada bit representa uma variável)
- **População inicial**: Geração aleatória com reparo para factibilidade
- **Seleção**: Torneio binário
- **Crossover**: 2-pontos
- **Mutação**: Bit-flip com reparo automático
- **Elitismo**: Melhor solução sempre preservada

### Estratégias Evolutivas Alternativas

1. **Latin Hypercube Sampling (LHC)** - EVOL1
   - Inicialização da população usando amostragem LHC
   - Garante melhor cobertura do espaço de soluções
   - Cada estrato é amostrado exatamente uma vez

2. **Adaptive Mutation** - EVOL2
   - Taxa de mutação adaptativa que decai ao longo das gerações
   - Início: alta exploração (taxa = 0.1)
   - Fim: refinamento (taxa = 0.001)
   - Decaimento linear

## 📁 Estrutura do Projeto

```
.
├── src/
│   ├── __init__.py
│   ├── solution.py           # Classe Solution
│   ├── evaluator.py          # Interface abstrata Evaluator
│   ├── qbf.py                # Implementação QBF
│   ├── qbf_inverse.py        # QBF inverso (minimização)
│   ├── qbf_sc.py             # QBF com Set Cover (maximização)
│   ├── abstract_ga.py        # Framework abstrato do GA
│   ├── ga_qbf.py             # GA para QBF simples
│   └── ga_qbf_sc.py          # GA para QBF-SC (★ principal)
├── instances/
│   └── qbf_sc/
│       ├── instance-01.txt   # n=25
│       ├── instance-04.txt   # n=50
│       ├── instance-07.txt   # n=100
│       └── ...               # 15 instâncias no total
├── main_ga_qbf_sc.py         # Script principal
├── run_experiments.py        # Execução de experimentos
└── README.md
```

## 🛠️ Instalação

### Requisitos
- Python 3.8 ou superior
- Nenhuma dependência externa (usa apenas biblioteca padrão)

### Setup

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/ga-qbf-setcover.git
cd ga-qbf-setcover

# Não é necessário instalar dependências
# O projeto usa apenas bibliotecas padrão do Python
```

## 🎮 Uso

### Execução Simples

```bash
python main_ga_qbf_sc.py <arquivo_instancia> [geracoes] [tam_pop] [taxa_mutacao]
```

**Exemplo**:
```bash
# Executar com parâmetros padrão
python main_ga_qbf_sc.py instances/qbf_sc/instance-01.txt

# Executar com parâmetros customizados
python main_ga_qbf_sc.py instances/qbf_sc/instance-01.txt 1000 100 0.01
```

### Execução de Experimentos Completos

```bash
python run_experiments.py
```

Este script executa automaticamente todas as 75 configurações:
- 15 instâncias × 5 configurações = 75 experimentos
- Configurações: PADRÃO, PADRÃO+POP, PADRÃO+MUT, PADRÃO+EVOL1, PADRÃO+EVOL2
- Resultados salvos em `results/`

## 📊 Configurações de Experimentos

| Config | População | Mutação | Estratégia | Descrição |
|--------|-----------|---------|------------|-----------|
| **PADRÃO** | 100 | 0.01 | Random | Configuração baseline |
| **PADRÃO+POP** | 300 | 0.01 | Random | População maior |
| **PADRÃO+MUT** | 100 | 0.05 | Random | Mutação maior |
| **PADRÃO+EVOL1** | 100 | 0.01 | LHC | Latin Hypercube |
| **PADRÃO+EVOL2** | 100 | adaptive | Random | Mutação adaptativa |

## 📝 Formato das Instâncias

```
<n>                           # Número de variáveis
<s1> <s2> ... <sn>           # Tamanhos dos conjuntos (opcional)
<elementos de S1>            # Elementos cobertos pelo conjunto 1
<elementos de S2>            # Elementos cobertos pelo conjunto 2
...
<elementos de Sn>            # Elementos cobertos pelo conjunto n
<a11> <a12> ... <a1n>        # Matriz A (triangular superior)
<a22> <a23> ... <a2n>
...
<ann>
```

**Exemplo** (n=5):
```
5
2 3 2 2 2
1 2
2 3 4
1 4
3 5
4 5
3 1 -2 0 3
-1 2 1 -1
2 -2 4
0 5
3
```

## 🔍 Detalhes de Implementação

### Manutenção de Factibilidade

Todas as operações genéticas mantêm a factibilidade das soluções:

1. **Inicialização**: Soluções reparadas após geração aleatória
2. **Crossover**: Offspring reparados se necessário
3. **Mutação**: Reparo aplicado quando bit desligado viola cobertura

### Função de Reparo

A função `repair_chromosome()` usa abordagem greedy:
- Identifica elementos não cobertos
- Adiciona variáveis que cobrem o máximo de elementos faltantes
- Continua até cobertura completa

### Função Fitness

```python
fitness(chromosome) = {
    f(x)                      se solução factível
    f(x) - |uncovered| × 10000  se solução infactível
}
```

A penalização alta garante que soluções infactíveis sejam evitadas.


## 📚 Referências

1. **Reeves, C. R.** (2010). *Genetic Algorithms*. In: Gendreau, M., Potvin, J.Y. (eds) Handbook of Metaheuristics. International Series in Operations Research & Management Science, vol 146. Springer. DOI: 10.1007/978-1-4419-1665-5_10

2. **Kochenberger, G. et al.** (2014). *The unconstrained binary quadratic programming problem: a survey*. Journal of Combinatorial Optimization, 28:58-81. DOI: 10.1007/s10878-014-9734-0

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos como parte da disciplina MO824/MC859.

