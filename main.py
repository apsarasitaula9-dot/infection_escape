# main.py
"""
Launcher script for Infection Escape.
Verifies dependencies, synthesizes missing audio files, and launches the game loop.
"""

import sys
import os

# 1. Verify dependencies are available
try:
    import pygame
except ImportError:
    print("-" * 60)
    print("CRITICAL ERROR: The 'pygame' library is not installed.")
    print("Please install Pygame to run this game:")
    print("   pip install pygame")
    print("-" * 60)
    input("Press Enter to exit...")
    sys.exit(1)

# 2. Trigger audio asset generation if missing
try:
    from generate_assets import generate_all_sounds
    print("Checking audio assets...")
    generate_all_sounds()
except Exception as e:
    print(f"Warning: Audio asset generation check failed: {e}")
    print("The game will run, but sound effects may be missing.")

# 3. Launch the game
try:
    from game import Game
    print("Launching Infection Escape...")
    game = Game()
    game.run()
except Exception as e:
    import traceback
    print("-" * 60)
    print("CRITICAL ERROR: Game crashed during runtime.")
    print(f"Error details: {e}")
    print("-" * 60)
    traceback.print_exc()
    input("\nPress Enter to close...")
    sys.exit(1)
