"""
Main script for running GA on QBF instances.

Usage:
    python main_qbf.py <instance_file> [generations] [pop_size] [mutation_rate]

Example:
    python main_qbf.py instances/qbf/qbf020
    python main_qbf.py instances/qbf/qbf040 1000 100 0.01
"""

import sys
import time
from src.ga_qbf import GA_QBF

def main():
    """Main execution function."""
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main_qbf.py <instance_file> [generations] [pop_size] [mutation_rate]")
        print("\nExample:")
        print("  python main_qbf.py instances/qbf/qbf020")
        print("  python main_qbf.py instances/qbf/qbf040 1000 100 0.01")
        sys.exit(1)
    
    # Required parameter
    instance_file = sys.argv[1]
    
    # Optional parameters with defaults
    generations = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    pop_size = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    mutation_rate = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0 / 100.0
    
    # Display configuration
    print("=" * 60)
    print("Genetic Algorithm for QBF Problem")
    print("=" * 60)
    print(f"Instance:      {instance_file}")
    print(f"Generations:   {generations}")
    print(f"Pop Size:      {pop_size}")
    print(f"Mutation Rate: {mutation_rate}")
    print("=" * 60)
    print()
    
    # Run GA
    try:
        start_time = time.time()
        
        ga = GA_QBF(generations, pop_size, mutation_rate, instance_file)
        best_sol = ga.solve()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Display results
        print()
        print("=" * 60)
        print("Results")
        print("=" * 60)
        print(f"Best Solution: {best_sol}")
        print(f"Time: {total_time:.2f} seconds")
        print("=" * 60)
        
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
