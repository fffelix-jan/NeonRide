# NeonRide
NeonRide is a Python/Pygame port of the Scratch game "Neon Ride" by Greenyman. The goal of this project is a faithful recreation, including the original pen-based drawing, physics feel, and collision behavior.

The original game can be found here: https://scratch.mit.edu/projects/30133706/

## Overview
- Direct Scratch-to-Python port with custom pen rendering and collision detection.
- Tunable movement and gravity constants.
- Current content includes levels 1-2.

## What's done
* Physics engine
* Levels 1-2

## What still needs to be done
* Remaining levels
* Instructions screen
* Emergency screen
* Testing
* Windows build script

## Controls
- Left/Right Arrow: Move
- Up Arrow: Jump
- R: Respawn
- Q (hold): Return to menu
- T: Toggle grid size (debug)

## How to Play
Select "play" from the main menu. Navigate the neon platforms to reach the goal (green). Lava (red) resets your position. Hold Q to return to the menu.

## Run from Source
1. Install Python 3.10+.
2. Install dependencies (also includes Pyinstaller for building):

```bash
python3 -m pip install -r requirements.txt
```

3. Run the game:

```bash
python3 main.py
```

## Building

### Windows
An automated build script has not been written yet.

### macOS
The macOS build uses PyInstaller.

1. Install PyInstaller:

```bash
python3 -m pip install pyinstaller
```

2. Build:

```bash
./build_macos.sh
```

3. Output app bundle:

```
dist/Neon Ride.app
```

## Credits
- Original Scratch game: Greenyman
- Python/Pygame port: Felix