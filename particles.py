# particles.py
"""
Particle effects system for muzzle flashes, sparks, blood splatters, and trails.
Includes ground staining mechanics for persistent visual debris.
"""

import pygame
import random
import math

class Particle:
    def __init__(self, x, y, dx, dy, color, size, lifetime, decay_speed=1.0, friction=0.98):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.size = size
        self.lifetime = lifetime  # remaining lifetime in frames
        self.max_lifetime = lifetime
        self.decay_speed = decay_speed
        self.friction = friction

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dx *= self.friction
        self.dy *= self.friction
        self.lifetime -= self.decay_speed

    def draw(self, surface, camera_x, camera_y):
        if self.lifetime <= 0:
            return
            
        # Calculate fade out factor
        life_pct = self.lifetime / self.max_lifetime
        alpha = int(life_pct * 255)
        alpha = max(0, min(255, alpha))
        
        # Shrink particle over time
        current_size = int(max(1, self.size * life_pct))
        
        # Screen position
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Create an alpha-enabled surface for transparent particles
        # (This is standard Pygame practice for drawing smooth alpha circles)
        surf_sz = current_size * 2
        if surf_sz < 2:
            surf_sz = 2
            
        temp_surf = pygame.Surface((surf_sz, surf_sz), pygame.SRCALPHA)
        # Draw circle on the temp surface, centered at (current_size, current_size)
        pygame.draw.circle(
            temp_surf, 
            (self.color[0], self.color[1], self.color[2], alpha), 
            (current_size, current_size), 
            current_size
        )
        # Blit the temp surface onto the main display
        surface.blit(temp_surf, (screen_x - current_size, screen_y - current_size))


class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.blood_stains = []  # Static blood pools on the ground

    def emit_spark(self, x, y, angle, color, count=5):
        """Emits sparks from a gunshot muzzle flash or wall impact."""
        for _ in range(count):
            # Spread angle slightly
            spread_angle = angle + random.uniform(-0.4, 0.4)
            speed = random.uniform(3.0, 7.0)
            dx = math.cos(spread_angle) * speed
            dy = math.sin(spread_angle) * speed
            size = random.uniform(2.5, 4.5)
            lifetime = random.uniform(12, 22)
            self.particles.append(Particle(x, y, dx, dy, color, size, lifetime, friction=0.92))

    def emit_blood(self, x, y, angle, color, count=10):
        """Emits spray of blood particles on hit."""
        for _ in range(count):
            # Spread angle (wider spray behind hit direction)
            spread_angle = angle + random.uniform(-0.7, 0.7)
            speed = random.uniform(1.5, 5.0)
            dx = math.cos(spread_angle) * speed
            dy = math.sin(spread_angle) * speed
            size = random.uniform(3.0, 6.0)
            lifetime = random.uniform(35, 65)
            
            # Blood has higher friction, slows down quickly
            self.particles.append(Particle(x, y, dx, dy, color, size, lifetime, friction=0.94))
            
            # Sporadically register ground stains
            if random.random() < 0.3:
                stain_dist = speed * random.uniform(5, 12)
                stain_x = x + math.cos(spread_angle) * stain_dist
                stain_y = y + math.sin(spread_angle) * stain_dist
                self.add_blood_stain(stain_x, stain_y, random.uniform(3.0, 7.0), color)

    def emit_rescue(self, x, y, color, count=12):
        """Emits soft floating neon sparkles when a survivor reaches safety."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.6, 2.0)
            dx = math.cos(angle) * speed
            # Drift upwards slightly
            dy = math.sin(angle) * speed - random.uniform(0.8, 2.0)
            size = random.uniform(3.0, 5.5)
            lifetime = random.uniform(40, 80)
            self.particles.append(Particle(x, y, dx, dy, color, size, lifetime, decay_speed=1.0, friction=0.97))

    def emit_trail(self, x, y, color, count=1):
        """Emits light trail for player running/sprinting."""
        for _ in range(count):
            dx = random.uniform(-0.4, 0.4)
            dy = random.uniform(-0.4, 0.4)
            size = random.uniform(2.0, 3.5)
            lifetime = random.uniform(10, 18)
            self.particles.append(Particle(x, y, dx, dy, color, size, lifetime, decay_speed=1.0, friction=0.98))

    def add_blood_stain(self, x, y, size, color):
        """Adds a static blood stain to the ground layer."""
        # Darken the blood stain color slightly to look dried/absorbed
        stain_color = (
            max(40, color[0] - 50),
            max(10, color[1] - 50),
            max(10, color[2] - 50)
        )
        self.blood_stains.append({
            'x': x + random.uniform(-5.0, 5.0),
            'y': y + random.uniform(-5.0, 5.0),
            'size': int(size),
            'color': stain_color
        })
        # Prevent memory leaks by capping the stain count
        if len(self.blood_stains) > 200:
            self.blood_stains.pop(0)

    def update(self):
        """Updates particle lifetime and motion."""
        for p in self.particles:
            p.update()
        # Keep only active particles
        self.particles = [p for p in self.particles if p.lifetime > 0]

    def draw_ground(self, surface, camera_x, camera_y):
        """Draws persistent stains on the floor (underneath players/zombies)."""
        for s in self.blood_stains:
            # Quick screen bounds check before drawing to optimize
            pos_x = int(s['x'] - camera_x)
            pos_y = int(s['y'] - camera_y)
            # Offset by radius to make sure offscreen items aren't drawn
            r = s['size']
            if -r < pos_x < surface.get_width() + r and -r < pos_y < surface.get_height() + r:
                pygame.draw.circle(surface, s['color'], (pos_x, pos_y), r)

    def draw_active(self, surface, camera_x, camera_y):
        """Draws active floating particles with alpha transparency."""
        for p in self.particles:
            p.draw(surface, camera_x, camera_y)

    def clear(self):
        """Resets the particle system."""
        self.particles.clear()
        self.blood_stains.clear()
