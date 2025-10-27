# Dream League Soccer 2030

## Members - Group 6
| **Student name** | **Student ID** |
|-----|--------|
| Nguyễn Ngọc Khôi | 2252378 |
| Nguyễn Quang Phú | 2252621 |
| Nguyễn Tấn Bảo Lễ | 2252428 |
| Nguyễn Minh Khôi | 2252377 |


## Concept
Top-down arcade mini-soccer with two teams of disk players knocking a physics ball to score in left/right goals. Ball bounces off walls and players. Two-player local controls, optional force-field (wind/gravity), and a debug overlay.

## Controls
- Player 1: W/A/S/D to move, Tab to cycle active, Left Shift to group move, Space to kick
- Player 2: Arrow Keys to move, K to cycle active, Right Shift to group move, Enter to kick
- B: Toggle debug overlay (bounding, velocities, stats)
- P: Pause, R: Reset kickoff, Esc: Quit

## Run guide
### Install dependencies from requirements.txt
```bash
cd A2/tiny-football
make install
```

### Run the game
```bash
make run
```

## Requirements
- Python 3.12+
- Install dependencies: `pip install -r requirements.txt`

## Configuration
- Edit `config.json` to tweak window size, ball speed/friction, players per team, colors, and force field.
- Modes: set `"mode"` to `"multiplayer"`, `"human_vs_ai"`, or `"two_plus_ai"`.
- Team sizes: set `"teams": { "per_team": N, "max_per_team": 5 }`.
- Example enables wind:
```json
{
  "force_field": { "enabled": true, "type": "wind", "strength": 80 }
}
```

## Notes
- Stable 120 FPS target; ball stays within the visible pitch and goals are sensor zones.
- HUD shows score, hits, FPS, and hints; debug shows per-entity position/velocity vectors.

## Game modes
- Multiplayer: both humans control separate teams; up to 5 players per team. Each stays on its half.
- Human vs AI: choose 1–3 players per team. AI players are line-locked vertically; only the nearest AI to the ball actively anticipates; others remain fixed on their lines.
- Two-Player + AI assistant: both humans plus one AI per team that anticipates.

## Assets

### Graphics
- **Player Sprites:** Custom pixel art (created for this project)
- **Ball Sprite:** `ball.png` - Custom design
- **Field Image:** `field_960x540.png` - Custom rendered grass texture
- **Menu Background:** `start_bg.jpg` - Royalty-free stadium image

### Audio
- **Goal Sound:** "Football Hits Net" by Unknown (Freesound.org)
- **Bounce Sound:** `bounce.wav` - Synthesized impact sound
- **Crowd Cheering:** "Crowd Cheering" by Freesound user (CC0 License)
- **Background Music:** "Football Crowd Ambience" (Royalty-free)

### Fonts
- System font (SysFont None) - Default monospace for stats
- PyGame built-in rendering


