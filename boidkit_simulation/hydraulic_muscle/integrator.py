"""Time integration for hydraulic muscle simulation."""

import numpy as np
import tqdm
import time
import logging
from .constants import *
from .physics import (
    compute_spring_forces, 
    compute_pressure_forces,
    apply_external_load,
    compute_ring_constraints
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def pressure_at_time(t):
    """Return pressure at time t based on square wave pattern."""
    cycle_position = t % PRESSURE_PERIOD
    if cycle_position < PRESSURE_ON_DURATION:
        return PRESSURE_AMPLITUDE
    else:
        return 0.0

def simulate(vertices, triangles, springs, ring_indices, end_vertices, 
            t_end=15.0, dt=DT, fps=VIDEO_FPS):
    """
    Simulate the hydraulic muscle dynamics.
    
    Args:
        vertices: Initial vertex positions
        triangles: Triangle indices
        springs: List of spring elements (i, j, rest_length, k)
        ring_indices: List of vertex indices for each ring
        end_vertices: Tuple of (start_vertices, end_vertices)
        t_end: Simulation end time
        dt: Time step
        fps: Frames per second for recording
    
    Returns:
        frames: List of vertex positions at each frame time
    """
    # Create mass array (each vertex has equal mass)
    n_vertices = vertices.shape[0]
    
    # Calculate total mass of tube
    tube_volume = np.pi * (2 * TUBE_RADIUS) * TUBE_LENGTH * WALL_THICKNESS
    total_mass = tube_volume * WALL_DENSITY
    
    # Divide mass among vertices
    mass = np.ones(n_vertices) * (total_mass / n_vertices)
    
    # Initialize state
    positions = vertices.copy()
    velocities = np.zeros_like(positions)
    original_vertices = vertices.copy()
    
    # Prepare output frames
    frame_dt = 1.0 / fps
    next_frame_time = 0.0
    frames = []
    
    # Performance tracking
    perf_log_interval = 0.5  # Log performance every 0.5 seconds
    next_perf_log = perf_log_interval
    iter_count = 0
    start_time = time.time()
    last_log_time = start_time
    
    logger.info(f"Starting simulation: {n_vertices} vertices, {len(triangles)} triangles, {len(springs)} springs")
    logger.info(f"Total simulation time: {t_end}s, dt={dt}s, expected iterations: {int(t_end/dt)}")
    
    # Main simulation loop
    t = 0.0
    pbar = tqdm.tqdm(total=int(t_end/dt), desc="Simulating")
    
    try:
        while t < t_end:
            # Compute current pressure
            pressure = pressure_at_time(t)
            
            # Compute all forces
            forces = np.zeros_like(positions)
            
            # 1. Spring forces
            spring_forces = compute_spring_forces(positions, springs)
            forces += spring_forces
            
            # 2. Pressure forces
            pressure_forces = compute_pressure_forces(positions, triangles, pressure)
            forces += pressure_forces
            
            # 3. External load
            forces = apply_external_load(forces, end_vertices)
            
            # 4. Ring constraints
            constraint_forces = compute_ring_constraints(positions, velocities, ring_indices, original_vertices)
            forces += constraint_forces
            
            # 5. Damping forces
            damping = -DAMPING_RATIO * velocities
            forces += damping
            
            # Compute accelerations (F = ma)
            accelerations = forces / mass[:, np.newaxis]
            
            # Semi-implicit Euler integration
            velocities += dt * accelerations
            positions += dt * velocities
            
            # Record frame if it's time
            if t >= next_frame_time:
                frames.append(positions.copy())
                next_frame_time += frame_dt
                
                # Calculate and log contraction percentage (every 10 frames)
                if len(frames) % 10 == 0:
                    init_length = vertices[-1, 2] - vertices[0, 2]
                    current_length = positions[-1, 2] - positions[0, 2]
                    contraction_pct = (init_length - current_length) / init_length * 100
                    logger.info(f"Frame {len(frames)}: t={t:.2f}s, contraction={contraction_pct:.2f}%")
            
            # Performance logging
            iter_count += 1
            current_time = time.time()
            if current_time - last_log_time >= perf_log_interval:
                elapsed = current_time - start_time
                iters_per_sec = iter_count / elapsed
                progress_pct = (t / t_end) * 100
                sim_time_remaining = (t_end - t) / iters_per_sec if iters_per_sec > 0 else float('inf')
                
                logger.info(f"Progress: {progress_pct:.1f}%, Sim time: {t:.3f}/{t_end}s, " +
                           f"Performance: {iters_per_sec:.1f} steps/sec, " +
                           f"ETA: {sim_time_remaining:.1f}s")
                
                last_log_time = current_time
            
            # Advance time
            t += dt
            pbar.update(1)
    
    except KeyboardInterrupt:
        logger.info(f"Simulation interrupted at t={t:.3f}s ({t/t_end*100:.1f}% complete)")
        if frames:
            logger.info(f"Collected {len(frames)} frames before interruption")
            return frames
        raise
    
    pbar.close()
    
    total_time = time.time() - start_time
    logger.info(f"Simulation completed in {total_time:.2f} seconds")
    logger.info(f"Average performance: {iter_count/total_time:.1f} iterations/sec")
    logger.info(f"Generated {len(frames)} animation frames")
    
    return frames 