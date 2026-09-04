# zombie.py
"""
Zombie module defining the base Zombie class and subclasses: Normal, Fast, and Tank.
Manages AI pathing (target chasing towards nearest survivor), collision steering,
combat damage checks, health-bars, and rendering.
"""

import pygame
import math
import random
from config import (
    COLOR_ZOMBIE_NORMAL, COLOR_ZOMBIE_FAST, COLOR_ZOMBIE_TANK,
    ZOMBIE_NORMAL_SPEED, ZOMBIE_NORMAL_HEALTH, ZOMBIE_NORMAL_DAMAGE,
    ZOMBIE_NORMAL_SIZE, ZOMBIE_NORMAL_POINTS,
    ZOMBIE_FAST_SPEED, ZOMBIE_FAST_HEALTH, ZOMBIE_FAST_DAMAGE,
    ZOMBIE_FAST_SIZE, ZOMBIE_FAST_POINTS,
    ZOMBIE_TANK_SPEED, ZOMBIE_TANK_HEALTH, ZOMBIE_TANK_DAMAGE,
    ZOMBIE_TANK_SIZE, ZOMBIE_TANK_POINTS, COLOR_UI_RED, COLOR_UI_GREEN
)

class Zombie:
    def __init__(self, x, y, speed, health, damage, size, points, color):
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.health = health
        self.max_health = health
        self.damage = damage
        self.size = size
        self.points = points
        self.color = color
        
        # Collider rect
        self.rect = pygame.Rect(
            int(self.x - self.size),
            int(self.y - self.size),
            self.size * 2,
            self.size * 2
        )
        
        self.angle = 0.0
        self.attack_cooldown = 1000  # ms between attacks
        self.last_attack_time = 0
        
        # Keep track of target for orientation
        self.chasing_player = True

    def update(self, player, npcs, game_map, now):
        """Finds closest target (player or rescueable NPC) and walks towards them with obstacle avoidance."""
        # 1. Target Selection: Find nearest target among player and uninfected NPCs
        closest_target = player
        min_dist = math.hypot(player.x - self.x, player.y - self.y)
        self.chasing_player = True
        
        for npc in npcs:
            if npc.state == "following" or npc.state == "wandering":
                if not npc.is_infected:  # Zombies target uninfected targets first
                    dist = math.hypot(npc.x - self.x, npc.y - self.y)
                    if dist < min_dist:
                        min_dist = dist
                        closest_target = npc
                        self.chasing_player = False

        # 2. Update angle towards target
        self.angle = math.atan2(closest_target.y - self.y, closest_target.x - self.x)

        # 3. Movement with obstacle steering assistance
        old_x, old_y = self.x, self.y
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        game_map.resolve_collision(self, old_x, old_y)
        
        # Wall steering fallback: if stuck (not moving), steer using oscillatory search
        if abs(self.x - old_x) < 0.05 and abs(self.y - old_y) < 0.05:
            # Shift angle by a wide wave to find an opening left or right
            drift = math.sin(now * 0.006 + self.x) * 1.1  # oscillates
            self.x += math.cos(self.angle + drift) * self.speed
            self.y += math.sin(self.angle + drift) * self.speed
            game_map.resolve_collision(self, old_x, old_y)

    def take_damage(self, amount):
        """Reduces health. Returns True if dead."""
        self.health -= amount
        return self.health <= 0

    def draw(self, surface, camera_x, camera_y):
        """Draws the zombie body, red eyes, and a floating health bar if damaged."""
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y - camera_y)
        
        # Draw base zombie circle
        pygame.draw.circle(surface, self.color, (draw_x, draw_y), self.size)
        pygame.draw.circle(surface, (10, 10, 10), (draw_x, draw_y), self.size, 2)  # border

        # Draw glowing red eyes looking at target
        eye_offset = 0.4
        left_eye_x = draw_x + math.cos(self.angle - eye_offset) * (self.size - 6)
        left_eye_y = draw_y + math.sin(self.angle - eye_offset) * (self.size - 6)
        right_eye_x = draw_x + math.cos(self.angle + eye_offset) * (self.size - 6)
        right_eye_y = draw_y + math.sin(self.angle + eye_offset) * (self.size - 6)
        
        pygame.draw.circle(surface, COLOR_UI_RED, (int(left_eye_x), int(left_eye_y)), 3)
        pygame.draw.circle(surface, COLOR_UI_RED, (int(right_eye_x), int(right_eye_y)), 3)

        # Draw health bar above head only if damaged
        if self.health < self.max_health:
            bar_width = self.size * 2
            bar_height = 4
            bar_x = draw_x - self.size
            bar_y = draw_y - self.size - 8
            
            # Draw black background
            pygame.draw.rect(surface, (20, 20, 20), (bar_x, bar_y, bar_width, bar_height))
            # Draw green health portion
            health_ratio = max(0.0, min(1.0, self.health / self.max_health))
            pygame.draw.rect(surface, COLOR_UI_GREEN, (bar_x, bar_y, int(bar_width * health_ratio), bar_height))


class NormalZombie(Zombie):
    def __init__(self, x, y):
        super().__init__(
            x=x, y=y,
            speed=ZOMBIE_NORMAL_SPEED,
            health=ZOMBIE_NORMAL_HEALTH,
            damage=ZOMBIE_NORMAL_DAMAGE,
            size=ZOMBIE_NORMAL_SIZE,
            points=ZOMBIE_NORMAL_POINTS,
            color=COLOR_ZOMBIE_NORMAL
        )


class FastZombie(Zombie):
    def __init__(self, x, y):
        super().__init__(
            x=x, y=y,
            speed=ZOMBIE_FAST_SPEED,
            health=ZOMBIE_FAST_HEALTH,
            damage=ZOMBIE_FAST_DAMAGE,
            size=ZOMBIE_FAST_SIZE,
            points=ZOMBIE_FAST_POINTS,
            color=COLOR_ZOMBIE_FAST
        )

    def draw(self, surface, camera_x, camera_y):
        # Overrides draw to add a motion blur tail/spikes for fast zombie
        super().draw(surface, camera_x, camera_y)
        
        # Add a subtle spike indicator to make it visually distinct
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y - camera_y)
        # Small red horns/ears pointing backwards
        back_angle = self.angle + math.pi
        horn_l_x = draw_x + math.cos(back_angle - 0.4) * self.size
        horn_l_y = draw_y + math.sin(back_angle - 0.4) * self.size
        horn_r_x = draw_x + math.cos(back_angle + 0.4) * self.size
        horn_r_y = draw_y + math.sin(back_angle + 0.4) * self.size
        pygame.draw.line(surface, COLOR_ZOMBIE_FAST, (draw_x, draw_y), (int(horn_l_x), int(horn_l_y)), 2)
        pygame.draw.line(surface, COLOR_ZOMBIE_FAST, (draw_x, draw_y), (int(horn_r_x), int(horn_r_y)), 2)


class TankZombie(Zombie):
    def __init__(self, x, y):
        super().__init__(
            x=x, y=y,
            speed=ZOMBIE_TANK_SPEED,
            health=ZOMBIE_TANK_HEALTH,
            damage=ZOMBIE_TANK_DAMAGE,
            size=ZOMBIE_TANK_SIZE,
            points=ZOMBIE_TANK_POINTS,
            color=COLOR_ZOMBIE_TANK
        )

    def draw(self, surface, camera_x, camera_y):
        # Overrides draw to add a armor shield plates around the tank zombie
        super().draw(surface, camera_x, camera_y)
        
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y - camera_y)
        
        # Draw a heavy steel armor band around the body
        pygame.draw.circle(surface, (100, 110, 120), (draw_x, draw_y), self.size - 4, 2)
        # Draw small yellow glowing hazard dots on its back (cool indicator!)
        back_angle = self.angle + math.pi
        dot_x = draw_x + math.cos(back_angle) * (self.size - 4)
        dot_y = draw_y + math.sin(back_angle) * (self.size - 4)
        pygame.draw.circle(surface, (241, 196, 15), (int(dot_x), int(dot_y)), 3)
