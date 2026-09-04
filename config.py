# config.py
"""
Configuration settings and constants for Infection Escape.
Allows easy adjustment of game balance, layout, and colors.
"""

# Screen Settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Color Palette (Dark mode with premium neon styling)
COLOR_BG = (15, 15, 22)             # Deep dark navy/black
COLOR_WALL = (35, 38, 50)           # Dark slate gray
COLOR_SAFE_ZONE = (34, 139, 34, 40) # Forest green with alpha (for overlays)
COLOR_SAFE_ZONE_BORDER = (46, 204, 113) # Neon green border

COLOR_PLAYER = (52, 152, 219)       # Neon cyan/blue
COLOR_PLAYER_SPARK = (93, 173, 226)  # Light cyan

# NPC Colors
COLOR_NPC = (241, 196, 15)          # Warm yellow
COLOR_NPC_INFECTED = (230, 126, 34) # Orange
COLOR_NPC_RESCUED = (46, 204, 113)  # Emerald green

# Zombie Colors
COLOR_ZOMBIE_NORMAL = (142, 68, 173) # Purple
COLOR_ZOMBIE_FAST = (231, 76, 60)    # Red
COLOR_ZOMBIE_TANK = (39, 55, 70)     # Dark heavy steel gray

# Bullet & Combat Colors
COLOR_BULLET = (254, 211, 48)       # Bright gold
COLOR_BLOOD = (192, 57, 43)         # Dark red blood
COLOR_SPARK = (243, 156, 18)        # Muzzle flash orange/yellow

# UI & text colors
COLOR_TEXT_WHITE = (236, 240, 241)  # Pure off-white
COLOR_TEXT_MUTED = (149, 165, 166)  # Gray
COLOR_PANEL_BG = (30, 30, 42, 200)   # Semi-transparent dark panel
COLOR_UI_GREEN = (46, 204, 113)     # Positive/Health
COLOR_UI_RED = (231, 76, 60)        # Negative/Danger
COLOR_UI_YELLOW = (241, 196, 15)    # Stamina/Warning

# Map Settings
TILE_SIZE = 64
MAP_COLS = 30   # Map total width: 1920 pixels
MAP_ROWS = 24   # Map total height: 1536 pixels
SAFE_ZONE_RECT = (100, 100, 350, 350)  # Left, Top, Width, Height of the safe zone

# Player Stats
PLAYER_SIZE = 20
PLAYER_SPEED = 4.0
PLAYER_SPRINT_SPEED = 6.5
PLAYER_MAX_HEALTH = 100
PLAYER_MAX_STAMINA = 100
PLAYER_STAMINA_DRAIN = 0.5   # Per frame during sprint
PLAYER_STAMINA_REGEN = 0.25  # Per frame during normal walk/idle
PLAYER_RELOAD_TIME = 1.5     # Seconds
PLAYER_FIRE_COOLDOWN = 150   # Milliseconds between shots
PLAYER_MAX_MAGAZINE = 12
PLAYER_START_AMMO = 36       # In reserve

# Bullet Stats
BULLET_SPEED = 12.0
BULLET_DAMAGE = 25
BULLET_SIZE = 4
BULLET_LIFETIME = 1500       # Milliseconds before disappearing

# Zombie Types & Stats
# Normal Zombie
ZOMBIE_NORMAL_SPEED = 2.0
ZOMBIE_NORMAL_HEALTH = 50
ZOMBIE_NORMAL_DAMAGE = 10
ZOMBIE_NORMAL_SIZE = 18
ZOMBIE_NORMAL_POINTS = 100

# Fast Zombie
ZOMBIE_FAST_SPEED = 3.6
ZOMBIE_FAST_HEALTH = 30
ZOMBIE_FAST_DAMAGE = 5
ZOMBIE_FAST_SIZE = 16
ZOMBIE_FAST_POINTS = 150

# Tank Zombie
ZOMBIE_TANK_SPEED = 1.2
ZOMBIE_TANK_HEALTH = 180
ZOMBIE_TANK_DAMAGE = 25
ZOMBIE_TANK_SIZE = 26
ZOMBIE_TANK_POINTS = 300

# NPC Stats
NPC_SIZE = 18
NPC_SPEED = 1.5
NPC_FOLLOW_DIST = 50        # Distance they try to maintain behind player
NPC_INFECT_TIME = 8.0       # Seconds before turning after attack
NPC_RESCUE_POINTS = 1000    # Points for bringing them to the safe zone

# Loot Drop Settings
LOOT_SIZE = 12
LOOT_LIFETIME = 12000       # 12 seconds
LOOT_DROP_CHANCE = 0.4      # Chance of zombie dropping loot on death
LOOT_TYPES = {
    'health': {'color': (46, 204, 113), 'val': 25}, # Restores health
    'ammo': {'color': (241, 196, 15), 'val': 12},   # Restores ammo reserve
    'food': {'color': (52, 152, 219), 'val': 15},   # Refills stamina buffer/bonus points
    'coin': {'color': (241, 196, 15), 'val': 200}   # Direct bonus score
}

# Assets Paths
SOUND_PATH_GUNSHOT = "assets/sounds/gunshot.wav"
SOUND_PATH_GROWL = "assets/sounds/zombie_growl.wav"
SOUND_PATH_INFECTION = "assets/sounds/infection.wav"
SOUND_PATH_MUSIC = "assets/sounds/bg_music.wav"
SOUND_PATH_RESCUE = "assets/sounds/rescue.wav"
SOUND_PATH_CLICK = "assets/sounds/click.wav"
SOUND_PATH_LOOT = "assets/sounds/loot.wav"
SOUND_PATH_HURT = "assets/sounds/hurt.wav"

HIGH_SCORE_FILE = "highscores.txt"
