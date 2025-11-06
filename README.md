# Spear To The Enemy

A top-down spear throwing survival/collect game built with Pygame.

## Features
- Main Menu, Options, Credits, Pause, Game Over, You Win states
- Hidden speed settings cheat (arrow / WASD sequence)
- Dynamic enemy spawning & difficulty progression
- Collectible money objects for scoring
- High score entry & persistence (`high_scores.json`)
- Responsive fullscreen scaling (F11 / Alt+Enter)
- Audio system with music & SFX and persistent volume settings (`config.json`)
- Level editor mode (`--editor` flag) groundwork

## Requirements
- Python 3.10+ (tested with 3.13)
- Pygame 2.1+


## Running
Normal game:
```powershell
python .\main.py
```
Level editor mode:
```powershell
python .\main.py --editor
```

## Controls
| Action | Key |
|--------|-----|
| Move | WASD |
| Throw spear | Left Mouse |
| Pause | ESC |
| Toggle fullscreen | F11 or Alt+Enter |

## Hidden Codes
Enter the sequence:
- Arrows: Up, Down, Up, Down, Left, Right, Left, Right
- or WASD: W, S, W, S, A, D, A, D

Unlocks player & enemy speed settings in Options.

## Project Structure
```
assets/              # Images, fonts, sfx
music/               # Music tracks
spear_game/          # Game package (states, controller, audio, sprites, ui)
levels/              # Level data files
tools/               # Utility scripts (smoke tests etc.)
```

Key files:
- `main.py` entry point
- `spear_game/controller.py` game loop & state switching
- `spear_game/game_states.py` all game states
- `spear_game/audio_manager.py` sound & music
- `high_scores.json` persistent scores

## Saving & Scores
When game ends you can enter a name to save score. Highest score displayed during play.

## Building (Optional)
You can create a standalone executable via PyInstaller:
```powershell
python -m pip install pyinstaller
pyinstaller --onefile --add-data "assets;assets" --add-data "music;music" main.py
```
Adjust --add-data pairs for your OS if needed.

## Contributing
PRs & issues welcome. Please keep code PEP8 and avoid large unreviewed assets.


## Roadmap Ideas
- Boss fight state
- Particle effects & hit feedback
- More enemy variety & behaviors
- Level editor completion
- Achievement system

## Troubleshooting
| Issue | Fix |
|-------|-----|
| Audio warnings | Ensure files exist under `assets/sfx` & `music` |
| Scaling looks off | Toggle fullscreen off/on (F11) |
| Font fallback warning | Confirm `assets/zelda_font.ttf` present |

Enjoy throwing spears! 🗡️
