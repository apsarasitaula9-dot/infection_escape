# sound_manager.py
"""
SoundManager class to load and control audio playback.
Initializes the Pygame mixer and includes error fallback wrappers to guarantee the game runs
even on systems with missing/disabled audio drivers.
"""

import pygame
import os
from config import (
    SOUND_PATH_GUNSHOT, SOUND_PATH_GROWL, SOUND_PATH_INFECTION, SOUND_PATH_MUSIC,
    SOUND_PATH_RESCUE, SOUND_PATH_CLICK, SOUND_PATH_LOOT, SOUND_PATH_HURT
)

class SoundManager:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        self.music_playing = False
        
        # 1. Attempt to initialize the Pygame mixer
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.enabled = True
            print("Audio system initialized successfully.")
        except Exception as e:
            print(f"Warning: Audio initialization failed ({e}). Playing in Silent Mode.")
            self.enabled = False
            return

        # 2. Pre-load sound effect files
        sound_paths = {
            'shoot': SOUND_PATH_GUNSHOT,
            'growl': SOUND_PATH_GROWL,
            'infection': SOUND_PATH_INFECTION,
            'rescue': SOUND_PATH_RESCUE,
            'click': SOUND_PATH_CLICK,
            'loot': SOUND_PATH_LOOT,
            'hurt': SOUND_PATH_HURT
        }
        
        for name, path in sound_paths.items():
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    # Adjust volume balances
                    if name == 'shoot':
                        self.sounds[name].set_volume(0.35)
                    elif name == 'click':
                        self.sounds[name].set_volume(0.50)
                    elif name == 'loot':
                        self.sounds[name].set_volume(0.40)
                    elif name == 'rescue':
                        self.sounds[name].set_volume(0.50)
                    elif name == 'hurt':
                        self.sounds[name].set_volume(0.60)
                    else:
                        self.sounds[name].set_volume(0.45)
                except Exception as ex:
                    print(f"Warning: Failed to load sound '{name}' at {path} ({ex})")
            else:
                print(f"Warning: Audio file not found for '{name}': {path}")

    def play(self, name):
        """Plays a pre-loaded sound effect."""
        if not self.enabled or name not in self.sounds:
            return
            
        try:
            self.sounds[name].play()
        except Exception as e:
            print(f"Failed to play sound '{name}': {e}")

    def play_music(self):
        """Loads and starts looping the synthesized background soundtrack."""
        if not self.enabled:
            return
            
        if os.path.exists(SOUND_PATH_MUSIC):
            try:
                pygame.mixer.music.load(SOUND_PATH_MUSIC)
                pygame.mixer.music.set_volume(0.30)
                pygame.mixer.music.play(-1)  # -1 loops indefinitely
                self.music_playing = True
                print("Background soundtrack loop started.")
            except Exception as e:
                print(f"Warning: Could not start music playback ({e})")
        else:
            print(f"Warning: Music file not found at {SOUND_PATH_MUSIC}")

    def stop_music(self):
        """Stops the background music."""
        if not self.enabled or not self.music_playing:
            return
            
        try:
            pygame.mixer.music.stop()
            self.music_playing = False
        except Exception as e:
            print(f"Error stopping music: {e}")
            
    def pause_music(self):
        """Pauses the background music loop."""
        if self.enabled and self.music_playing:
            pygame.mixer.music.pause()
            
    def unpause_music(self):
        """Unpauses the background music loop."""
        if self.enabled and self.music_playing:
            pygame.mixer.music.unpause()
