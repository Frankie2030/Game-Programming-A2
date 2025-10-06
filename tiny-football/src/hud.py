"""Heads-up display for scores, stats, timer, and debug text."""

import os
import pygame
from settings import CFG
from scaling import SCALING


class HUD:
	"""Draws overlay information and debug telemetry."""
	
	def __init__(self):
		"""Initialize HUD with fonts and display settings."""
		pygame.font.init()
		self.base_font_size = int(CFG.hud.get("font_size", 20))
		self.base_big_font_size = self.base_font_size + 6
		self.font = pygame.font.SysFont(None, self.base_font_size)
		self.big = pygame.font.SysFont(None, self.base_big_font_size)
		self.show_fps = bool(CFG.hud.get("show_fps", True))
		self.debug = False
		self.show_live_stats = False  # Toggle for live player stats
		
		# Update fonts with current scaling
		self._update_fonts()

	def toggle_debug(self):
		"""Toggle debug information display on/off."""
		self.debug = not self.debug

	def toggle_live_stats(self):
		"""Toggle live player statistics display on/off."""
		self.show_live_stats = not self.show_live_stats
		
	def _update_fonts(self):
		"""Update fonts with current scaling factor."""
		scaled_font_size = SCALING.scale_font_size(self.base_font_size)
		scaled_big_font_size = SCALING.scale_font_size(self.base_big_font_size)
		self.font = pygame.font.SysFont(None, scaled_font_size)
		self.big = pygame.font.SysFont(None, scaled_big_font_size)

	def draw(self, surface: pygame.Surface, score_l: int, score_r: int, hits_l: int, hits_r: int, fps_val: float, force_label: str = "", time_left: float = None) -> None:
		"""Draw main HUD elements including score, controls, and optional info.
		
		Args:
			surface: Pygame surface to draw on
			score_l: Left team score
			score_r: Right team score
			hits_l: Left team hit count
			hits_r: Right team hit count
			fps_val: Current FPS value
			force_label: Optional force field status text
			time_left: Remaining match time in seconds
		"""
		# Update fonts with current scaling
		self._update_fonts()
		
		w, h = surface.get_size()
		offset = SCALING.get_offset()
		
		# Top center score - simplified without scoreboard
		score_text = self.big.render(f"P1 {score_l} - {score_r} P2", True, (255, 255, 255))
		rect = score_text.get_rect(center=(w // 2, int(24 + offset.y)))
		surface.blit(score_text, rect)
		
		# Controls hint bottom-left (updated to remove group command)
		hint = self.font.render("WASD vs Arrows | Tab/K: cycle | 1-5/6-0: select | B: stats | P: pause | M: mute", True, (235, 235, 235))
		surface.blit(hint, (int(16 + offset.x), int(h - 28)))
		
		if force_label:
			fl = self.font.render(force_label, True, (220, 240, 255))
			surface.blit(fl, (int(16 + offset.x), int(16 + offset.y)))
		if self.show_fps:
			fps = self.font.render(f"{fps_val:.0f} FPS", True, (230, 230, 230))
			surface.blit(fps, (int(16 + offset.x), int(16 + offset.y)))
		if time_left is not None:
			m = int(time_left // 60)
			s = int(time_left % 60)
			txt = self.big.render(f"{m:02d}:{s:02d}", True, (255, 255, 255))
			surface.blit(txt, (int(w - 110 + offset.x), int(16 + offset.y)))

	def draw_live_stats(self, surface: pygame.Surface, ball, teams) -> None:
		"""Draw live player statistics on top left and right corners."""
		if not self.show_live_stats:
			return
		
		w, _ = surface.get_size()
		
		# Show only basic info in normal mode, detailed info in debug mode
		if not self.debug:
			# Normal mode: show only which players are active
			if teams and len(teams) > 0:
				active_players = []
				for pi, p in enumerate(teams[0].players):
					if p.is_active:
						active_players.append(f"P1-{pi+1}")
				if active_players:
					text = f"Active: {', '.join(active_players)}"
					surf = self.font.render(text, True, (255, 255, 100))
					surface.blit(surf, (16, 60))
			
			if teams and len(teams) > 1:
				active_players = []
				for pi, p in enumerate(teams[1].players):
					if p.is_active:
						active_players.append(f"P2-{pi+1}")
				if active_players:
					text = f"Active: {', '.join(active_players)}"
					surf = self.font.render(text, True, (255, 255, 100))
					text_rect = surf.get_rect()
					surface.blit(surf, (w - text_rect.width - 16, 60))
		else:
			# Debug mode: show detailed position and speed info
			# Get offset for proper scaling
			offset = SCALING.get_offset()
			
			# Position debug text in the yellow corner areas (top left and top right)
			# These should be in the corners, not on the field
			y_debug = SCALING.scale_font_size(80)  # Fixed position in corner areas
			
			# Left team stats (top left corner)
			if teams and len(teams) > 0:
				y_left = y_debug
				for pi, p in enumerate(teams[0].players):
					speed = p.vel.length()
					# Show the actual rendered position (scaled + offset)
					rendered_pos = SCALING.apply_offset(SCALING.scale_position(p.pos))
					text = f"P1-{pi+1}: pos({rendered_pos.x:.0f},{rendered_pos.y:.0f}) spd({speed:.0f})"
					# Use scaled font size like in starting screen
					scaled_font = pygame.font.Font(None, SCALING.scale_font_size(16))
					surf = scaled_font.render(text, True, (255, 255, 255))
					surface.blit(surf, (int(SCALING.scale_font_size(16)), int(y_left)))
					y_left += SCALING.scale_font_size(18)
			
			# Right team stats (top right corner)
			if teams and len(teams) > 1:
				y_right = y_debug
				for pi, p in enumerate(teams[1].players):
					speed = p.vel.length()
					# Show the actual rendered position (scaled + offset)
					rendered_pos = SCALING.apply_offset(SCALING.scale_position(p.pos))
					text = f"P2-{pi+1}: pos({rendered_pos.x:.0f},{rendered_pos.y:.0f}) spd({speed:.0f})"
					# Use scaled font size like in starting screen
					scaled_font = pygame.font.Font(None, SCALING.scale_font_size(16))
					surf = scaled_font.render(text, True, (255, 255, 255))
					text_rect = surf.get_rect()
					surface.blit(surf, (int(w - text_rect.width - SCALING.scale_font_size(16)), int(y_right)))
					y_right += SCALING.scale_font_size(18)

	def draw_debug_text(self, surface: pygame.Surface, ball, teams) -> None:
		"""Draw detailed debug information about ball and player positions/velocities.
		
		Args:
			surface: Pygame surface to draw on
			ball: Ball object to display info for
			teams: List of team objects to display player info for
		"""
		if not self.debug:
			return
		info = [
			f"Ball pos=({ball.pos.x:.1f},{ball.pos.y:.1f}) vel=({ball.vel.x:.1f},{ball.vel.y:.1f})",
		]
		for ti, team in enumerate(teams):
			for pi, p in enumerate(team.players):
				info.append(f"T{ti+1}P{pi+1} pos=({p.pos.x:.1f},{p.pos.y:.1f}) vel=({p.vel.x:.1f},{p.vel.y:.1f}){' *' if p.is_active else ''}")
		y = 72
		for line in info:
			surf = self.font.render(line, True, (255, 255, 0))
			surface.blit(surf, (16, y))
			y += 18

