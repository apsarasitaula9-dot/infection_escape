# loot.py
"""
Loot class representing collectable items (health, ammo, food, coins).
Includes animated bobbing (sine-wave float) and glow pulsing.
"""

import pygame
import math
from config import LOOT_SIZE, LOOT_LIFETIME, LOOT_TYPES

class Loot:
    def __init__(self, x, y, loot_type=None):
        self.x = x
        self.y = y
        
        # Select type (random selection is handled in Game, but fallback here)
        import random
        self.type = loot_type if loot_type in LOOT_TYPES else random.choice(list(LOOT_TYPES.keys()))
        
        # Load stats from config
        self.stats = LOOT_TYPES[self.type]
        self.color = self.stats['color']
        self.val = self.stats['val']
        self.size = LOOT_SIZE
        
        self.rect = pygame.Rect(
            int(self.x - self.size),
            int(self.y - self.size),
            self.size * 2,
            self.size * 2
        )
        
        self.spawn_time = pygame.time.get_ticks()
        self.to_remove = False

    def update(self):
        """Checks expiration based on lifetime."""
        now = pygame.time.get_ticks()
        if now - self.spawn_time > LOOT_LIFETIME:
            self.to_remove = True

    def draw(self, surface, camera_x, camera_y):
        """Draws the loot item with floating animation, glow, and emblem letter."""
        now = pygame.time.get_ticks()
        time_alive = now - self.spawn_time
        
        # Expiration flashing: Flash when less than 3 seconds remain
        if LOOT_LIFETIME - time_alive < 3000:
            if (time_alive // 150) % 2 == 0:  # Rapid flashing
                return
                
        # Bobbing float animation: Y displacement between -6 and +6 pixels
        bob_offset = math.sin(time_alive * 0.005) * 6.0
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y + bob_offset - camera_y)
        
        # Pulsing glow radius
        pulse = math.sin(time_alive * 0.01) * 3.0
        glow_radius = int(self.size + 4 + pulse)
        
        # 1. Draw transparent glow aura
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surf,
            (self.color[0], self.color[1], self.color[2], 60),  # Transparent matching color
            (glow_radius, glow_radius),
            glow_radius
        )
        surface.blit(glow_surf, (draw_x - glow_radius, draw_y - glow_radius))
        
        # 2. Draw solid core
        pygame.draw.circle(surface, self.color, (draw_x, draw_y), self.size)
        # Outline for depth
        pygame.draw.circle(surface, (255, 255, 255), (draw_x, draw_y), self.size, 1)
        
        # 3. Draw emblem letter
        font = pygame.font.SysFont("Arial", 11, bold=True)
        letter = ""
        if self.type == "health":
            letter = "H"
        elif self.type == "ammo":
            letter = "A"
        elif self.type == "food":
            letter = "F"
        elif self.type == "coin":
            letter = "$"
            
        text_surf = font.render(letter, True, (COLOR_BG if self.type != 'coin' else (20, 20, 20)))
        text_rect = text_surf.get_rect(center=(draw_x, draw_y))
        surface.blit(text_surf, text_rect)
