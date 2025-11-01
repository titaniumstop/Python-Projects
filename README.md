# FPS Game - Python/Pygame

A top-down 2D first-person shooter game built with Python and Pygame.

## Features

- 🎮 Player controls with WASD movement and mouse aiming
- 🔫 Shooting mechanics with ammo system
- 👾 Infinite enemy spawning with smart AI that chases and shoots at the player
- 🗺️ Maze-like map with walls and obstacles
- 💊 Health system
- 🎯 Real-time HUD with health bar, ammo, score, and enemy count
- 🚀 Optimized performance for smooth gameplay

## Getting Started

### 1. Activate the virtual environment:
```bash
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 2. Install dependencies (already done):
```bash
pip install -r requirements.txt
```

### 3. Run the game:
```bash
# Easy way (recommended):
./run_game.sh

# Or manually:
python fps_game.py
```

## Controls

- **WASD** or **Arrow Keys** - Move player
- **Mouse** - Look around and aim
- **Left Click** - Shoot
- **R** - Reload (restores ammo to 30)
- **ESC** - Exit game

## Gameplay

- Survive as long as possible against infinite waves of enemies!
- Enemies spawn continuously from the map edges
- Avoid enemy bullets and manage your ammo carefully
- Navigate the maze to escape and fight enemies strategically
- See how high you can score

## Project Structure
- `fps_game.py` - Main game file
- `requirements.txt` - Python dependencies (pygame)
- `venv/` - Virtual environment (ignored by git)

