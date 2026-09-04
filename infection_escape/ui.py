# ui.py
"""
UIManager class handling HUD rendering, menu states, text styling, and high score systems.
Implements dark glassmorphism panel styling, layout calculations, and highscore saving.
"""

import pygame
import os
from config import (
    COLOR_TEXT_WHITE, COLOR_TEXT_MUTED, COLOR_PANEL_BG, COLOR_UI_GREEN,
    COLOR_UI_RED, COLOR_UI_YELLOW, HIGH_SCORE_FILE, COLOR_BG, COLOR_PLAYER,
    COLOR_ZOMBIE_FAST, COLOR_NPC
)

class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Load fonts
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Courier New", 52, bold=True)
        self.font_subtitle = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_hud_large = pygame.font.SysFont("Courier New", 20, bold=True)
        self.font_hud_small = pygame.font.SysFont("Arial", 14, bold=True)
        self.font_menu = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_stats = pygame.font.SysFont("Courier New", 16, bold=True)
        
        # High Score state
        self.high_score = self.load_high_score()
        self.new_high_score_achieved = False

    def load_high_score(self):
        """Loads the high score from highscores.txt, returning 0 if missing/corrupt."""
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, "r") as f:
                    content = f.read().strip()
                    if content.isdigit():
                        return int(content)
            except Exception as e:
                print(f"Error loading high score: {e}")
        return 0

    def update_high_score(self, score):
        """Saves current score to highscores.txt if it exceeds the record."""
        if score > self.high_score:
            self.high_score = score
            self.new_high_score_achieved = True
            try:
                with open(HIGH_SCORE_FILE, "w") as f:
                    f.write(str(score))
                print(f"New high score saved: {score}")
            except Exception as e:
                print(f"Error saving high score: {e}")
        else:
            self.new_high_score_achieved = False

    def draw_glass_panel(self, rect, alpha=190, border_color=(75, 78, 105)):
        """Draws a premium semi-transparent dark container rect with border outline."""
        panel_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel_surf.fill((22, 22, 33, alpha))
        
        # Border inside the alpha surface
        pygame.draw.rect(panel_surf, border_color + (255,), (0, 0, rect.width, rect.height), 2)
        self.screen.blit(panel_surf, (rect.x, rect.y))

    def draw_text_with_shadow(self, text, font, color, center_pos, shadow_color=(10, 10, 15)):
        """Renders text with a subtle 3D-like drop shadow offset by 2px."""
        text_surf_shadow = font.render(text, True, shadow_color)
        text_surf_main = font.render(text, True, color)
        
        rect_shadow = text_surf_shadow.get_rect(center=(center_pos[0] + 2, center_pos[1] + 2))
        rect_main = text_surf_main.get_rect(center=center_pos)
        
        self.screen.blit(text_surf_shadow, rect_shadow)
        self.screen.blit(text_surf_main, rect_main)

    def draw_hud(self, player, wave_num, rescued_count, score, elapsed_time):
        """Draws HUD stats, HP bar, stamina bar, and ammunition counts."""
        
        # 1. Top HUD Glass Panel (Score, Wave, Rescued, Time)
        hud_panel_rect = pygame.Rect(15, 15, self.width - 30, 48)
        self.draw_glass_panel(hud_panel_rect, alpha=200)
        
        # Formatted details
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_str = f"SURVIVED: {minutes:02d}:{seconds:02d}"
        
        # Draw stats elements inside the top bar
        # Wave (Left)
        wave_txt = self.font_hud_large.render(f"WAVE {wave_num:02d}", True, COLOR_PLAYER)
        self.screen.blit(wave_txt, (30, 28))
        
        # Rescued (Left-Middle)
        resc_txt = self.font_hud_large.render(f"RESCUED: {rescued_count}", True, COLOR_UI_GREEN)
        self.screen.blit(resc_txt, (200, 28))
        
        # Time (Middle-Right)
        time_txt = self.font_hud_large.render(time_str, True, COLOR_TEXT_WHITE)
        self.screen.blit(time_txt, (self.width // 2 - 100, 28))
        
        # Score (Right)
        score_txt = self.font_hud_large.render(f"SCORE: {score:05d}", True, COLOR_UI_YELLOW)
        score_rect = score_txt.get_rect(right=self.width - 30, top=28)
        self.screen.blit(score_txt, score_rect)

        # 2. Bottom HUD Panel (Health, Stamina, Ammo)
        bottom_panel_h = 75
        bottom_panel_rect = pygame.Rect(15, self.height - bottom_panel_h - 15, self.width - 30, bottom_panel_h)
        self.draw_glass_panel(bottom_panel_rect, alpha=210)
        
        # --- A. Health Bar ---
        hb_x, hb_y = 35, self.height - bottom_panel_h + 5
        hb_w, hb_h = 240, 16
        # Background
        pygame.draw.rect(self.screen, (40, 20, 20), (hb_x, hb_y, hb_w, hb_h))
        # Fill ratio
        hp_ratio = max(0, min(100, player.health)) / 100.0
        hp_color = COLOR_UI_GREEN if hp_ratio > 0.4 else COLOR_UI_RED
        pygame.draw.rect(self.screen, hp_color, (hb_x, hb_y, int(hb_w * hp_ratio), hb_h))
        pygame.draw.rect(self.screen, COLOR_TEXT_MUTED, (hb_x, hb_y, hb_w, hb_h), 1)  # border
        
        hp_text = self.font_hud_small.render(f"HEALTH: {int(player.health)} / 100", True, COLOR_TEXT_WHITE)
        self.screen.blit(hp_text, (hb_x, hb_y - 18))

        # --- B. Stamina Bar ---
        sb_x, sb_y = 300, self.height - bottom_panel_h + 5
        sb_w, sb_h = 240, 16
        # Background
        pygame.draw.rect(self.screen, (30, 30, 30), (sb_x, sb_y, sb_w, sb_h))
        # Fill ratio
        st_ratio = max(0, min(100, player.stamina)) / 100.0
        pygame.draw.rect(self.screen, COLOR_UI_YELLOW, (sb_x, sb_y, int(sb_w * st_ratio), sb_h))
        pygame.draw.rect(self.screen, COLOR_TEXT_MUTED, (sb_x, sb_y, sb_w, sb_h), 1)  # border
        
        st_text = self.font_hud_small.render(f"STAMINA: {int(player.stamina)}%", True, COLOR_TEXT_WHITE)
        self.screen.blit(st_text, (sb_x, sb_y - 18))

        # --- C. Ammo Info ---
        ammo_x = self.width - 150
        ammo_y = self.height - bottom_panel_h + 12
        
        # Ammo icon (small circle with cross/bullets representation)
        magazine_str = f"{player.magazine}"
        if player.is_reloading:
            magazine_str = "RELOAD"
            
        ammo_str = f"{magazine_str} / {player.reserve_ammo}"
        ammo_color = COLOR_UI_YELLOW if player.magazine > 0 else COLOR_UI_RED
        
        ammo_txt = self.font_hud_large.render(ammo_str, True, ammo_color)
        self.screen.blit(ammo_txt, (ammo_x, ammo_y))
        
        label_txt = self.font_hud_small.render("AMMO RESERVES", True, COLOR_TEXT_MUTED)
        self.screen.blit(label_txt, (ammo_x, ammo_y - 18))

    def draw_start_menu(self):
        """Draws the main titles, settings, and instructions menu."""
        # Clean background overlay
        self.screen.fill(COLOR_BG)
        
        # 1. Decorative grid overlay lines just on start screen for styling
        for x in range(0, self.width, 64):
            pygame.draw.line(self.screen, (22, 24, 32), (x, 0), (x, self.height))
        for y in range(0, self.height, 64):
            pygame.draw.line(self.screen, (22, 24, 32), (0, y), (self.width, y))
            
        # Draw Main Panel
        panel_w = 600
        panel_h = 520
        panel_rect = pygame.Rect((self.width - panel_w) // 2, (self.height - panel_h) // 2, panel_w, panel_h)
        self.draw_glass_panel(panel_rect, alpha=230, border_color=(60, 110, 160))

        # Title
        self.draw_text_with_shadow("INFECTION ESCAPE", self.font_title, COLOR_UI_RED, (self.width // 2, 200))
        
        # High score display
        hs_str = f"HIGH SCORE RECORD: {self.high_score:05d}"
        self.draw_text_with_shadow(hs_str, self.font_subtitle, COLOR_UI_YELLOW, (self.width // 2, 255))
        
        # Instructions Panel
        ins_y = 300
        inst_lines = [
            "--- SURVIVAL BLUEPRINT ---",
            "• Use [WASD] or Arrow keys to move around the infected sectors.",
            "• Hold [SHIFT] to Sprint (stamina will drain rapidly).",
            "• Aim with [MOUSE cursor] and Shoot using [LEFT CLICK].",
            "• Press [R] to reload magazine from ammunition reserve.",
            "• Walk near survivors (yellow) to recruit them. Bring them to",
            "  the Safe Zone (top-left green zone) to rescue them.",
            "• Warning: NPCs bitten by zombies turn into zombies after 8s!",
            "• Escape vehicle spawns after clear wave 10. Reach it to WIN."
        ]
        
        for idx, line in enumerate(inst_lines):
            color = COLOR_TEXT_WHITE if not line.startswith("---") else COLOR_PLAYER
            text = self.font_stats.render(line, True, color)
            self.screen.blit(text, (self.width // 2 - 250, ins_y + idx * 22))

        # Play Button Prompt
        self.draw_text_with_shadow("Press [SPACEBAR] or [ENTER] to Begin Survival", self.font_subtitle, COLOR_UI_GREEN, (self.width // 2, 540))
        self.draw_text_with_shadow("Press [ESC] to Quit", self.font_hud_small, COLOR_TEXT_MUTED, (self.width // 2, 580))

    def draw_pause_menu(self):
        """Draws the semi-transparent pause modal over current game frame."""
        # 1. Overlay fade surface
        fade_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        fade_surf.fill((10, 10, 15, 120))  # dark dim
        self.screen.blit(fade_surf, (0, 0))
        
        # 2. Main Box
        panel_w, panel_h = 350, 220
        panel_rect = pygame.Rect((self.width - panel_w) // 2, (self.height - panel_h) // 2, panel_w, panel_h)
        self.draw_glass_panel(panel_rect, alpha=230, border_color=COLOR_PLAYER)
        
        self.draw_text_with_shadow("SURVIVAL PAUSED", self.font_title, COLOR_PLAYER, (self.width // 2, self.height // 2 - 50))
        
        self.draw_text_with_shadow("Press [P] or [SPACE] to Resume", self.font_subtitle, COLOR_TEXT_WHITE, (self.width // 2, self.height // 2 + 20))
        self.draw_text_with_shadow("Press [ESC] to Exit to Main Menu", self.font_menu, COLOR_TEXT_MUTED, (self.width // 2, self.height // 2 + 60))

    def draw_game_over(self, score, wave, rescued):
        """Draws the final stats screen and prompts to restart."""
        # Fade background
        fade_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        fade_surf.fill((15, 10, 10, 180))  # Dim reddish
        self.screen.blit(fade_surf, (0, 0))
        
        # Panel
        panel_w, panel_h = 500, 380
        panel_rect = pygame.Rect((self.width - panel_w) // 2, (self.height - panel_h) // 2, panel_w, panel_h)
        self.draw_glass_panel(panel_rect, alpha=240, border_color=COLOR_UI_RED)
        
        self.draw_text_with_shadow("YOU WERE INFECTED", self.font_title, COLOR_UI_RED, (self.width // 2, self.height // 2 - 120))
        
        # Stats summary
        stat_y = self.height // 2 - 40
        self.draw_text_with_shadow(f"FINAL SCORE: {score:05d}", self.font_subtitle, COLOR_UI_YELLOW, (self.width // 2, stat_y))
        self.draw_text_with_shadow(f"WAVES COMPLETED: {wave}", self.font_subtitle, COLOR_TEXT_WHITE, (self.width // 2, stat_y + 35))
        self.draw_text_with_shadow(f"SURVIVORS ESCAPED: {rescued}", self.font_subtitle, COLOR_UI_GREEN, (self.width // 2, stat_y + 70))
        
        # New high score notification
        if self.new_high_score_achieved:
            self.draw_text_with_shadow("★ NEW SECTOR HIGH SCORE RECORD ★", self.font_subtitle, COLOR_UI_GREEN, (self.width // 2, stat_y + 110))
        else:
            self.draw_text_with_shadow(f"RECORD TO BEAT: {self.high_score:05d}", self.font_stats, COLOR_TEXT_MUTED, (self.width // 2, stat_y + 110))
            
        # Controls
        self.draw_text_with_shadow("Press [R] to Retry Sector Run", self.font_subtitle, COLOR_TEXT_WHITE, (self.width // 2, self.height // 2 + 115))
        self.draw_text_with_shadow("Press [ESC] for Main menu", self.font_menu, COLOR_TEXT_MUTED, (self.width // 2, self.height // 2 + 145))

    def draw_victory_screen(self, score, rescued, elapsed_time):
        """Draws the victory stats screen upon escaping map."""
        # Fade background
        fade_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        fade_surf.fill((10, 15, 10, 180))  # Dim greenish
        self.screen.blit(fade_surf, (0, 0))
        
        # Panel
        panel_w, panel_h = 500, 380
        panel_rect = pygame.Rect((self.width - panel_w) // 2, (self.height - panel_h) // 2, panel_w, panel_h)
        self.draw_glass_panel(panel_rect, alpha=240, border_color=COLOR_UI_GREEN)
        
        self.draw_text_with_shadow("SECTOR ESCAPED!", self.font_title, COLOR_UI_GREEN, (self.width // 2, self.height // 2 - 120))
        
        # Time calc
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        # Stats summary
        stat_y = self.height // 2 - 40
        self.draw_text_with_shadow(f"FINAL ESCAPE SCORE: {score:05d}", self.font_subtitle, COLOR_UI_YELLOW, (self.width // 2, stat_y))
        self.draw_text_with_shadow(f"SURVIVORS SAVED: {rescued}", self.font_subtitle, COLOR_TEXT_WHITE, (self.width // 2, stat_y + 35))
        self.draw_text_with_shadow(f"CLEAR TIME: {minutes:02d}:{seconds:02d}", self.font_subtitle, COLOR_TEXT_WHITE, (self.width // 2, stat_y + 70))
        
        # New high score notification
        if self.new_high_score_achieved:
            self.draw_text_with_shadow("★ NEW SECTOR HIGH SCORE RECORD ★", self.font_subtitle, COLOR_UI_GREEN, (self.width // 2, stat_y + 110))
        else:
            self.draw_text_with_shadow(f"RECORD TO BEAT: {self.high_score:05d}", self.font_stats, COLOR_TEXT_MUTED, (self.width // 2, stat_y + 110))
            
        # Controls
        self.draw_text_with_shadow("Press [R] to Play Again", self.font_subtitle, COLOR_TEXT_WHITE, (self.width // 2, self.height // 2 + 115))
        self.draw_text_with_shadow("Press [ESC] for Main menu", self.font_menu, COLOR_TEXT_MUTED, (self.width // 2, self.height // 2 + 145))
