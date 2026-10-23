# Castle Wars — Python Strategy Game

Castle Wars is a two-player strategy game developed in **Python using Pygame** as part of a university programming exam.

Players compete by managing resources, recruiting different types of units, defending their positions, and attacking their opponent's castle. The project involved implementing gameplay mechanics, a graphical interface, animations, and interactions between game entities.

## Project Status

The completed version of Castle Wars received the **highest grade in the university programming exam** for which it was developed.

Unfortunately, the final version of the code has been lost. This repository contains an earlier iteration, which may have unresolved bugs and gameplay issues.

I've chosen to share this version because it demonstrates the skills I developed while building the game, particularly in object-oriented design, event-driven programming, and game-state management.

## Gameplay and Features

Castle Wars is designed for two players sharing the same keyboard. Its features include:

- **Unit recruitment:** workers, archers, and knights with different roles.
- **Resource management:** workers collect resources from mines.
- **Castle defense:** walls, towers, and defensive structures.
- **Combat mechanics:** units attack opposing forces and structures.
- **Graphics and animation:** character movement, combat animations, and visual feedback.
- **Save/load functionality:** game progress can be saved and restored using Python's `pickle` module.
- **Graphical menus:** Pygame interface for starting and loading the game.

## Technical Implementation

**Object-oriented programming:** Classes represent game entities and organize their properties, behaviors, and interactions.

**Event-driven programming:** Keyboard and mouse events are processed through Pygame, enabling players to control characters and issue commands.

**Game logic and state management:** The implementation manages recruitment, resource collection, combat, health, building interactions, and game screens.

**Graphics and animation:** Pygame sprites and image assets are used to represent characters, buildings, and gameplay events.

**File handling:** The game uses `pickle` for saving and restoring progress.

## How to Run

1. Download or clone this repository, preserving its folder structure.
2. Install Python and Pygame:

   ```bash
   python -m pip install pygame
   ```

3. From the project directory, run:

   ```bash
   python cacace_project_castle_wars.py
   ```

Alternatively, open the project in **PyCharm**, configure an interpreter with Pygame installed, and run `cacace_project_castle_wars.py` with the working directory set to the project folder.

Keep the `assets` directory and all its subfolders alongside the Python files. Because this is an earlier iteration, some features may not work as intended.

## Controls

The game is designed for two players sharing a keyboard:

| Action | Player 1 | Player 2 |
|---|---|---|
| Move character left/right | Left Ctrl / Left Alt | Left / Right arrows |
| Recruit worker | C | B |
| Recruit archer | Z | M |
| Recruit knight | X | N |
| Send workers to mine | Q | P |
| Repair tower | W | O |
| Repair wall | E | I |
| Fire tower arrow | Space | Enter |

Additional commands and interactions are implemented; some may behave differently in this earlier version.

## Project Structure

```text
castle-wars/
├── cacace_project_castle_wars.py
├── constants_castle_wars.py
├── assets/
└── README.md
```

- `cacace_project_castle_wars.py` — main game implementation and entry point.
- `constants_castle_wars.py` — constants and configuration values.
- `assets/` — graphics, animations, and fonts.
- `README.md` — project documentation.

## Technologies and Skills

**Technologies:** Python, Pygame, PyCharm  
**Programming concepts:** Object-oriented programming, event-driven programming, game loops, state management, graphical interfaces, file handling, and debugging.

## Final Remarks

Castle Wars was one of my first opportunities to develop a larger interactive application rather than smaller, isolated programming exercises. It helped me gain experience organizing code, coordinating interactions between different components, and translating game mechanics into working Python code.

Although the final version is no longer available, this project remains an important example of my early programming experience and one I particularly enjoyed developing.

*Note: Only load `pickle` save files from trusted sources. Check redistribution rights for any third-party artwork and fonts before publishing.*
