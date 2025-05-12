"""Physics calculations for hydraulic muscle simulation."""

import numpy as np
from .constants import *

def build_springs(vertices, triangles):
    """
    Build spring elements between mesh vertices.
    
    Returns:
        list of tuples (i, j, rest_length, spring_constant)
    """
    # Create an empty set to store unique edges
    edges = set()
    
    # Add all edges from triangles
    for tri in triangles:
        for i in range(3):
            v1, v2 = tri[i], tri[(i+1)%3]
            # Ensure edge direction is consistent (low index -> high index)
            edge = (min(v1, v2), max(v1, v2))
            edges.add(edge)
    
    # Convert to a list and compute rest lengths
    springs = []
    for i, j in edges:
        rest_length = np.linalg.norm(vertices[i] - vertices[j])
        
        # Determine spring type and associated stiffness
        # Check if edge is mostly circumferential
        dz = abs(vertices[i][2] - vertices[j][2])
        
        if dz < 0.25 * RING_SPACING:  # Mostly circumferential spring
            k = ELASTIC_MODULUS * WALL_THICKNESS * RING_SPACING / rest_length
        else:  # Mostly axial spring
            k = ELASTIC_MODULUS * WALL_THICKNESS * (2 * np.pi * TUBE_RADIUS / N_CIRCUMFERENTIAL) / rest_length
        
        springs.append((i, j, rest_length, k))
    
    return springs

def compute_spring_forces(vertices, springs):
    """
    Compute spring forces for all vertices.
    
    Returns:
        forces: (N, 3) array of forces
    """
    n_vertices = vertices.shape[0]
    forces = np.zeros_like(vertices)
    
    for i, j, rest_length, k in springs:
        # Calculate displacement vector
        x_i = vertices[i]
        x_j = vertices[j]
        displacement = x_j - x_i
        
        # Calculate current length
        length = np.linalg.norm(displacement)
        if length < 1e-10:  # Avoid division by zero
            continue
            
        # Unit vector from i to j
        direction = displacement / length
        
        # Spring force magnitude (positive for extension)
        force_mag = k * (length - rest_length)
        
        # Apply forces to vertices
        force_vec = force_mag * direction
        forces[i] += force_vec
        forces[j] -= force_vec
    
    return forces

def compute_pressure_forces(vertices, triangles, pressure):
    """
    Compute forces due to internal pressure.
    
    Returns:
        forces: (N, 3) array of pressure forces
    """
    n_vertices = vertices.shape[0]
    forces = np.zeros_like(vertices)
    
    if pressure <= 0:
        return forces
    
    for tri in triangles:
        # Get triangle vertices
        v0 = vertices[tri[0]]
        v1 = vertices[tri[1]]
        v2 = vertices[tri[2]]
        
        # Calculate triangle normal and area
        normal = np.cross(v1 - v0, v2 - v0)
        area = 0.5 * np.linalg.norm(normal)
        
        if area < 1e-10:
            continue
            
        # Unit normal (pointing outward)
        normal = normal / (2 * area)
        
        # Pressure force is applied in the direction of the normal
        # Force = pressure * area * normal / 3 (divided equally among vertices)
        force = pressure * area * normal / 3
        
        # Add force to each vertex of the triangle
        forces[tri[0]] += force
        forces[tri[1]] += force
        forces[tri[2]] += force
    
    return forces

def apply_external_load(forces, end_vertices, load=EXTERNAL_LOAD):
    """Apply external tensile load to the end vertices of the muscle."""
    n_end = len(end_vertices[0])
    
    # Apply downward force to the top end
    for idx in end_vertices[1]:
        forces[idx, 2] -= load / n_end
    
    # Apply upward force to the bottom end
    for idx in end_vertices[0]:
        forces[idx, 2] += load / n_end
    
    return forces

def compute_ring_constraints(vertices, velocities, ring_indices, original_vertices):
    """
    Apply ring constraints - rings maintain original radius but can move axially.
    """
    forces = np.zeros_like(vertices)
    
    for ring in ring_indices:
        for idx in ring:
            # Original and current positions
            orig_pos = original_vertices[idx]
            curr_pos = vertices[idx]
            
            # Project back to original radius
            # Calculate displacement in xy-plane
            xy_orig = orig_pos[:2]
            xy_curr = curr_pos[:2]
            
            # Calculate original radius
            r_orig = np.linalg.norm(xy_orig)
            
            if r_orig < 1e-10:
                continue
                
            # Find current radius and direction
            r_curr = np.linalg.norm(xy_curr)
            if r_curr < 1e-10:
                continue
                
            xy_dir = xy_curr / r_curr
            
            # Constraint force to maintain radius
            k_ring = 1e7  # Very stiff spring for ring constraint
            radial_force = -k_ring * (r_curr - r_orig) * xy_dir
            
            # Add constraint force (only in x,y directions)
            forces[idx, 0] += radial_force[0]
            forces[idx, 1] += radial_force[1]
            
            # Also add velocity damping for stability in the radial direction
            damping = -200.0 * velocities[idx, :2]
            forces[idx, :2] += damping
    
    return forces 