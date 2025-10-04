"""
Main script for running GA on QBF-SC instances.

Usage:
    python main_ga_qbf_sc.py <instance_file> [generations] [pop_size] [mutation_rate]

Example:
    python main_ga_qbf_sc.py instances/qbf_sc/instance-01.txt
    python main_ga_qbf_sc.py instances/qbf_sc/instance-04.txt 1000 100 0.01
"""

import sys
import time
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.ga_qbf_sc import GA_QBF_SC

def main():
    """Main execution function."""
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main_ga_qbf_sc.py <instance_file> [generations] [pop_size] [mutation_rate]")
        print("\nExample:")
        print("  python main_ga_qbf_sc.py instances/qbf_sc/instance-01.txt")
        print("  python main_ga_qbf_sc.py instances/qbf_sc/instance-04.txt 1000 100 0.01")
        sys.exit(1)
    
    # Required parameter
    instance_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(instance_file):
        print(f"Error: Instance file '{instance_file}' not found.")
        sys.exit(1)
    
    # Optional parameters with defaults
    generations = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    pop_size = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    mutation_rate = float(sys.argv[4]) if len(sys.argv) > 4 else 0.01
    
    # Display configuration
    print("=" * 70)
    print("Genetic Algorithm for QBF with Set Cover")
    print("=" * 70)
    print(f"Instance:      {instance_file}")
    print(f"Generations:   {generations}")
    print(f"Pop Size:      {pop_size}")
    print(f"Mutation Rate: {mutation_rate}")
    print("=" * 70)
    print()
    
    # Run GA
    try:
        start_time = time.time()
        
        ga = GA_QBF_SC(generations, pop_size, mutation_rate, instance_file)
        best_sol = ga.solve()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Display results
        print()
        print("=" * 70)
        print("Final Results")
        print("=" * 70)
        print(f"Best Solution: {best_sol}")
        print(f"Cost:          {best_sol.cost}")
        print(f"Size:          {len(best_sol)} variables selected")
        print(f"Feasible:      {ga.qbf_sc.is_feasible(best_sol)}")
        print(f"Time:          {total_time:.2f} seconds")
        
        # Additional statistics
        if ga.qbf_sc.is_feasible(best_sol):
            coverage = ga.qbf_sc.get_coverage_count(best_sol)
            removable = ga.qbf_sc.get_removable_variables(best_sol)
            
            print()
            print("Solution Statistics:")
            print(f"  Coverage:")
            print(f"    - Min: {min(coverage.values())}")
            print(f"    - Max: {max(coverage.values())}")
            print(f"    - Avg: {sum(coverage.values())/len(coverage):.2f}")
            print(f"  Removable variables: {len(removable)}")
        else:
            uncovered = ga.qbf_sc.get_uncovered_elements(best_sol)
            print()
            print(f"WARNING: Solution is INFEASIBLE!")
            print(f"  Uncovered elements: {len(uncovered)}")
        
        print("=" * 70)
        
    except FileNotFoundError:
        print(f"Error: Instance file '{instance_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
