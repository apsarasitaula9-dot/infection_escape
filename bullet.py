# bullet.py
"""
Projectile class representing bullets fired by the player.
Handles tracking, linear propagation, wall collision triggers, and stylized rendering.
"""

import pygame
import math
from config import BULLET_SPEED, BULLET_DAMAGE, BULLET_SIZE, COLOR_BULLET

class Bullet:
    def __init__(self, x, y, angle, damage=BULLET_DAMAGE, speed=BULLET_SPEED):
        self.x = float(x)
        self.y = float(y)
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.size = BULLET_SIZE
        
        # Calculate velocity components
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        
        # Collider rect
        self.rect = pygame.Rect(
            int(self.x - self.size),
            int(self.y - self.size),
            self.size * 2,
            self.size * 2
        )
        
        # Max range/time indicator (avoid infinite movement if out of bounds)
        self.distance_traveled = 0.0
        self.max_distance = 1600.0  # Slightly larger than screen diagonal
        self.to_remove = False

    def update(self, dt_modifier=1.0):
        """Updates bullet coordinates based on velocity and dt modifier."""
        # Calculate frame movement
        move_x = self.dx * dt_modifier
        move_y = self.dy * dt_modifier
        
        self.x += move_x
        self.y += move_y
        
        # Update collider pos
        self.rect.x = int(self.x - self.size)
        self.rect.y = int(self.y - self.size)
        
        # Accumulate distance traveled to clean up old bullets
        self.distance_traveled += math.hypot(move_x, move_y)
        if self.distance_traveled >= self.max_distance:
            self.to_remove = True

    def draw(self, surface, camera_x, camera_y):
        """Draws the bullet as a glowing golden streak along its movement vector."""
        # Draw a small streak line representing movement vector (cool velocity effect)
        length = 12
        start_x = self.x - camera_x
        start_y = self.y - camera_y
        
        end_x = start_x - math.cos(self.angle) * length
        end_y = start_y - math.sin(self.angle) * length
        
        # Outer glow (transparent wider line)
        glow_width = 5
        glow_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        pygame.draw.line(
            glow_surf,
            (COLOR_BULLET[0], COLOR_BULLET[1], COLOR_BULLET[2], 75),  # Semi-transparent golden
            (start_x, start_y),
            (end_x, end_y),
            glow_width
        )
        surface.blit(glow_surf, (0, 0))
        
        # Core solid bullet line
        pygame.draw.line(
            surface,
            COLOR_BULLET,
            (start_x, start_y),
            (end_x, end_y),
            2
        )
