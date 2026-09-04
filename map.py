# map.py
"""
Game map system representing the infected city environment.
Defines walls, buildings, safe zones, collision checks, and entity sliding-movement resolution.
"""

import pygame
import random
from config import (
    TILE_SIZE, MAP_COLS, MAP_ROWS, COLOR_WALL, COLOR_BG,
    COLOR_SAFE_ZONE, COLOR_SAFE_ZONE_BORDER, SAFE_ZONE_RECT
)

class Map:
    def __init__(self):
        self.width = MAP_COLS * TILE_SIZE    # 1920
        self.height = MAP_ROWS * TILE_SIZE  # 1536
        
        self.walls = []
        self.safe_zone = pygame.Rect(*SAFE_ZONE_RECT)
        
        # Build the map
        self._generate_map()

    def _generate_map(self):
        """Generates outer boundary walls, buildings, and obstacles."""
        # 1. Outer Boundaries (thick rectangles to prevent out-of-bounds)
        thickness = 100
        # Top
        self.walls.append(pygame.Rect(-thickness, -thickness, self.width + thickness * 2, thickness))
        # Bottom
        self.walls.append(pygame.Rect(-thickness, self.height, self.width + thickness * 2, thickness))
        # Left
        self.walls.append(pygame.Rect(-thickness, 0, thickness, self.height))
        # Right
        self.walls.append(pygame.Rect(self.width, 0, thickness, self.height))

        # 2. Buildings (City Blocks)
        # Defined building structures that leave nice streets and narrow alleys.
        # Safe zone occupies (100, 100, 350, 350) - we avoid building inside/near it.
        building_rects = [
            # Top row blocks (skipping safe zone)
            pygame.Rect(550, 100, 220, 280),
            pygame.Rect(900, 80, 250, 220),
            pygame.Rect(1250, 120, 280, 240),
            pygame.Rect(1650, 100, 180, 300),

            # Upper middle row blocks
            pygame.Rect(100, 550, 320, 160),
            pygame.Rect(550, 500, 240, 240),
            pygame.Rect(900, 420, 200, 280),
            pygame.Rect(1220, 480, 240, 220),
            pygame.Rect(1580, 520, 220, 260),

            # Lower middle row blocks
            pygame.Rect(150, 850, 240, 240),
            pygame.Rect(500, 850, 320, 180),
            pygame.Rect(950, 800, 180, 250),
            pygame.Rect(1250, 820, 260, 200),
            pygame.Rect(1620, 900, 200, 240),

            # Bottom row blocks
            pygame.Rect(100, 1200, 280, 220),
            pygame.Rect(500, 1150, 240, 260),
            pygame.Rect(860, 1180, 280, 200),
            pygame.Rect(1260, 1140, 240, 260),
            pygame.Rect(1600, 1250, 220, 180),
        ]
        self.walls.extend(building_rects)

        # 3. Add small scatter obstacles (crates/barricades) to block straight paths
        scatter_obstacles = [
            pygame.Rect(480, 250, 40, 40),
            pygame.Rect(830, 200, 40, 40),
            pygame.Rect(1180, 180, 40, 40),
            pygame.Rect(480, 600, 40, 40),
            pygame.Rect(820, 550, 40, 40),
            pygame.Rect(1150, 600, 40, 40),
            pygame.Rect(1500, 550, 40, 40),
            pygame.Rect(430, 920, 40, 40),
            pygame.Rect(880, 900, 40, 40),
            pygame.Rect(1180, 880, 40, 40),
            pygame.Rect(1550, 950, 40, 40),
        ]
        self.walls.extend(scatter_obstacles)

    def check_collision(self, rect):
        """Returns True if the given rect collides with any wall."""
        for wall in self.walls:
            if rect.colliderect(wall):
                return True
        return False

    def check_line_of_sight(self, start_pos, end_pos):
        """
        Simple raycasting / line-of-sight check.
        Returns True if there are NO walls blocking the line between start_pos and end_pos.
        """
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Calculate steps based on distance to be granular but efficient
        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            return True
            
        steps = int(dist / 16)  # Check every 16 pixels
        if steps == 0:
            steps = 1
            
        for i in range(1, steps + 1):
            t = i / steps
            cx = x1 + dx * t
            cy = y1 + dy * t
            # Check if this point lies inside any wall
            for wall in self.walls:
                if wall.collidepoint(cx, cy):
                    return False
        return True

    def resolve_collision(self, entity, old_x, old_y):
        """
        Resolves collisions by reverting movement axis-by-axis, allowing sliding.
        `entity` must have a `.rect` (pygame.Rect) and attributes `.x` and `.y` (floats).
        """
        # 1. Resolve X axis
        entity.rect.x = int(entity.x)
        if self.check_collision(entity.rect):
            # Revert X
            entity.x = old_x
            entity.rect.x = int(old_x)
            
        # 2. Resolve Y axis
        entity.rect.y = int(entity.y)
        if self.check_collision(entity.rect):
            # Revert Y
            entity.y = old_y
            entity.rect.y = int(old_y)

    def draw(self, surface, camera_x, camera_y):
        """Draws the floor grid, the buildings, and the safe zone."""
        # 1. Draw Grid lines on floor for spatial orientation
        grid_color = (25, 27, 36)
        start_col = int(camera_x // TILE_SIZE) - 1
        end_col = start_col + (surface.get_width() // TILE_SIZE) + 3
        start_row = int(camera_y // TILE_SIZE) - 1
        end_row = start_row + (surface.get_height() // TILE_SIZE) + 3

        # Clamp grid boundaries
        start_col = max(0, start_col)
        end_col = min(MAP_COLS, end_col)
        start_row = max(0, start_row)
        end_row = min(MAP_ROWS, end_row)

        for col in range(start_col, end_col + 1):
            x = col * TILE_SIZE - camera_x
            pygame.draw.line(surface, grid_color, (x, 0), (x, surface.get_height()))
        for row in range(start_row, end_row + 1):
            y = row * TILE_SIZE - camera_y
            pygame.draw.line(surface, grid_color, (0, y), (surface.get_width(), y))

        # 2. Draw Safe Zone
        # Safe zone fill (needs alpha blend)
        sz_surface = pygame.Surface((self.safe_zone.width, self.safe_zone.height), pygame.SRCALPHA)
        sz_surface.fill(COLOR_SAFE_ZONE)
        surface.blit(sz_surface, (self.safe_zone.x - camera_x, self.safe_zone.y - camera_y))
        
        # Safe zone outline
        sz_outline = pygame.Rect(
            self.safe_zone.x - camera_x, 
            self.safe_zone.y - camera_y, 
            self.safe_zone.width, 
            self.safe_zone.height
        )
        pygame.draw.rect(surface, COLOR_SAFE_ZONE_BORDER, sz_outline, 3)

        # 3. Draw Walls / Buildings (only if on screen to save rendering cycles)
        screen_rect = pygame.Rect(camera_x, camera_y, surface.get_width(), surface.get_height())
        for wall in self.walls:
            if wall.colliderect(screen_rect):
                # Adjust rect to camera coords
                cam_rect = pygame.Rect(wall.x - camera_x, wall.y - camera_y, wall.width, wall.height)
                # Draw building body
                pygame.draw.rect(surface, COLOR_WALL, cam_rect)
                # Draw neon highlights on wall edges for stylized contrast
                pygame.draw.rect(surface, (53, 59, 72), cam_rect, 1)  # outer highlight
                # Add a subtle bevel effect or top lit edge
                pygame.draw.line(surface, (71, 79, 99), cam_rect.topleft, cam_rect.topright, 2)
                pygame.draw.line(surface, (71, 79, 99), cam_rect.topleft, cam_rect.bottomleft, 2)
