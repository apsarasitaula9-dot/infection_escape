# game.py
"""
Game controller containing the main state machine, event processor,
physics loop, entity manager, and graphics rendering pipeline.
"""

import pygame
import random
import math
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_WALL, TILE_SIZE,
    PLAYER_MAX_HEALTH, LOOT_DROP_CHANCE, COLOR_BLOOD, COLOR_SPARK,
    COLOR_UI_YELLOW, COLOR_UI_GREEN, COLOR_UI_RED, SOUND_PATH_MUSIC
)
from player import Player
from zombie import NormalZombie, FastZombie, TankZombie
from npc import NPC
from loot import Loot
from map import Map
from particles import ParticleSystem
from sound_manager import SoundManager
from ui import UIManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Infection Escape")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # State: "MENU", "PLAYING", "PAUSED", "GAMEOVER", "VICTORY"
        self.state = "MENU"
        
        # Subsystems
        self.map = Map()
        self.particle_system = ParticleSystem()
        self.sound_manager = SoundManager()
        self.ui_manager = UIManager(self.screen)
        
        # Camera coordinates
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.screen_shake = 0  # Damage shake intensity
        
        # Game stats
        self.score = 0
        self.wave = 1
        self.rescued_count = 0
        self.start_ticks = 0
        self.elapsed_time = 0.0
        self.game_paused_ticks = 0
        self.pause_start_ticks = 0
        
        # Entity lists
        self.player = None
        self.bullets = []
        self.zombies = []
        self.npcs = []
        self.loots = []
        
        # Wave details
        self.zombies_spawned_this_wave = 0
        self.zombies_needed_to_spawn = 0
        self.zombie_spawn_timer = 0
        self.zombie_spawn_cooldown = 2000  # ms between spawns
        self.max_active_zombies = 45        # Frame rate protection
        
        # Escape Zone details
        self.escape_active = False
        self.escape_rect = pygame.Rect(self.map.width - 250, self.map.height - 250, 150, 150)
        self.escape_points_reward = 3000
        
        # Load music
        self.sound_manager.play_music()

    def reset_game(self):
        """Resets all stats and entity lists for a fresh game session."""
        self.player = Player(250, 250)  # Spawn near safe zone (top-left)
        self.bullets.clear()
        self.zombies.clear()
        self.npcs.clear()
        self.loots.clear()
        self.particle_system.clear()
        
        self.score = 0
        self.wave = 1
        self.rescued_count = 0
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0.0
        self.game_paused_ticks = 0
        
        self.escape_active = False
        self.screen_shake = 0
        
        self.zombies_spawned_this_wave = 0
        self.zombies_needed_to_spawn = 0
        self.zombie_spawn_timer = 0
        
        # Trigger initial wave setup
        self.start_wave(self.wave)

    def start_wave(self, wave_num):
        """Sets up difficulty params and spawns survivors for the current wave."""
        self.zombies_spawned_this_wave = 0
        # Calculate zombies count (exponential scaling)
        self.zombies_needed_to_spawn = 8 + (wave_num * 5)
        # Faster spawns on later waves
        self.zombie_spawn_cooldown = max(400, 2000 - (wave_num * 150))
        
        # Spawn survivors in distant, safe grid tiles
        num_survivors = random.randint(1, 3)
        if wave_num == 1:
            num_survivors = 2  # friendly starting number
            
        spawn_attempts = 0
        while len(self.npcs) < num_survivors and spawn_attempts < 50:
            rx = random.uniform(200, self.map.width - 200)
            ry = random.uniform(200, self.map.height - 200)
            
            # Verify coordinates are not inside safe zone, not in a wall, and away from player
            temp_rect = pygame.Rect(int(rx - 15), int(ry - 15), 30, 30)
            dist_to_player = math.hypot(rx - (self.player.x if self.player else 250), ry - (self.player.y if self.player else 250))
            
            if (not self.map.safe_zone.colliderect(temp_rect) and 
                not self.map.check_collision(temp_rect) and 
                dist_to_player > 350.0):
                self.npcs.append(NPC(rx, ry))
            spawn_attempts += 1
            
        print(f"Wave {wave_num} initialized: Spawning {self.zombies_needed_to_spawn} zombies, {len(self.npcs)} survivors.")

    def spawn_zombie(self):
        """Spawns a random zombie type around the perimeter of the map."""
        # Frame rate defense: don't spawn if too many active zombies
        if len(self.zombies) >= self.max_active_zombies:
            return
            
        # Select type based on wave progression
        roll = random.random()
        zombie_type = "normal"
        
        if self.wave >= 5:
            if roll < 0.20:
                zombie_type = "tank"
            elif roll < 0.50:
                zombie_type = "fast"
        elif self.wave >= 3:
            if roll < 0.08:
                zombie_type = "tank"
            elif roll < 0.30:
                zombie_type = "fast"
        elif self.wave >= 2:
            if roll < 0.15:
                zombie_type = "fast"

        # Find perimeter coordinates
        # Edge select: 0 = Top, 1 = Bottom, 2 = Left, 3 = Right
        edge = random.randint(0, 3)
        sx, sy = 0.0, 0.0
        
        if edge == 0:  # Top
            sx = random.uniform(50, self.map.width - 50)
            sy = 50.0
        elif edge == 1:  # Bottom
            sx = random.uniform(50, self.map.width - 50)
            sy = self.map.height - 50.0
        elif edge == 2:  # Left
            sx = 50.0
            sy = random.uniform(50, self.map.height - 50)
        else:  # Right
            sx = self.map.width - 50.0
            sy = random.uniform(50, self.map.height - 50)

        # Ensure coordinate is valid (not inside a wall)
        temp_rect = pygame.Rect(int(sx - 20), int(sy - 20), 40, 40)
        if self.map.check_collision(temp_rect):
            # Fallback to coordinate near center if edge collides
            sx = self.map.width / 2.0 + random.uniform(-100, 100)
            sy = self.map.height / 2.0 + random.uniform(-100, 100)

        # Create Zombie
        if zombie_type == "fast":
            self.zombies.append(FastZombie(sx, sy))
        elif zombie_type == "tank":
            self.zombies.append(TankZombie(sx, sy))
        else:
            self.zombies.append(NormalZombie(sx, sy))
            
        self.zombies_spawned_this_wave += 1

    def handle_events(self):
        """Processes input key/mouse clicks and transitions game states."""
        now = pygame.time.get_ticks()
        for event in pygame.event.get_down() if hasattr(pygame.event, 'get_down') else pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                # ----------------- MENU KEYS -----------------
                if self.state == "MENU":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.sound_manager.play('click')
                        self.reset_game()
                        self.state = "PLAYING"
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        
                # ----------------- PLAYING KEYS -----------------
                elif self.state == "PLAYING":
                    if event.key == pygame.K_p:
                        self.sound_manager.play('click')
                        self.sound_manager.pause_music()
                        self.pause_start_ticks = now
                        self.state = "PAUSED"
                    elif event.key == pygame.K_ESCAPE:
                        self.sound_manager.play('click')
                        self.sound_manager.pause_music()
                        self.pause_start_ticks = now
                        self.state = "PAUSED"
                    elif event.key == pygame.K_r:
                        self.player.reload(now, self.sound_manager)
                        
                # ----------------- PAUSED KEYS -----------------
                elif self.state == "PAUSED":
                    if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                        self.sound_manager.play('click')
                        self.sound_manager.unpause_music()
                        self.game_paused_ticks += (now - self.pause_start_ticks)
                        self.state = "PLAYING"
                    elif event.key == pygame.K_ESCAPE:
                        self.sound_manager.play('click')
                        self.state = "MENU"
                        
                # ----------------- GAMEOVER / VICTORY KEYS -----------------
                elif self.state in ["GAMEOVER", "VICTORY"]:
                    if event.key == pygame.K_r:
                        self.sound_manager.play('click')
                        self.reset_game()
                        self.state = "PLAYING"
                    elif event.key == pygame.K_ESCAPE:
                        self.sound_manager.play('click')
                        self.state = "MENU"

            # ----------------- PLAYING MOUSE PRESS -----------------
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "PLAYING":
                    if event.button == 1:  # Left click
                        bullet, result = self.player.shoot(now)
                        if result == "shoot":
                            self.bullets.append(bullet)
                            self.sound_manager.play('shoot')
                            # Emit muzzle flash sparks
                            barrel_len = self.player.size + 12
                            flash_x = self.player.x + math.cos(self.player.angle) * barrel_len
                            flash_y = self.player.y + math.sin(self.player.angle) * barrel_len
                            self.particle_system.emit_spark(flash_x, flash_y, self.player.angle, COLOR_SPARK, count=6)
                        elif result == "empty":
                            self.sound_manager.play('click')

    def update(self):
        """Main game step running physics, collisions, state updates, and particle simulations."""
        if self.state != "PLAYING":
            return
            
        now = pygame.time.get_ticks()
        
        # 1. Update Game Timer
        self.elapsed_time = (now - self.start_ticks - self.game_paused_ticks) / 1000.0

        # 2. Camera Tracking (center smoothly on player with bounds clamp)
        target_cam_x = self.player.x - SCREEN_WIDTH / 2.0
        target_cam_y = self.player.y - SCREEN_HEIGHT / 2.0
        
        # Linear interpolation (lerp) for smooth camera tracking
        self.camera_x += (target_cam_x - self.camera_x) * 0.1
        self.camera_y += (target_cam_y - self.camera_y) * 0.1
        
        # Clamp camera to map bounds
        self.camera_x = max(0.0, min(self.map.width - SCREEN_WIDTH, self.camera_x))
        self.camera_y = max(0.0, min(self.map.height - SCREEN_HEIGHT, self.camera_y))

        # Camera Shake Decay
        if self.screen_shake > 0:
            self.screen_shake -= 1

        # 3. Update Player input movement
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        self.player.update(keys, mouse_pos, self.camera_x, self.camera_y, self.map, now, self.particle_system)

        # 4. Spawning Zombies check
        if self.zombies_spawned_this_wave < self.zombies_needed_to_spawn:
            self.zombie_spawn_timer += 16.67  # Milliseconds approx per frame
            if self.zombie_spawn_timer >= self.zombie_spawn_cooldown:
                self.spawn_zombie()
                self.zombie_spawn_timer = 0
                # Growl sound occasionally
                if random.random() < 0.12:
                    self.sound_manager.play('growl')

        # 5. Update Bullets
        for b in self.bullets:
            b.update()
            # Wall Collision checking
            if self.map.check_collision(b.rect):
                b.to_remove = True
                # Spark spray opposite to flight angle
                self.particle_system.emit_spark(b.x, b.y, b.angle + math.pi, COLOR_SPARK, count=4)
                
        # Clean dead bullets
        self.bullets = [b for b in self.bullets if not b.to_remove]

        # 6. Update NPCs (Rescue survivors checking & infection updates)
        npcs_to_keep = []
        for npc in self.npcs:
            recruit = npc.update(self.player, self.map, now)
            if recruit:
                self.sound_manager.play('click')
                
            # A. Safe Zone Rescue Check
            if npc.state == "following" and self.map.safe_zone.contains(npc.rect):
                # Rescued successfully!
                self.rescued_count += 1
                self.score += npc.stats.get('rescue_points', 1000) if hasattr(npc, 'stats') else 1000
                # Heal player
                self.player.health = min(PLAYER_MAX_HEALTH, self.player.health + 20)
                
                # Emit green particles
                self.particle_system.emit_rescue(npc.x, npc.y, COLOR_UI_GREEN, count=15)
                self.sound_manager.play('rescue')
                # Skip adding to keep list (removed from game)
                continue
                
            # B. Mutating check
            if npc.has_turned:
                # Mutate to fast zombie (cooler and scarier!)
                self.zombies.append(FastZombie(npc.x, npc.y))
                self.particle_system.emit_blood(npc.x, npc.y, random.uniform(0, 2*math.pi), COLOR_BLOOD, count=15)
                self.sound_manager.play('infection')
                # Skip adding to keep list
                continue
                
            npcs_to_keep.append(npc)
        self.npcs = npcs_to_keep

        # 7. Update Zombies
        for z in self.zombies:
            z.update(self.player, self.npcs, self.map, now)
            
            # Collision checks: Zombie hits Player
            if z.rect.colliderect(self.player.rect):
                if now - z.last_attack_time > z.attack_cooldown:
                    self.player.health = max(0, self.player.health - z.damage)
                    z.last_attack_time = now
                    self.sound_manager.play('hurt')
                    self.screen_shake = 10  # trigger shake
                    
                    # Spawn damage sparks/blood at player pos
                    self.particle_system.emit_blood(self.player.x, self.player.y, z.angle, COLOR_BLOOD, count=5)
                    
                    if self.player.health <= 0:
                        self.state = "GAMEOVER"
                        self.ui_manager.update_high_score(self.score)
                        self.sound_manager.stop_music()
                        
            # Collision checks: Zombie hits NPC
            for npc in self.npcs:
                if not npc.is_infected and z.rect.colliderect(npc.rect):
                    if now - z.last_attack_time > z.attack_cooldown:
                        npc.infect()
                        z.last_attack_time = now
                        self.sound_manager.play('infection')
                        # Spray blood at NPC pos
                        self.particle_system.emit_blood(npc.x, npc.y, z.angle, COLOR_BLOOD, count=5)

        # 8. Bullet vs Zombie Collisions
        for b in self.bullets:
            for z in self.zombies:
                if b.rect.colliderect(z.rect):
                    b.to_remove = True
                    is_dead = z.take_damage(b.damage)
                    
                    # Blood spray opposite to bullet path
                    self.particle_system.emit_blood(z.x, z.y, b.angle, COLOR_BLOOD, count=6)
                    
                    if is_dead:
                        self.score += z.points
                        # Add blood stains on floor
                        self.particle_system.add_blood_stain(z.x, z.y, z.size * 0.7, COLOR_BLOOD)
                        
                        # Loot Drop trigger
                        if random.random() < LOOT_DROP_CHANCE:
                            self.loots.append(Loot(z.x, z.y))
                            
                        # Remove zombie
                        if z in self.zombies:
                            self.zombies.remove(z)
                    break

        # 9. Update Loot Collections
        loots_to_keep = []
        for loot in self.loots:
            loot.update()
            if loot.rect.colliderect(self.player.rect):
                # Collect loot!
                self.sound_manager.play('loot')
                self.apply_loot(loot)
                
                # Emit color matched sparkle sparks
                self.particle_system.emit_spark(loot.x, loot.y, 0.0, loot.color, count=8)
                continue
            if not loot.to_remove:
                loots_to_keep.append(loot)
        self.loots = loots_to_keep

        # 10. Update Particles
        self.particle_system.update()

        # 11. Wave Clear Verification
        # If all zombies of wave are spawned and killed
        if self.zombies_spawned_this_wave >= self.zombies_needed_to_spawn and len(self.zombies) == 0:
            if self.wave < 10:
                self.wave += 1
                self.start_wave(self.wave)
                self.score += 500  # Wave reward
            else:
                # Wave 10 cleared: Escape zone active!
                if not self.escape_active:
                    self.escape_active = True
                    print("All waves cleared! Reach escape zone in bottom-right grid sector.")

        # 12. Escape Zone check
        if self.escape_active and self.escape_rect.colliderect(self.player.rect):
            self.score += self.escape_points_reward
            # Add survivors count bonus
            self.score += self.rescued_count * 2000
            self.state = "VICTORY"
            self.ui_manager.update_high_score(self.score)
            self.sound_manager.stop_music()

    def apply_loot(self, loot):
        """Applies loot statistics directly to the player."""
        if loot.type == "health":
            self.player.health = min(PLAYER_MAX_HEALTH, self.player.health + loot.val)
        elif loot.type == "ammo":
            self.player.reserve_ammo += loot.val
        elif loot.type == "food":
            # restamina and bonus score
            self.player.stamina = min(100, self.player.stamina + 20)
            self.score += loot.val
        elif loot.type == "coin":
            self.score += loot.val

    def draw(self):
        """Renders the screen frame depending on game states."""
        if self.state == "MENU":
            self.ui_manager.draw_start_menu()
            pygame.display.flip()
            return
            
        # Render Game Layer
        self.screen.fill(COLOR_BG)
        
        # Calculate camera shake offsets
        cam_offset_x = 0
        cam_offset_y = 0
        if self.screen_shake > 0 and self.state == "PLAYING":
            cam_offset_x = random.randint(-self.screen_shake, self.screen_shake)
            cam_offset_y = random.randint(-self.screen_shake, self.screen_shake)
            
        camera_draw_x = self.camera_x + cam_offset_x
        camera_draw_y = self.camera_y + cam_offset_y

        # --- A. Draw Map Floor Grid & Safe Zone ---
        self.map.draw(self.screen, camera_draw_x, camera_draw_y)

        # --- B. Draw Blood Stains (Static Ground elements) ---
        self.particle_system.draw_ground(self.screen, camera_draw_x, camera_draw_y)

        # --- C. Draw Escape Zone if active ---
        if self.escape_active:
            # Pulsing color
            pulse = math.sin(pygame.time.get_ticks() * 0.007) * 40
            color = (int(max(100, 230 + pulse)), int(max(100, 150 + pulse)), 20)
            
            e_rect_cam = pygame.Rect(
                self.escape_rect.x - camera_draw_x,
                self.escape_rect.y - camera_draw_y,
                self.escape_rect.width,
                self.escape_rect.height
            )
            # Fill
            e_surf = pygame.Surface((self.escape_rect.width, self.escape_rect.height), pygame.SRCALPHA)
            e_surf.fill((color[0], color[1], color[2], 70))
            self.screen.blit(e_surf, (e_rect_cam.x, e_rect_cam.y))
            # Border
            pygame.draw.rect(self.screen, color, e_rect_cam, 4)
            
            # Helipad H draw
            font_h = pygame.font.SysFont("Courier New", 72, bold=True)
            text_surf = font_h.render("ESCAPE", True, color)
            text_rect = text_surf.get_rect(center=(e_rect_cam.centerx, e_rect_cam.centery))
            self.screen.blit(text_surf, text_rect)
            
            # Compass overlay to show direction to escape if offscreen
            dx = self.escape_rect.centerx - self.player.x
            dy = self.escape_rect.centery - self.player.y
            dist = math.hypot(dx, dy)
            if dist > 400.0:  # Only draw arrow if escape is somewhat far
                angle = math.atan2(dy, dx)
                arrow_length = 50
                arrow_center_x = SCREEN_WIDTH - 80
                arrow_center_y = SCREEN_HEIGHT // 2
                
                # Draw small compass base
                pygame.draw.circle(self.screen, (30, 30, 40), (arrow_center_x, arrow_center_y), 32)
                pygame.draw.circle(self.screen, color, (arrow_center_x, arrow_center_y), 32, 2)
                
                # Draw arrow point
                tip_x = arrow_center_x + math.cos(angle) * 22
                tip_y = arrow_center_y + math.sin(angle) * 22
                
                wing_l_x = arrow_center_x + math.cos(angle + 2.5) * 14
                wing_l_y = arrow_center_y + math.sin(angle + 2.5) * 14
                
                wing_r_x = arrow_center_x + math.cos(angle - 2.5) * 14
                wing_r_y = arrow_center_y + math.sin(angle - 2.5) * 14
                
                pygame.draw.polygon(self.screen, color, [
                    (tip_x, tip_y),
                    (wing_l_x, wing_l_y),
                    (arrow_center_x, arrow_center_y),
                    (wing_r_x, wing_r_y)
                ])

        # --- D. Draw Loot items ---
        for loot in self.loots:
            loot.draw(self.screen, camera_draw_x, camera_draw_y)

        # --- E. Draw Friendly NPCs ---
        for npc in self.npcs:
            npc.draw(self.screen, camera_draw_x, camera_draw_y)

        # --- F. Draw Zombies ---
        for z in self.zombies:
            z.draw(self.screen, camera_draw_x, camera_draw_y)

        # --- G. Draw Bullets ---
        for b in self.bullets:
            b.draw(self.screen, camera_draw_x, camera_draw_y)

        # --- H. Draw Player ---
        self.player.draw(self.screen, camera_draw_x, camera_draw_y)

        # --- I. Draw Active Particles ---
        self.particle_system.draw_active(self.screen, camera_draw_x, camera_draw_y)

        # --- J. Draw HUD stats ---
        self.ui_manager.draw_hud(
            player=self.player, 
            wave_num=self.wave, 
            rescued_count=self.rescued_count, 
            score=self.score, 
            elapsed_time=self.elapsed_time
        )

        # --- K. Menu overlays ---
        if self.state == "PAUSED":
            self.ui_manager.draw_pause_menu()
        elif self.state == "GAMEOVER":
            self.ui_manager.draw_game_over(self.score, self.wave - 1, self.rescued_count)
        elif self.state == "VICTORY":
            self.ui_manager.draw_victory_screen(self.score, self.rescued_count, self.elapsed_time)

        pygame.display.flip()

    def run(self):
        """Core gameplay tick loop."""
        while self.running:
            # Cap at 60 FPS
            self.clock.tick(60)
            
            # 1. Event processing
            self.handle_events()
            
            # 2. Physics & Logic Step
            self.update()
            
            # 3. Graphics Rendering Step
            self.draw()
            
        pygame.quit()
