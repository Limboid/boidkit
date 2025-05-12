"""Visualization for hydraulic muscle simulation."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import os
from .constants import *

def create_animation(frames, triangles, output_path, fps=VIDEO_FPS):
    """
    Create animation of the hydraulic muscle simulation.
    
    Args:
        frames: List of vertex positions at each frame
        triangles: Triangle indices
        output_path: Path to save the animation
        fps: Frames per second
    """
    # Set up figure and 3D axes
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    # Initial mesh for visualization
    init_verts = frames[0]
    
    # Prepare triangle vertices for Poly3DCollection
    triangle_vertices = []
    for tri in triangles:
        triangle_vertices.append([init_verts[tri[0]], init_verts[tri[1]], init_verts[tri[2]]])
    
    # Create the mesh collection
    mesh = Poly3DCollection(triangle_vertices, alpha=0.9, edgecolor='k', linewidth=0.2)
    mesh.set_facecolor('cyan')
    ax.add_collection3d(mesh)
    
    # Set axis limits with some padding
    max_dim = max(TUBE_LENGTH, 2 * TUBE_RADIUS)
    
    ax.set_xlim(-max_dim/2, max_dim/2)
    ax.set_ylim(-max_dim/2, max_dim/2)
    ax.set_zlim(-0.1 * max_dim, TUBE_LENGTH + 0.1 * max_dim)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Hydraulic Artificial Muscle Simulation')
    
    def update(frame_idx):
        """Update function for animation."""
        # Update mesh vertices
        new_verts = frames[frame_idx]
        
        # Rebuild triangle vertices
        new_triangle_vertices = []
        for tri in triangles:
            new_triangle_vertices.append([new_verts[tri[0]], new_verts[tri[1]], new_verts[tri[2]]])
        
        # Update the collection
        mesh.set_verts(new_triangle_vertices)
        
        # Set title with time and contraction information
        time = frame_idx / fps
        cycle = time % PRESSURE_PERIOD
        
        # Calculate contraction as percentage
        init_length = frames[0][-1, 2] - frames[0][0, 2]
        current_length = new_verts[-1, 2] - new_verts[0, 2]
        contraction_pct = (init_length - current_length) / init_length * 100
        
        ax.set_title(f'Time: {time:.2f}s, Cycle: {cycle:.2f}s, Contraction: {contraction_pct:.1f}%')
        
        return mesh,
    
    # Create the animation
    anim = FuncAnimation(
        fig, update, frames=len(frames), interval=1000/fps, blit=True)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save as mp4
    writer = FFMpegWriter(fps=fps, metadata=dict(artist='BoidKit'), bitrate=5000)
    anim.save(output_path, writer=writer)
    
    plt.close(fig)
    print(f"Animation saved to {output_path}") 