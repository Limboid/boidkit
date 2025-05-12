"""Entry point for boidkit_simulation package."""

import sys
import logging
from boidkit_simulation.hydraulic_muscle.driver import run_simulation, main

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

if __name__ == "__main__":
    # If run as a module with args, pass to main
    if len(sys.argv) > 1:
        main()
    else:
        # Default to a quick simulation for testing
        print("Running quick simulation with default parameters...")
        print("For options, run: python -m boidkit_simulation --help")
        run_simulation(duration=5.0, reduced_mesh=True) 