# player.py
"""
Player class representing the user-controlled survivor.
Manages input, movement (sprinting/stamina), orientation, shooting stats, and reload loops.
"""

import pygame
import math
from config import (
    COLOR_PLAYER, PLAYER_SIZE, PLAYER_SPEED, PLAYER_SPRINT_SPEED,
    PLAYER_MAX_HEALTH, PLAYER_MAX_STAMINA, PLAYER_STAMINA_DRAIN,
    PLAYER_STAMINA_REGEN, PLAYER_MAX_MAGAZINE, PLAYER_START_AMMO,
    PLAYER_RELOAD_TIME, PLAYER_FIRE_COOLDOWN, COLOR_TEXT_WHITE, COLOR_PLAYER_SPARK
)
from bullet import Bullet

class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.size = PLAYER_SIZE
        
        # Collider rect (centered on x, y)
        self.rect = pygame.Rect(
            int(self.x - self.size),
            int(self.y - self.size),
            self.size * 2,
            self.size * 2
        )
        
        # Stats
        self.health = PLAYER_MAX_HEALTH
        self.stamina = PLAYER_MAX_STAMINA
        
        # Weapon State
        self.magazine = PLAYER_MAX_MAGAZINE
        self.reserve_ammo = PLAYER_START_AMMO
        self.is_reloading = False
        self.reload_timer = 0
        self.last_shot_time = 0
        
        # Orientation & Movement
        self.angle = 0.0
        self.is_sprinting = False
        self.is_moving = False

    def update(self, keys, mouse_pos, camera_x, camera_y, game_map, now, particle_system=None):
        """Processes player inputs, updates cooldowns, reloads, and moves with wall sliding."""
        
        # 1. Aiming (calculate angle from player screen position to mouse position)
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        mouse_x, mouse_y = mouse_pos
        self.angle = math.atan2(mouse_y - screen_y, mouse_x - screen_x)

        # 2. Weapon Reload Timer Update
        if self.is_reloading:
            self.reload_timer -= 16.67  # Approximating ms per frame at 60 FPS
            if self.reload_timer <= 0:
                self.is_reloading = False
                # Calculate ammo needs
                needed = PLAYER_MAX_MAGAZINE - self.magazine
                transfer = min(needed, self.reserve_ammo)
                self.magazine += transfer
                self.reserve_ammo -= transfer

        # 3. Determine Speed & Sprint (drain/regen stamina)
        move_x = 0
        move_y = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y += 1

        self.is_moving = (move_x != 0 or move_y != 0)
        
        # Check sprint requirements: holds Shift, is moving, has stamina, and is not reloading
        wants_sprint = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
        self.is_sprinting = wants_sprint and self.is_moving and self.stamina > 0.0

        if self.is_sprinting:
            current_speed = PLAYER_SPRINT_SPEED
            self.stamina = max(0.0, self.stamina - PLAYER_STAMINA_DRAIN)
            # Emit trail particles behind player
            if particle_system and now % 4 == 0:
                trail_angle = self.angle + math.pi + random_offset()
                trail_x = self.x - math.cos(self.angle) * self.size
                trail_y = self.y - math.sin(self.angle) * self.size
                particle_system.emit_trail(trail_x, trail_y, COLOR_PLAYER_SPARK)
        else:
            current_speed = PLAYER_SPEED
            self.stamina = min(PLAYER_MAX_STAMINA, self.stamina + PLAYER_STAMINA_REGEN)

        # 4. Perform Movement with sliding collision resolution
        if self.is_moving:
            # Normalize diagonal movement vector
            dist = math.hypot(move_x, move_y)
            dx = (move_x / dist) * current_speed
            dy = (move_y / dist) * current_speed
            
            # Save original position
            old_x, old_y = self.x, self.y
            
            # Move
            self.x += dx
            self.y += dy
            
            # Resolve collisions using the map
            game_map.resolve_collision(self, old_x, old_y)

    def shoot(self, now):
        """Fires a bullet if criteria are met. Returns a Bullet instance or None."""
        if self.is_reloading:
            return None, "reloading"
        if self.magazine <= 0:
            return None, "empty"
        if now - self.last_shot_time < PLAYER_FIRE_COOLDOWN:
            return None, "cooldown"
            
        self.magazine -= 1
        self.last_shot_time = now
        
        # Create bullet. Spawns at the tip of the player's gun barrel
        barrel_length = self.size + 12
        spawn_x = self.x + math.cos(self.angle) * barrel_length
        spawn_y = self.y + math.sin(self.angle) * barrel_length
        
        bullet = Bullet(spawn_x, spawn_y, self.angle)
        return bullet, "shoot"

    def reload(self, now, sound_manager=None):
        """Starts reload phase if weapons are empty/partial and reserve ammo is available."""
        if self.is_reloading:
            return
        if self.magazine == PLAYER_MAX_MAGAZINE:
            return
        if self.reserve_ammo <= 0:
            return
            
        self.is_reloading = True
        self.reload_timer = PLAYER_RELOAD_TIME * 1000  # Convert to ms
        if sound_manager:
            sound_manager.play('click')

    def draw(self, surface, camera_x, camera_y):
        """Draws player body, aim direction indicators (gun, eyes), and reload progress arc."""
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y - camera_y)
        
        # Draw player outer neon shadow/glow
        glow_size = self.size + 5
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (52, 152, 219, 50), (glow_size, glow_size), glow_size)
        surface.blit(glow_surf, (draw_x - glow_size, draw_y - glow_size))
        
        # Draw core body circle
        pygame.draw.circle(surface, COLOR_PLAYER, (draw_x, draw_y), self.size)
        pygame.draw.circle(surface, (255, 255, 255), (draw_x, draw_y), self.size, 2)  # border

        # Draw gun barrel pointing in mouse direction
        barrel_length = self.size + 12
        end_x = draw_x + math.cos(self.angle) * barrel_length
        end_y = draw_y + math.sin(self.angle) * barrel_length
        pygame.draw.line(surface, COLOR_TEXT_WHITE, (draw_x, draw_y), (end_x, end_y), 4)

        # Draw eyes looking in aiming direction (looks super premium and animated!)
        eye_offset_angle = 0.4  # radians offset from direction angle
        eye_dist = 10
        left_eye_x = draw_x + math.cos(self.angle - eye_offset_angle) * eye_dist
        left_eye_y = draw_y + math.sin(self.angle - eye_offset_angle) * eye_dist
        right_eye_x = draw_x + math.cos(self.angle + eye_offset_angle) * eye_dist
        right_eye_y = draw_y + math.sin(self.angle + eye_offset_angle) * eye_dist
        
        pygame.draw.circle(surface, (255, 255, 255), (int(left_eye_x), int(left_eye_y)), 3)
        pygame.draw.circle(surface, (255, 255, 255), (int(right_eye_x), int(right_eye_y)), 3)
        # Small pupils
        pupil_x_l = left_eye_x + math.cos(self.angle) * 1.0
        pupil_y_l = left_eye_y + math.sin(self.angle) * 1.0
        pupil_x_r = right_eye_x + math.cos(self.angle) * 1.0
        pupil_y_r = right_eye_y + math.sin(self.angle) * 1.0
        pygame.draw.circle(surface, (0, 0, 0), (int(pupil_x_l), int(pupil_y_l)), 1)
        pygame.draw.circle(surface, (0, 0, 0), (int(pupil_x_r), int(pupil_y_r)), 1)

        # Draw reload indicator circle above head
        if self.is_reloading:
            progress = 1.0 - (self.reload_timer / (PLAYER_RELOAD_TIME * 1000))
            progress = max(0.0, min(1.0, progress))
            
            ind_y = draw_y - self.size - 12
            ind_rect = pygame.Rect(draw_x - 8, ind_y - 8, 16, 16)
            
            # Draw gray base circle
            pygame.draw.circle(surface, (70, 70, 70), (draw_x, ind_y), 8, 2)
            # Draw green arc representing load percentage
            start_angle = -math.pi / 2
            end_angle = start_angle + (2 * math.pi * progress)
            # draw arc requires angles in radians
            pygame.draw.arc(surface, (46, 204, 113), ind_rect, -end_angle, -start_angle, 2)

def random_offset():
    import random
    return random.uniform(-0.15, 0.15)
