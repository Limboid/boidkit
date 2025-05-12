"""Mesh generation for hydraulic muscle simulation."""

import numpy as np
from .constants import *

def generate_cylinder(n_circ=N_CIRCUMFERENTIAL, n_axial=N_AXIAL, 
                     length=TUBE_LENGTH, radius=TUBE_RADIUS):
    """
    Generate a cylindrical mesh with rings at regular intervals.
    
    Returns:
        vertices: (N, 3) array of vertex positions
        triangles: (M, 3) array of triangle indices
        ring_vertex_indices: list of indices for vertices that are part of rings
        end_vertices: indices of vertices at the ends of the tube
    """
    # Create vertices
    n_vertices = n_circ * n_axial
    vertices = np.zeros((n_vertices, 3))
    
    # Place vertices in a cylinder
    for i in range(n_axial):
        z = length * i / (n_axial - 1)
        for j in range(n_circ):
            theta = 2 * np.pi * j / n_circ
            idx = i * n_circ + j
            vertices[idx, 0] = radius * np.cos(theta)
            vertices[idx, 1] = radius * np.sin(theta)
            vertices[idx, 2] = z
    
    # Create triangles (two per quad)
    n_triangles = 2 * n_circ * (n_axial - 1)
    triangles = np.zeros((n_triangles, 3), dtype=np.int32)
    
    t = 0
    for i in range(n_axial - 1):
        for j in range(n_circ):
            j_next = (j + 1) % n_circ
            
            v00 = i * n_circ + j
            v01 = i * n_circ + j_next
            v10 = (i + 1) * n_circ + j
            v11 = (i + 1) * n_circ + j_next
            
            # First triangle
            triangles[t, 0] = v00
            triangles[t, 1] = v10
            triangles[t, 2] = v01
            t += 1
            
            # Second triangle
            triangles[t, 0] = v01
            triangles[t, 1] = v10
            triangles[t, 2] = v11
            t += 1
    
    # Identify ring vertices
    n_rings = int(length / RING_SPACING) + 1
    ring_indices = []
    
    for ring in range(n_rings):
        # Find the closest z-position where we want a ring
        z_target = ring * RING_SPACING
        i_closest = int(round(z_target * (n_axial - 1) / length))
        
        # Store all vertices at this axial position
        ring_verts = [i_closest * n_circ + j for j in range(n_circ)]
        ring_indices.append(ring_verts)
    
    # Identify end vertices
    start_vertices = [j for j in range(n_circ)]
    end_vertices = [(n_axial - 1) * n_circ + j for j in range(n_circ)]
    
    return vertices, triangles, ring_indices, (start_vertices, end_vertices) 