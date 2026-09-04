# Infection Escape

A polished 2D survival shooter game built in Python using the **Pygame** engine. 

You are trapped in an infected city sector. Zombies roam the streets, chasing you and any survivors they can spot. Your mission: survive the onslaught across 10 waves, rescue civilian survivors by bringing them to the green Safe Zone, gather critical drops, and reach the escape landing pad when it is activated!

---

## 🎮 How to Play

### Controls
* **Movement**: `W` `A` `S` `D` (or Arrow Keys)
* **Sprint**: Hold `Left Shift` or `Right Shift` (costs Stamina)
* **Aim**: Move the Mouse cursor (direction indicator follows)
* **Shoot**: `Left Click`
* **Reload**: `R`
* **Pause / Resume**: `P` or `Escape`
* **Restart Game (on Game Over / Victory)**: `R`
* **Exit to Menu (on Pause / Game Over / Victory)**: `Escape`

### Game Rules & Tips
1. **Wave Progression**: The game becomes increasingly difficult. The count, spawn rate, and speed of zombies scale with each wave.
2. **Zombie Types**:
   * 🟣 **Normal Zombie**: Average health and speed.
   * 🔴 **Fast Zombie**: Low health but moves extremely quickly and has defensive spikes.
   * ⚫ **Tank Zombie**: Giant, heavily armored, hits hard, but moves slowly.
3. **Rescue Survivors (NPCs)**:
   * Walk near yellow wandering survivors to recruit them. They will turn green and follow you.
   * Guide them into the **Safe Zone** (the green glowing area in the top-left) to rescue them. Rescuing grants **1,000 points** and **heals you for +20 HP**!
   * **Infection**: If a zombie attacks an NPC, they become infected (orange). A countdown timer will appear above their head. If they don't reach the Safe Zone before the timer hits `0`, they mutate into a Fast Zombie and attack!
4. **Loot Drops**: Defeated zombies have a chance to drop loot crates:
   * 🟢 **Health (H)**: Restores +25 Health points.
   * 🟡 **Ammo (A)**: Adds +12 Bullets to your reserve ammo.
   * 🔵 **Food (F)**: Instantly refills Stamina and awards score points.
   * 🟡 **Coin ($)**: Awards +200 bonus score.
5. **Escape**: Once Wave 10 is fully cleared, the **Escape Zone** is activated in the bottom-right corner. Make your way there to secure your victory!

---

## 🛠️ Installation & Setup

### Prerequisites
* Python 3.10, 3.11, or **Python 3.12+**
* **Pygame** library

### Steps to Run
1. Open a terminal or Command Prompt.
2. Install Pygame:
   ```bash
   pip install pygame
   ```
3. Navigate to the game folder:
   ```bash
   cd C:\Users\HP\.gemini\antigravity\scratch\infection_escape
   ```
4. Run the game:
   ```bash
   python main.py
   ```

*Note: On first launch, the game will automatically synthesize and generate all audio `.wav` files under the `assets/sounds/` folder! No external sound file downloads are necessary.*

---

## 📂 Code Architecture

The game uses clean, modular Object-Oriented programming:
* `config.py` - Contains balancing factors, speeds, color constants, and tile maps.
* `generate_assets.py` - Synthesis engine generating the retro sound effects and music.
* `sound_manager.py` - Manages audio loading and playback with error fallbacks.
* `particles.py` - Renders active muzzle flashes, blood sprays, sprint trails, and ground stains.
* `map.py` - Renders streets/alleys/Safe Zone, and manages character sliding collisions.
* `player.py` - Handles player movement, aiming directions, and gun reload timers.
* `bullet.py` - Fired projectiles with velocity trails.
* `zombie.py` - Chasing AI vectors for Normal, Fast, and Tank zombie types.
* `npc.py` - AI states (wandering, following) and infection countdowns for survivors.
* `loot.py` - Floating item crates with pulsing glows.
* `ui.py` - Draw HUD metrics and overlay screens (Start, Pause, GameOver, Victory).
* `game.py` - Coordinates loops, collision detection, camera tracking, and screen shake.
* `main.py` - Checks imports, runs sound synthesizer, and boots the game.
