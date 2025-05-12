import os
import sys
from simulation import run_simulation, create_animation

def main():
    print("Starting hydraulic artificial muscle simulation...")
    
    # Run simulation for 25 seconds to show 5 complete cycles
    simulation_data = run_simulation(duration=25.0, dt=0.01)
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Create and save animation
    output_file = os.path.join("output", "hydraulic_muscle_simulation.mp4")
    animation = create_animation(simulation_data, filename=output_file, fps=30)
    
    print(f"Simulation complete. Video saved to {output_file}")
    
if __name__ == "__main__":
    main() 