# Hydraulic Artificial Muscle Simulation

This project simulates a hydraulic artificial muscle expanding and contracting from 1MPa impulses of hydraulic pressure applied in a square wave pattern. The simulation models:

- 1MPa pressure impulses in a square wave pattern
- Each impulse lasts 500ms
- Impulses occur every 5 seconds
- The muscle is under a constant 10N load

## Requirements

- Python 3.6+
- NumPy
- Matplotlib
- SciPy
- FFmpeg (for video generation)

## Installation

1. Install required Python packages:
```
pip install numpy matplotlib scipy
```

2. Install FFmpeg: 
   - On macOS: `brew install ffmpeg`
   - On Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - On Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)

## Usage

Run the simulation:
```
python main.py
```

The simulation will generate a video file in the `output` directory showing the muscle's expansion and contraction.

## Physics Model

The simulation includes:
- Elastic forces (Young's modulus)
- Damping forces
- Hydraulic pressure forces
- Constant load forces
- Volume conservation (muscle gets thinner as it extends)

## Output

The video shows:
- Visual representation of the muscle expanding and contracting
- Real-time pressure values
- Muscle length changes
- Strain measurements over time 