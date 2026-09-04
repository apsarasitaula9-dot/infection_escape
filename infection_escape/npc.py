# npc.py
"""
NPC (Non-Player Character) Survivor class.
Manages survivor AI state machine (Wandering, Following, Infected),
movement, pathing towards the player, infection countdowns, and rendering.
"""

import pygame
import random
import math
from config import (
    COLOR_NPC, COLOR_NPC_INFECTED, COLOR_NPC_RESCUED, NPC_SIZE, NPC_SPEED,
    NPC_FOLLOW_DIST, NPC_INFECT_TIME, COLOR_TEXT_WHITE, COLOR_UI_RED, COLOR_BG
)

class NPC:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.size = NPC_SIZE
        
        # Collider rect
        self.rect = pygame.Rect(
            int(self.x - self.size),
            int(self.y - self.size),
            self.size * 2,
            self.size * 2
        )
        
        # States: "wandering", "following"
        self.state = "wandering"
        
        # Infection state
        self.is_infected = False
        self.infection_timer = 0.0  # Remaining seconds before turning
        self.has_turned = False     # Triggers spawning a zombie
        
        # Wander state attributes
        self.wander_target_x = self.x
        self.wander_target_y = self.y
        self.wander_timer = 0
        
        # Orientation angle
        self.angle = random.uniform(0, 2 * math.pi)

    def infect(self):
        """Triggers the infection sequence."""
        if not self.is_infected:
            self.is_infected = True
            self.infection_timer = NPC_INFECT_TIME

    def update(self, player, game_map, now):
        """Updates NPC states: wandering, following, and infection timer decays."""
        
        # 1. Update Infection countdown
        if self.is_infected:
            self.infection_timer -= 0.01667  # Subtract 1 frame (1/60th of a second)
            if self.infection_timer <= 0:
                self.has_turned = True
                return

        # 2. Check for player recruitment
        dist_to_player = math.hypot(player.x - self.x, player.y - self.y)
        if self.state == "wandering" and dist_to_player < 80.0:
            self.state = "following"
            # Return true to play a rescue sound trigger
            return True

        # 3. AI Movement Logic
        old_x, old_y = self.x, self.y
        
        if self.state == "following":
            # Walk towards the player, but stop at NPC_FOLLOW_DIST
            if dist_to_player > NPC_FOLLOW_DIST:
                self.angle = math.atan2(player.y - self.y, player.x - self.x)
                # If infected, they walk slightly erratically in panic
                angle_offset = math.sin(now * 0.01) * 0.3 if self.is_infected else 0.0
                
                self.x += math.cos(self.angle + angle_offset) * NPC_SPEED
                self.y += math.sin(self.angle + angle_offset) * NPC_SPEED
                game_map.resolve_collision(self, old_x, old_y)
                
        elif self.state == "wandering":
            # Wandering AI
            self.wander_timer -= 1
            
            # Choose a new target direction occasionally, or if close to current target
            target_dist = math.hypot(self.wander_target_x - self.x, self.wander_target_y - self.y)
            if self.wander_timer <= 0 or target_dist < 15.0:
                # Pick a random spot nearby
                self.wander_target_x = self.x + random.uniform(-150, 150)
                self.wander_target_y = self.y + random.uniform(-150, 150)
                # Keep within map bounds
                self.wander_target_x = max(50.0, min(game_map.width - 50.0, self.wander_target_x))
                self.wander_target_y = max(50.0, min(game_map.height - 50.0, self.wander_target_y))
                
                self.wander_timer = random.randint(120, 300)  # 2 to 5 seconds
                
            # Move towards wander target
            self.angle = math.atan2(self.wander_target_y - self.y, self.wander_target_x - self.x)
            self.x += math.cos(self.angle) * (NPC_SPEED * 0.7)  # Wander slower
            self.y += math.sin(self.angle) * (NPC_SPEED * 0.7)
            
            # If hit a wall, pick a new target immediately
            collision_occurred = game_map.check_collision(self.rect)
            game_map.resolve_collision(self, old_x, old_y)
            if collision_occurred:
                self.wander_timer = 0  # Re-evaluate next frame
                
        return False

    def draw(self, surface, camera_x, camera_y):
        """Draws the NPC with appropriate color, indicator smileys, eyes, and timer if infected."""
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y - camera_y)
        
        # Color based on state
        if self.is_infected:
            color = COLOR_NPC_INFECTED
        elif self.state == "following":
            color = COLOR_NPC_RESCUED
        else:
            color = COLOR_NPC
            
        # Draw base survivor circle
        pygame.draw.circle(surface, color, (draw_x, draw_y), self.size)
        pygame.draw.circle(surface, (255, 255, 255), (draw_x, draw_y), self.size, 2)

        # Draw eyes looking in orientation angle
        eye_offset = 0.4
        left_eye_x = draw_x + math.cos(self.angle - eye_offset) * 8
        left_eye_y = draw_y + math.sin(self.angle - eye_offset) * 8
        right_eye_x = draw_x + math.cos(self.angle + eye_offset) * 8
        right_eye_y = draw_y + math.sin(self.angle + eye_offset) * 8
        
        pygame.draw.circle(surface, (255, 255, 255), (int(left_eye_x), int(left_eye_y)), 3)
        pygame.draw.circle(surface, (255, 255, 255), (int(right_eye_x), int(right_eye_y)), 3)
        pygame.draw.circle(surface, (0, 0, 0), (int(left_eye_x), int(left_eye_y)), 1)
        pygame.draw.circle(surface, (0, 0, 0), (int(right_eye_x), int(right_eye_y)), 1)

        # Draw rescued smiley indicator if following
        if self.state == "following" and not self.is_infected:
            # Draw a tiny heart or plus symbol above head
            icon_y = draw_y - self.size - 10
            pygame.draw.circle(surface, (46, 204, 113), (draw_x, icon_y), 5)
            # draw a white plus inside the green circle
            pygame.draw.line(surface, COLOR_TEXT_WHITE, (draw_x - 2, icon_y), (draw_x + 2, icon_y), 1)
            pygame.draw.line(surface, COLOR_TEXT_WHITE, (draw_x, icon_y - 2), (draw_x, icon_y + 2), 1)

        # Draw infection countdown timer text
        if self.is_infected:
            font = pygame.font.SysFont("Courier New", 12, bold=True)
            timer_text = f"{self.infection_timer:.1f}s"
            # Flash timer text between white and red
            text_color = COLOR_UI_RED if int(self.infection_timer * 5) % 2 == 0 else COLOR_TEXT_WHITE
            
            text_surf = font.render(timer_text, True, text_color)
            text_rect = text_surf.get_rect(center=(draw_x, draw_y - self.size - 12))
            
            # Small background box for legibility
            bg_rect = pygame.Rect(text_rect.x - 3, text_rect.y - 1, text_rect.width + 6, text_rect.height + 2)
            pygame.draw.rect(surface, (10, 10, 10), bg_rect)
            pygame.draw.rect(surface, COLOR_NPC_INFECTED, bg_rect, 1)
            
            surface.blit(text_surf, text_rect)
