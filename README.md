# Assignment 2 — Tiny Football (Arcade Mini Soccer)

## Overview
A complete Pygame implementation of a 2D arcade-style football (soccer) game featuring:
- Two teams of disk players that push a physics-based ball
- Multiple game modes with AI opponents
- Realistic physics with collision detection and momentum transfer
- Resizable window with uniform scaling
- Debug mode with visual physics predictions
- Customizable gameplay through configuration files

## Features

### 🎮 Game Modes
1. **Multiplayer (Two Humans)**: Two players compete with up to 5 players per team
2. **Human vs AI (Line-Locked)**: Player vs AI where AI maintains defensive lines
3. **Two-Player + AI Assistant**: Both players get AI teammates for assistance

### ⚽ Physics & Gameplay
- **Realistic Ball Physics**: Momentum transfer, friction, and collision detection
- **Player Movement**: Acceleration-based movement with drag
- **Goal Detection**: Sensor zones inside the pitch boundaries
- **Half-Field Restriction**: Teams are confined to their respective halves
- **120 FPS Support**: Smooth gameplay with high frame rates

### 🎨 Visual Features
- **Uniform Scaling**: Game scales properly when window is resized
- **Debug Mode**: Press 'B' to see ball trajectory predictions and physics
- **Visual Feedback**: Active player highlighting, goal celebrations
- **Responsive UI**: Starting screen and HUD scale with window size

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pygame library

### Installation
1. **Create/activate your Python virtual environment** or use the provided `myenv`:
   ```bash
   # Using provided environment (Windows)
   myenv\Scripts\activate
   
   # Or create your own
   python -m venv myenv
   myenv\Scripts\activate  # Windows
   source myenv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies**:
   ```bash
   pip install -r A2/tiny-football/requirements.txt
   ```

3. **Run the game**:
   ```bash
   python A2/tiny-football/src/main.py
   ```

### Starting the Game
1. **Main Menu**: Choose game mode (1/2/3)
2. **Configure Settings**: 
   - Adjust players per team with Left/Right arrow keys
   - Modify player acceleration and match length
3. **Start**: Press Enter or click the Start button

## Controls

### Player 1 (Left Team)
- **Movement**: W/A/S/D keys
- **Player Selection**: Tab (cycle through players) or 1-5 (direct selection)
- **Group Control**: Left Shift (all players move together)
- **Kick**: Space (when near ball)

### Player 2 (Right Team)
- **Movement**: Arrow Keys (↑↓←→)
- **Player Selection**: K (cycle through players) or 6-0 (direct selection)
- **Group Control**: Right Shift (all players move together)
- **Kick**: Enter (when near ball)

### Global Controls
- **B**: Toggle debug overlay (shows ball trajectory, player positions)
- **P**: Pause/resume game
- **R**: Reset to kickoff position
- **M**: Mute/unmute audio
- **Esc**: Quit to menu

## Configuration

### Main Config File (`A2/tiny-football/config.json`)

```json
{
  "window": { 
    "width": 960, 
    "height": 540, 
    "fps": 120 
  },
  "field": { 
    "margin": 40, 
    "wall_thickness": 8, 
    "goal_width": 80, 
    "goal_depth": 20 
  },
  "ball": { 
    "radius": 10, 
    "base_speed": 320, 
    "max_speed": 520, 
    "restitution": 0.98, 
    "friction": 0.995 
  },
  "player": { 
    "radius": 16, 
    "speed": 350, 
    "accel": 1400, 
    "min_accel": 800, 
    "max_accel": 2500, 
    "drag": 0.90 
  },
  "teams": { 
    "per_team": 2, 
    "max_per_team": 5 
  },
  "colors": { 
    "p1": "#4CAF50", 
    "p2": "#2196F3", 
    "active_glow": "#FFD54F", 
    "ball": "#FF7043", 
    "bg": "#0B4F26", 
    "lines": "#DDDDDD" 
  },
  "force_field": { 
    "enabled": false, 
    "type": "gravity", 
    "strength": 80 
  },
  "hud": { 
    "font_size": 20, 
    "show_fps": true 
  }
}
```

### Key Configuration Options

#### Window Settings
- **fps**: Game frame rate (60, 120, etc.)
- **width/height**: Default window dimensions

#### Physics Settings
- **ball.base_speed**: Initial ball speed when kicked
- **ball.max_speed**: Maximum ball velocity
- **ball.friction**: How quickly ball slows down (0.995 = very slow)
- **player.accel**: Player acceleration rate
- **player.drag**: How quickly players slow down

#### Team Settings
- **teams.per_team**: Default number of players per team
- **teams.max_per_team**: Maximum allowed players per team

#### Visual Settings
- **colors**: Customize team colors, ball color, background
- **hud.show_fps**: Display FPS counter

## Game Modes Details

### 1. Multiplayer (Two Humans)
- Both teams controlled by human players
- Up to 5 players per team
- Half-field restriction enforced
- Real-time competitive gameplay

### 2. Human vs AI (Line-Locked)
- Human controls one team, AI controls the other
- AI maintains defensive line formations
- Only the nearest AI player to the ball actively pursues
- Other AI players hold their defensive positions
- Configurable difficulty through AI parameters

### 3. Two-Player + AI Assistant
- Both human players get AI teammates
- AI assists with ball anticipation and positioning
- Balanced gameplay with human strategy and AI support

## Debug Mode Features

Press **B** during gameplay to enable debug mode:

### Visual Debug Information
- **Ball Trajectory**: Yellow line and dot showing predicted ball position
- **Player Positions**: Real-time coordinates and speed
- **Goal Boundaries**: Red rectangles showing goal collision zones
- **Pitch Outline**: Red border showing playable area
- **FPS Counter**: Real-time frame rate display

### Debug Information Display
- **Top Left**: P1 team player positions and speeds
- **Top Right**: P2 team player positions and speeds
- **Center**: Score and timer
- **Bottom**: Control instructions

## Technical Features

### Physics Engine
- **Delta Time Integration**: Frame-rate independent physics
- **Momentum Transfer**: Realistic ball-player collisions
- **Friction Simulation**: Gradual speed reduction over time
- **Boundary Collisions**: Wall bouncing with proper reflection angles

### Scaling System
- **Uniform Scaling**: Maintains aspect ratio when resizing
- **Responsive UI**: All elements scale proportionally
- **Debug Positioning**: Debug elements scale with window size

### Audio System
- **Sound Effects**: Ball bounces, goal celebrations, crowd noise
- **Configurable**: Can be disabled via config
- **Fallback**: Works without audio files

## Assets (Optional)

Place custom assets in `A2/tiny-football/assets/`:

### Graphics (`assets/gfx/`)
- **ball.png**: 64x64 centered ball sprite
- **player_p1.png**: 80x80 P1 team player sprite
- **player_p2.png**: 80x80 P2 team player sprite
- **field_960x540.png**: Custom field background
- **scoreboard.png**: Custom scoreboard graphics

### Audio (`assets/sfx/`)
- **bounce.wav**: Ball collision sound
- **goal.wav**: Goal scoring sound
- **crowd-cheering.mp3**: Crowd celebration

### Fonts (`assets/fonts/`)
- **OpenSans.ttf**: Custom font for HUD text

**Note**: Game falls back to simple shapes and system fonts if assets are missing.

## Development & Customization

### Project Structure
```
A2/tiny-football/
├── src/
│   ├── main.py           # Entry point and menu
│   ├── game.py           # Main game loop and state management
│   ├── settings.py       # Configuration management
│   ├── scaling.py        # Window scaling system
│   ├── entities/
│   │   ├── ball.py       # Ball physics and rendering
│   │   ├── player.py     # Player movement and physics
│   │   └── team.py       # Team management and input
│   ├── physics/
│   │   ├── collisions.py # Collision detection
│   │   └── force_field.py # Force field effects
│   ├── pitch.py          # Field rendering and boundaries
│   └── hud.py            # User interface and debug display
├── assets/               # Graphics, audio, fonts
├── config.json          # Game configuration
└── requirements.txt     # Python dependencies
```

### Adding New Features
1. **New Physics**: Modify `src/physics/` modules
2. **New Entities**: Add to `src/entities/`
3. **UI Changes**: Edit `src/hud.py` and `src/main.py`
4. **Configuration**: Update `config.json` and `src/settings.py`

## Performance Optimization

### Frame Rate
- **Target**: 120 FPS for smooth gameplay
- **Physics**: Delta time integration ensures consistent speed
- **Rendering**: Efficient sprite scaling and collision detection

### Memory Management
- **Asset Loading**: Sprites loaded once and cached
- **Collision Detection**: Optimized boundary checking
- **Debug Mode**: Minimal performance impact

## Troubleshooting

### Common Issues
1. **Game won't start**: Check Python version and pygame installation
2. **Poor performance**: Reduce FPS in config or close other applications
3. **Audio not working**: Check audio files in assets/sfx/ directory
4. **Window scaling issues**: Ensure uniform scaling is enabled

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: 512MB RAM minimum
- **Graphics**: Any graphics card supporting OpenGL 2.0
- **Audio**: Optional, game works without audio

## Grading Checklist

### Core Requirements ✅
- [x] **Player Entities**: Multiple controllable players per team
- [x] **Keyboard Input**: WASD + Arrow keys with player cycling
- [x] **Collisions**: Wall bounces, player-ball interactions
- [x] **Score/HUD**: Live score, FPS, debug overlay
- [x] **Two-Player**: Full multiplayer support

### Advanced Features ✅
- [x] **AI Opponents**: Line-locked AI with anticipation
- [x] **Force Fields**: Configurable gravity/wind effects
- [x] **Debug Mode**: Visual physics and trajectory prediction
- [x] **Responsive Scaling**: Window resizing with uniform scaling
- [x] **Configuration**: Extensive customization options

## License
This project is part of a Game Programming course assignment. All code is provided for educational purposes.

## Credits
- **Physics Engine**: Custom implementation using Pygame
- **Graphics**: Simple shapes with optional sprite support
- **Audio**: Basic sound effects with fallback support
- **AI**: Simple state machine with anticipation algorithms