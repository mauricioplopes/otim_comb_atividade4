"""
Script para executar experimentos em batch com timeout de 30 minutos.
Coleta resultados parciais mesmo se o tempo limite for atingido.

COMPATÍVEL COM WINDOWS: Monitora tempo manualmente.

Usage:
    python run_experiments.py [output_dir]
"""

import sys
import os
import time
import csv
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.ga_qbf_sc import GA_QBF_SC

# Timeout global (30 minutos = 1800 segundos)
TIMEOUT_SECONDS = 1800

class TimeoutChecker:
    """Classe para verificar timeout de forma compatível com Windows."""
    
    def __init__(self, timeout_seconds):
        self.timeout_seconds = timeout_seconds
        self.start_time = None
        self.timed_out = False
        self.ga = None
        
    def start(self, ga):
        """Inicia monitoramento."""
        self.start_time = time.time()
        self.timed_out = False
        self.ga = ga
        
    def check(self):
        """Verifica se timeout foi atingido."""
        if self.start_time is None:
            return False
        elapsed = time.time() - self.start_time
        return elapsed >= self.timeout_seconds
    
    def get_elapsed(self):
        """Retorna tempo decorrido."""
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

class TimeoutGA(GA_QBF_SC):
    """GA modificado para verificar timeout periodicamente."""
    
    def __init__(self, *args, timeout_checker=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout_checker = timeout_checker
        self.generation_counter = 0
        self.best_generation = 0  # Adicionar rastreamento da melhor geração
        
    def solve(self):
        """Main GA loop com verificação de timeout."""
        # Initialize population
        population = self.initialize_population()
        
        self.best_chromosome = self.get_best_chromosome(population)
        self.best_sol = self.decode(self.best_chromosome)
        self.best_generation = 0  # Melhor solução encontrada na geração 0
        
        if self.verbose:
            print(f"(Gen. 0) BestSol = {self.best_sol}")
            print(f"         Feasible: {self.qbf_sc.is_feasible(self.best_sol)}")
        
        # Main evolutionary loop
        for g in range(1, self.generations + 1):
            self.generation_counter = g
            
            # Verificar timeout a cada 10 gerações
            if g % 10 == 0 and self.timeout_checker and self.timeout_checker.check():
                if self.verbose:
                    print(f"\n⏱ TIMEOUT atingido na geração {g}")
                break
            
            parents = self.select_parents(population)
            offsprings = self.crossover(parents)
            mutants = self.mutate(offsprings, generation=g)
            population = self.select_population(mutants)
            
            best_chromosome = self.get_best_chromosome(population)
            
            if self.fitness(best_chromosome) > self.fitness(self.best_chromosome):
                self.best_chromosome = best_chromosome
                self.best_sol = self.decode(best_chromosome)
                self.best_generation = g  # Registrar geração da melhoria
                
                if self.verbose:
                    is_feasible = self.qbf_sc.is_feasible(self.best_sol)
                    print(f"(Gen. {g}) BestSol = {self.best_sol}")
                    print(f"         Feasible: {is_feasible}")
        
        return self.best_sol

def get_instance_size(filename):
    """Lê o tamanho da instância do arquivo."""
    try:
        with open(filename, 'r') as f:
            first_line = f.readline().strip()
            return int(first_line)
    except Exception as e:
        print(f"  ERRO ao ler tamanho: {e}")
        return 0

def run_experiment_with_timeout(instance_file, config_name, generations, pop_size, 
                                mutation_rate, strategy='random', adaptive=False, seed=42):
    """Run a single experiment with timeout protection (Windows compatible)."""
    
    instance_name = Path(instance_file).name
    instance_size = get_instance_size(instance_file)
    
    print(f"\nRunning: {config_name} on {instance_name}")
    print(f"  Instance size: n={instance_size}")
    print(f"  Params: gen={generations}, pop={pop_size}, mut={mutation_rate}, "
          f"strategy={strategy}, adaptive={adaptive}")
    print(f"  Timeout: {TIMEOUT_SECONDS}s")
    
    timeout_checker = TimeoutChecker(TIMEOUT_SECONDS)
    best_sol = None
    timeout_occurred = False
    
    try:
        # Criar GA com timeout checker
        ga = TimeoutGA(
            generations, pop_size, mutation_rate, instance_file, 
            seed, population_strategy=strategy, adaptive_mutation=adaptive,
            timeout_checker=timeout_checker
        )
        ga.verbose = False
        
        # Iniciar monitoramento
        timeout_checker.start(ga)
        
        # Executar
        best_sol = ga.solve()
        
        elapsed = timeout_checker.get_elapsed()
        
        # Verificar se houve timeout
        if timeout_checker.check():
            timeout_occurred = True
            print(f"  ⏱ TIMEOUT: Resultado parcial na geração {ga.generation_counter}")
            print(f"     cost={best_sol.cost:.2f}, size={len(best_sol)}, time={elapsed:.2f}s")
        else:
            print(f"  ✓ Concluído: cost={best_sol.cost:.2f}, size={len(best_sol)}, time={elapsed:.2f}s")
        
    except Exception as e:
        elapsed = timeout_checker.get_elapsed()
        print(f"  ✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'configuracao': config_name,
            'estrategia': f"{strategy}{'+adaptive' if adaptive else ''}",
            'geracoes': generations,
            'tamanho_populacao': pop_size,
            'taxa_mutacao': mutation_rate,
            'arquivo_instancia': instance_name,
            'tamanho_instancia': instance_size,
            'custo_obtido': None,
            'tempo_execucao': elapsed,
            'tamanho_solucao': None,
            'elementos_solucao': None,
            'timeout': False,
            'erro': str(e)
        }
    
    # Verificar viabilidade
    is_feasible = ga.qbf_sc.is_feasible(best_sol) if best_sol else False
    
    # Formatar elementos da solução
    elementos = sorted(list(best_sol)) if best_sol else []
    elementos_str = ' '.join(map(str, elementos)) if elementos else ''
    
    # Construir resultado
    result = {
        'configuracao': config_name,
        'estrategia': f"{strategy}{'+adaptive' if adaptive else ''}",
        'geracoes': generations,
        'tamanho_populacao': pop_size,
        'taxa_mutacao': mutation_rate,
        'arquivo_instancia': instance_name,
        'tamanho_instancia': instance_size,
        'custo_obtido': best_sol.cost if best_sol else None,
        'tempo_execucao': elapsed,
        'tamanho_solucao': len(best_sol) if best_sol else None,
        'geracao_melhor_solucao': ga.best_generation if hasattr(ga, 'best_generation') else None,
        'elementos_solucao': elementos_str,
        'timeout': timeout_occurred,
        'feasible': is_feasible
    }
    
    return result

def save_results(results, output_dir):
    """Save results to CSV with semicolon separator."""
    output_file = os.path.join(output_dir, "resultados.csv")
    
    if not results:
        return output_file
    
    fieldnames = [
        'configuracao', 'estrategia', 'geracoes', 'tamanho_populacao', 'taxa_mutacao',
        'arquivo_instancia', 'tamanho_instancia', 'custo_obtido', 'tempo_execucao',
        'tamanho_solucao', 'geracao_melhor_solucao', 'elementos_solucao'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', extrasaction='ignore')
        writer.writeheader()
        
        for result in results:
            row = result.copy()
            if row.get('custo_obtido') is not None:
                row['custo_obtido'] = f"{row['custo_obtido']:.2f}"
            if row.get('tempo_execucao') is not None:
                row['tempo_execucao'] = f"{row['tempo_execucao']:.2f}"
            if row.get('taxa_mutacao') is not None:
                row['taxa_mutacao'] = f"{row['taxa_mutacao']:.4f}"
            
            writer.writerow(row)
    
    return output_file

def print_summary(results):
    """Print summary statistics."""
    print("\nSummary by Configuration:")
    print("-" * 80)
    
    configs = {}
    for result in results:
        config = result.get('configuracao', 'Unknown')
        if config not in configs:
            configs[config] = {
                'count': 0, 'total_cost': 0, 'total_time': 0,
                'feasible': 0, 'timeout': 0, 'valid': 0
            }
        
        configs[config]['count'] += 1
        
        if result.get('custo_obtido') is not None:
            configs[config]['total_cost'] += result['custo_obtido']
            configs[config]['valid'] += 1
        
        if result.get('tempo_execucao') is not None:
            configs[config]['total_time'] += result['tempo_execucao']
        
        if result.get('feasible', False):
            configs[config]['feasible'] += 1
        
        if result.get('timeout', False):
            configs[config]['timeout'] += 1
    
    for config, stats in sorted(configs.items()):
        n = stats['count']
        v = stats['valid']
        avg_cost = stats['total_cost'] / v if v > 0 else 0
        avg_time = stats['total_time'] / n if n > 0 else 0
        feasible_pct = (stats['feasible'] / n * 100) if n > 0 else 0
        timeout_pct = (stats['timeout'] / n * 100) if n > 0 else 0
        
        print(f"{config:15s}: n={n:2d}, avg_cost={avg_cost:8.2f}, "
              f"avg_time={avg_time:7.2f}s, feasible={feasible_pct:5.1f}%, "
              f"timeout={timeout_pct:5.1f}%")

def main():
    """Main execution function."""
    
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "results"
    os.makedirs(output_dir, exist_ok=True)
    
    instances_dir = "instances/qbf_sc"
    if not os.path.exists(instances_dir):
        print(f"Error: Directory '{instances_dir}' not found")
        sys.exit(1)
    
    instances = sorted([
        os.path.join(instances_dir, f) 
        for f in os.listdir(instances_dir) 
        if f.endswith('.txt')
    ])
    
    if not instances:
        print(f"Error: No instances found in '{instances_dir}'")
        sys.exit(1)
    
    print(f"Found {len(instances)} instances")
    print(f"Output directory: {output_dir}")
    print(f"Timeout per instance: {TIMEOUT_SECONDS}s")
    print(f"Platform: Windows (timeout manual)")
    
    configurations = [
        ("PADRAO", 10000, 100, 0.01, 'random', False),
        ("PADRAO+POP", 10000, 200, 0.01, 'random', False),
        ("PADRAO+MUT", 10000, 100, 0.05, 'random', False),
        ("PADRAO+EVOL1", 10000, 100, 0.01, 'lhc', False),
        ("PADRAO+EVOL2", 10000, 100, 0.01, 'random', True),
    ]
    
    all_results = []
    total_experiments = len(instances) * len(configurations)
    current = 0
    
    print(f"\nStarting {total_experiments} experiments...")
    print(f"Estimated max time: {total_experiments * TIMEOUT_SECONDS / 3600:.1f} hours")
    print("=" * 80)
    
    experiment_start = time.time()
    
    for instance_file in instances:
        for config_name, generations, pop_size, mutation_rate, strategy, adaptive in configurations:
            current += 1
            print(f"\n[{current}/{total_experiments}]", end=" ")
            
            result = run_experiment_with_timeout(
                instance_file, config_name, generations, pop_size, mutation_rate,
                strategy=strategy, adaptive=adaptive, seed=42
            )
            all_results.append(result)
            
            if current % 5 == 0:
                save_results(all_results, output_dir)
                print(f"\n  → Resultados salvos incrementalmente ({current}/{total_experiments})")
    
    total_time = time.time() - experiment_start
    
    output_file = save_results(all_results, output_dir)
    
    print("\n" + "=" * 80)
    print(f"All experiments completed!")
    print(f"Total time: {total_time/3600:.2f} hours")
    print(f"Results saved to: {output_file}")
    
    print_summary(all_results)
    
    print("=" * 80)

if __name__ == "__main__":
    main()
