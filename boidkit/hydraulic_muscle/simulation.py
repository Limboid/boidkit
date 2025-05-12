import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle
import os

class HydraulicMuscle:
    def __init__(self, initial_length=0.15, cross_section=0.002, elastic_modulus=1e6, 
                 damping=50, load=10, max_pressure=1e6, num_rings=6):
        """
        Initialize hydraulic artificial muscle as a flexible tube with inelastic rings
        
        Parameters:
        - initial_length: Initial length of the muscle in meters
        - cross_section: Cross-sectional area in m²
        - elastic_modulus: Young's modulus in Pa
        - damping: Damping coefficient
        - load: Constant load in Newtons
        - max_pressure: Maximum pressure in Pa (1MPa = 1e6 Pa)
        - num_rings: Number of constraining rings
        """
        self.rest_length = initial_length
        self.length = initial_length
        self.cross_section = cross_section
        self.elastic_modulus = elastic_modulus
        self.damping = damping
        self.load = load
        self.max_pressure = max_pressure
        self.pressure = 0
        self.velocity = 0
        self.strain = 0
        self.time = 0
        
        # Time between pressure pulses (5 seconds)
        self.pulse_interval = 5.0
        # Duration of each pulse (500ms)
        self.pulse_duration = 0.5
        
        # Ring configuration
        self.num_rings = num_rings
        self.ring_positions = np.linspace(0, 1, num_rings)  # Normalized positions
        
        # Dimension changes for visualization
        self.base_width = 0.03
        self.width = self.base_width
        self.segment_widths = np.ones(num_rings-1) * self.base_width
        self.segment_lengths = np.ones(num_rings-1) * (initial_length / (num_rings-1))
        self.total_volume = initial_length * cross_section
    
    def update_pressure(self, t):
        """Update pressure based on square wave pattern"""
        cycle_time = t % self.pulse_interval
        if cycle_time < self.pulse_duration:
            self.pressure = self.max_pressure
        else:
            self.pressure = 0
            
    def calculate_forces(self):
        """Calculate all forces acting on the muscle"""
        # Elastic force (spring)
        elastic_force = self.elastic_modulus * self.cross_section * (self.length - self.rest_length) / self.rest_length
        
        # Damping force
        damping_force = self.damping * self.velocity
        
        # Pressure force (causes bulging and shortening)
        contraction_factor = 0.8  # Maximum contraction at full pressure
        pressure_normalized = self.pressure / self.max_pressure
        # Pressure causes contraction (negative force)
        pressure_force = -self.pressure * self.cross_section * contraction_factor * pressure_normalized
        
        # Load force (constant tension)
        load_force = self.load
        
        # Net force: positive means extension, negative means contraction
        net_force = load_force + pressure_force + elastic_force + damping_force
        
        return net_force
    
    def update_segment_geometry(self):
        """Update the geometry of each segment between rings"""
        # Calculate bulge based on pressure
        pressure_ratio = self.pressure / self.max_pressure
        
        # Calculate segment lengths and widths based on volume conservation
        # When pressure increases, segments bulge out (width increases) and overall length decreases
        segment_length_ratio = 1.0 - 0.3 * pressure_ratio  # Segments shorten with pressure
        
        # Update segment lengths
        base_segment_length = self.rest_length / (self.num_rings - 1)
        self.segment_lengths = np.ones(self.num_rings-1) * base_segment_length * segment_length_ratio
        
        # Calculate new total length
        self.length = np.sum(self.segment_lengths)
        
        # Calculate segment widths based on volume conservation
        segment_volume = self.total_volume / (self.num_rings - 1)
        for i in range(self.num_rings - 1):
            # Volume = π * r² * length, solving for r and converting to width (diameter)
            self.segment_widths[i] = np.sqrt(segment_volume / (np.pi * self.segment_lengths[i])) * 2
    
    def update(self, dt):
        """Update muscle state for one time step"""
        self.time += dt
        old_pressure = self.pressure
        self.update_pressure(self.time)
        
        # If pressure changed, update geometry
        if old_pressure != self.pressure:
            self.update_segment_geometry()
        
        # Calculate acceleration using F=ma
        mass = 0.5  # kg, simplified
        
        net_force = self.calculate_forces()
        acceleration = net_force / mass
        
        # Update velocity and position using semi-implicit Euler integration
        self.velocity += acceleration * dt
        old_length = self.length
        
        # Length is primarily determined by segment geometry, but can be slightly adjusted by forces
        length_adjustment = self.velocity * dt
        self.length += length_adjustment
        
        # Update segment lengths proportionally
        if old_length > 0:
            self.segment_lengths *= (self.length / old_length)
        
        # Ensure the muscle doesn't collapse or over-extend
        min_length = self.rest_length * 0.6
        max_length = self.rest_length * 1.1
        
        if self.length < min_length:
            scale_factor = min_length / self.length
            self.length = min_length
            self.segment_lengths *= scale_factor
            self.velocity = 0
        elif self.length > max_length:
            scale_factor = max_length / self.length
            self.length = max_length
            self.segment_lengths *= scale_factor
            self.velocity = 0
            
        # Calculate strain
        self.strain = (self.length - self.rest_length) / self.rest_length
        
        # Update segment widths based on volume conservation
        segment_volume = self.total_volume / (self.num_rings - 1)
        for i in range(self.num_rings - 1):
            # Ensure segments maintain their volume
            self.segment_widths[i] = np.sqrt(segment_volume / (np.pi * self.segment_lengths[i])) * 2
        
        # Update overall width (max width for visualization)
        self.width = np.max(self.segment_widths)
        
        return {
            'time': self.time,
            'length': self.length,
            'pressure': self.pressure,
            'strain': self.strain,
            'velocity': self.velocity,
            'width': self.width,
            'segment_lengths': self.segment_lengths.copy(),
            'segment_widths': self.segment_widths.copy()
        }


def run_simulation(duration=20.0, dt=0.01):
    """Run the muscle simulation for the specified duration"""
    # Initialize muscle
    muscle = HydraulicMuscle()
    
    # Time steps
    n_steps = int(duration / dt)
    
    # Data storage
    time_data = np.zeros(n_steps)
    length_data = np.zeros(n_steps)
    pressure_data = np.zeros(n_steps)
    strain_data = np.zeros(n_steps)
    width_data = np.zeros(n_steps)
    
    # Store segment data for every 10th timestep (to save memory)
    segment_data_interval = 10
    segments_data = []
    
    # Run simulation
    for i in range(n_steps):
        data = muscle.update(dt)
        
        # Store data
        time_data[i] = data['time']
        length_data[i] = data['length']
        pressure_data[i] = data['pressure'] / 1e6  # Convert to MPa for display
        strain_data[i] = data['strain']
        width_data[i] = data['width']
        
        # Store segment data at intervals
        if i % segment_data_interval == 0:
            segments_data.append({
                'time': data['time'],
                'segment_lengths': data['segment_lengths'],
                'segment_widths': data['segment_widths']
            })
    
    return {
        'time': time_data,
        'length': length_data,
        'pressure': pressure_data,
        'strain': strain_data,
        'width': width_data,
        'segments': segments_data,
        'segment_interval': segment_data_interval * dt
    }


def create_animation(sim_data, filename='muscle_simulation.mp4', fps=30):
    """Create an animation of the muscle simulation with rings and bulging segments"""
    # Calculate actual number of frames needed for smooth animation
    duration = sim_data['time'][-1]
    n_frames = int(duration * fps)
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})
    fig.tight_layout(pad=4)
    
    # Setup the muscle visualization subplot
    ax1.set_xlim(-0.05, 0.25)
    ax1.set_ylim(-0.1, 0.1)
    ax1.set_aspect('equal')
    ax1.set_title('Hydraulic Artificial Muscle with Bulging Segments')
    ax1.set_xlabel('Position (m)')
    ax1.set_ylabel('Width (m)')
    
    # Fixed left anchor point
    anchor_left = plt.Circle((-0.01, 0), 0.01, fc='gray')
    ax1.add_patch(anchor_left)
    
    # Moving right anchor point
    anchor_right = plt.Circle((0.15, 0), 0.01, fc='gray')
    ax1.add_patch(anchor_right)
    
    # Get number of rings from the first segment data
    num_rings = len(sim_data['segments'][0]['segment_lengths']) + 1
    
    # Muscle segments
    segments = []
    for i in range(num_rings - 1):
        segment = Rectangle((0, 0), 0.02, 0.03, fc='blue', alpha=0.7)
        ax1.add_patch(segment)
        segments.append(segment)
    
    # Rings
    rings = []
    for i in range(num_rings):
        ring = Circle((0, 0), 0.005, fc='black')
        ax1.add_patch(ring)
        rings.append(ring)
    
    # Mass (load) representation
    load = Rectangle((0.15, -0.025), 0.02, 0.05, fc='brown')
    ax1.add_patch(load)
    
    # Text annotations
    time_text = ax1.text(0.02, 0.06, '', transform=ax1.transAxes)
    length_text = ax1.text(0.02, 0.01, '', transform=ax1.transAxes)
    pressure_text = ax1.text(0.7, 0.06, '', transform=ax1.transAxes)
    
    # Setup the time plot subplot
    ax2.set_xlim(0, duration)
    ax2.set_ylim(-0.1, 1.1)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Pressure (MPa) / Strain')
    
    # Two lines: one for pressure, one for strain
    pressure_line, = ax2.plot([], [], 'r-', label='Pressure (MPa)')
    strain_line, = ax2.plot([], [], 'b-', label='Normalized Strain')
    ax2.legend(loc='upper right')
    
    # Setup the time indicator
    time_indicator = ax2.axvline(x=0, color='k', linestyle='--')
    
    # Interpolation function for segment data
    from scipy.interpolate import interp1d
    
    # Segment data is stored at intervals
    segment_times = np.array([data['time'] for data in sim_data['segments']])
    
    # Function to initialize the animation
    def init():
        # Initial segment positions
        for i in range(num_rings - 1):
            segments[i].set_width(0.02)
            segments[i].set_height(0.03)
            segments[i].set_xy((i * 0.02, -0.015))
        
        # Initial ring positions
        for i in range(num_rings):
            rings[i].set_center((i * 0.02, 0))
        
        # Initial load position
        load.set_x(sim_data['length'][0])
        
        # Clear text and plots
        time_text.set_text('')
        length_text.set_text('')
        pressure_text.set_text('')
        pressure_line.set_data([], [])
        strain_line.set_data([], [])
        time_indicator.set_xdata([0])
        
        return [*segments, *rings, load, time_text, length_text, pressure_text, pressure_line, strain_line, time_indicator]
    
    # Interpolate data to match frame rate
    t_sim = sim_data['time']
    # Make sure t_frames starts from the minimum time in t_sim
    t_frames = np.linspace(t_sim[0], duration, n_frames)
    
    length_interp = interp1d(t_sim, sim_data['length'])(t_frames)
    pressure_interp = interp1d(t_sim, sim_data['pressure'])(t_frames)
    strain_interp = interp1d(t_sim, sim_data['strain'])(t_frames)
    
    # Normalize strain for plotting
    min_strain = np.min(strain_interp)
    max_strain = np.max(strain_interp)
    if max_strain == min_strain:
        strain_norm = np.zeros_like(strain_interp)
    else:
        strain_norm = (strain_interp - min_strain) / (max_strain - min_strain)
    
    # Function to update the animation
    def update(frame):
        t = t_frames[frame]
        idx = frame
        
        # Find closest segment data
        segment_idx = np.argmin(np.abs(segment_times - t))
        segment_data = sim_data['segments'][segment_idx]
        
        # Current total length
        length = length_interp[idx]
        
        # Position tracker for segments
        pos_x = 0
        
        # Update each segment and ring
        for i in range(num_rings - 1):
            seg_length = segment_data['segment_lengths'][i]
            seg_width = segment_data['segment_widths'][i]
            
            # Position the segment
            segments[i].set_xy((pos_x, -seg_width/2))
            segments[i].set_width(seg_length)
            segments[i].set_height(seg_width)
            
            # Position the left ring
            rings[i].set_center((pos_x, 0))
            
            # Move position tracker
            pos_x += seg_length
        
        # Position the last ring
        rings[-1].set_center((pos_x, 0))
        
        # Update load position
        load.set_x(pos_x)
        
        # Update text annotations
        time_text.set_text(f'Time: {t:.2f}s')
        length_text.set_text(f'Length: {length*100:.1f}cm')
        pressure_text.set_text(f'Pressure: {pressure_interp[idx]:.2f}MPa')
        
        # Update plots
        pressure_line.set_data(t_sim[t_sim <= t], sim_data['pressure'][t_sim <= t])
        
        # Safe normalization for strain plot
        strain_data = sim_data['strain'][t_sim <= t]
        if len(strain_data) > 0:
            min_strain = np.min(strain_data)
            max_strain = np.max(strain_data)
            if max_strain == min_strain:
                norm_strain = np.zeros_like(strain_data)
            else:
                norm_strain = (strain_data - min_strain) / (max_strain - min_strain)
            strain_line.set_data(t_sim[t_sim <= t], norm_strain)
        
        # Update time indicator
        time_indicator.set_xdata([t])
        
        return [*segments, *rings, load, time_text, length_text, pressure_text, pressure_line, strain_line, time_indicator]
    
    # Create animation
    ani = animation.FuncAnimation(fig, update, frames=n_frames, init_func=init, 
                                 blit=True, interval=1000/fps)
    
    # Save animation as MP4
    writer = animation.FFMpegWriter(fps=fps, metadata=dict(artist='HydraulicMuscleSimulation'), 
                                   bitrate=5000)
    ani.save(filename, writer=writer)
    
    print(f"Animation saved to {filename}")
    return ani 