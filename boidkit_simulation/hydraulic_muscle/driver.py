"""Driver script for hydraulic muscle simulation."""

import os
import argparse
import time
import logging
from .mesh import generate_cylinder
from .physics import build_springs
from .integrator import simulate
from .render import create_animation
from .constants import *

logger = logging.getLogger(__name__)

def run_simulation(duration=5.0, fps=VIDEO_FPS, output_path=None, reduced_mesh=False):
    """
    Run the complete hydraulic muscle simulation.
    
    Args:
        duration: Simulation duration in seconds
        fps: Frames per second for the output video
        output_path: Path to save the video (default: output/hydraulic_muscle.mp4)
        reduced_mesh: Use a lower resolution mesh for faster testing
    """
    if output_path is None:
        output_path = os.path.join('output', 'hydraulic_muscle.mp4')
    
    logger.info("Generating mesh...")
    
    # Use a reduced resolution mesh for quick testing if requested
    if reduced_mesh:
        n_circ = 12  # half the default circumferential resolution
        n_axial = 30  # half the default axial resolution
        logger.info(f"Using reduced mesh resolution: {n_circ}x{n_axial}")
        vertices, triangles, ring_indices, end_vertices = generate_cylinder(n_circ=n_circ, n_axial=n_axial)
    else:
        vertices, triangles, ring_indices, end_vertices = generate_cylinder()
    
    logger.info(f"Created mesh with {vertices.shape[0]} vertices and {len(triangles)} triangles")
    
    logger.info("Building springs...")
    start_time = time.time()
    springs = build_springs(vertices, triangles)
    logger.info(f"Built {len(springs)} springs in {time.time() - start_time:.2f} seconds")
    
    logger.info(f"Simulating for {duration} seconds...")
    start_time = time.time()
    frames = simulate(vertices, triangles, springs, ring_indices, end_vertices, 
                     t_end=duration, fps=fps)
    sim_time = time.time() - start_time
    logger.info(f"Simulation completed in {sim_time:.2f} seconds (avg {sim_time/duration:.1f}x slower than real-time)")
    
    if frames:
        logger.info(f"Rendering animation to {output_path}...")
        create_animation(frames, triangles, output_path, fps)
        logger.info(f"Video saved to {output_path}")
    else:
        logger.warning("No frames were collected, animation cannot be created")
    
def main():
    parser = argparse.ArgumentParser(description="Hydraulic Artificial Muscle Simulation")
    parser.add_argument('--duration', type=float, default=5.0, help='Simulation duration in seconds')
    parser.add_argument('--fps', type=int, default=VIDEO_FPS, help='Frames per second')
    parser.add_argument('--output', type=str, default=None, help='Output video path')
    parser.add_argument('--fast', action='store_true', help='Use reduced resolution for faster testing')
    
    args = parser.parse_args()
    run_simulation(args.duration, args.fps, args.output, reduced_mesh=args.fast)

if __name__ == "__main__":
    main() 