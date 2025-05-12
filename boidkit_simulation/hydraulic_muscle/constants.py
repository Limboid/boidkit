"""Physical constants for hydraulic muscle simulation."""

# Geometry
TUBE_LENGTH = 0.30  # meters
TUBE_RADIUS = 0.010  # meters
RING_SPACING = 0.020  # meters
WALL_THICKNESS = 0.001  # meters

# Material properties
WALL_DENSITY = 1100  # kg/m³
ELASTIC_MODULUS = 1.0e6  # Pa (1 MPa)

# Physics
GRAVITY = 9.81  # m/s²
EXTERNAL_LOAD = 10.0  # Newtons
PRESSURE_AMPLITUDE = 1.0e6  # Pa (1 MPa)
PRESSURE_ON_DURATION = 0.5  # seconds
PRESSURE_PERIOD = 5.0  # seconds

# Simulation
DT = 1.0e-4  # seconds
DAMPING_RATIO = 0.02  # fraction of critical damping

# Mesh resolution
N_CIRCUMFERENTIAL = 24  # vertices around circumference
N_AXIAL = 60  # vertices along axis

# Visualization
VIDEO_FPS = 30 