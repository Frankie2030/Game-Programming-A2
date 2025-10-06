import pygame
import sys
from settings import CFG
from scaling import SCALING
from game import Game


class Menu:
	"""Main menu system for game mode selection and configuration."""
	
	def __init__(self, screen: pygame.Surface):
		"""Initialize menu with UI elements and default settings"""
		self.screen = screen
		pygame.font.init()
		self.base_font_size = 24
		self.base_big_font_size = 42
		self.font = pygame.font.SysFont(None, self.base_font_size)
		self.big = pygame.font.SysFont(None, self.base_big_font_size)
		
		# Update fonts with current scaling
		self._update_fonts()
		
		# Load background image
		self.background = None
		self.original_background = None
		self.ai_difficulties = ["Easy", "Normal", "Hard"]
		self.ai_diff_idx = 1   # default Normal
		self.ai_difficulty = self.ai_difficulties[self.ai_diff_idx]
  		# self.ai_difficulty = ai_difficulty
		try:
			import os
			base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
			bg_path = os.path.join(base_dir, "assets", "gfx", "start_bg.jpg")
			if os.path.exists(bg_path):
				self.original_background = pygame.image.load(bg_path).convert()
				self._update_background()
				print(f"Background loaded successfully: {bg_path}")
			else:
				print(f"Background image not found: {bg_path}")
				self.original_background = None
		except Exception as e:
			print(f"Error loading background: {e}")
			self.original_background = None

		# 0: multiplayer, 1: human_vs_ai, 2: two_plus_ai
		self.mode_idx = 0  
		self.per_team = max(1, min(CFG.teams.get("per_team", 2), CFG.teams.get("max_per_team", 5)))

		# clickable UI regions
		self._mode_rects = []
		self._minus_rect = None
		self._plus_rect = None
		self.match_minutes = max(1, int(CFG.default_minutes))

		# sliders for ball tuning from config
		self.base_speed = float(CFG.ball.get("base_speed", 360))
		self.friction = float(CFG.ball.get("friction", 0.992))
		self._bs_minus = None
		self._bs_plus = None
		self._fr_minus = None
		self._fr_plus = None
		
		# player acceleration slider (this controls movement responsiveness)
		self.player_accel = float(CFG.player.get("accel", 2600))
		self.player_min_accel = float(CFG.player.get("min_accel", 800))
		self.player_max_accel = float(CFG.player.get("max_accel", 4000))
		self._pa_minus = None
		self._pa_plus = None

	def _update_fonts(self):
		"""Update fonts with current scaling factor."""
		scaled_font_size = max(12, min(48, SCALING.scale_font_size(self.base_font_size)))  # Clamp font size
		scaled_big_font_size = max(16, min(72, SCALING.scale_font_size(self.base_big_font_size)))  # Clamp font size
		# Use a more reliable font
		self.font = pygame.font.Font(None, scaled_font_size)
		self.big = pygame.font.Font(None, scaled_big_font_size)
		
	def _update_background(self):
		"""Update background image with current scaling."""
		if self.original_background:
			screen_size = self.screen.get_size()
			self.background = pygame.transform.smoothscale(self.original_background, screen_size)

	def loop(self):
		"""Main menu event loop handling user input and rendering."""
		clock = pygame.time.Clock()
		running = True

		while running:
			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					return None
				
				# Handle window resize events
				if e.type == pygame.VIDEORESIZE:
					# Update scaling system with new window size (forced uniform scaling)
					SCALING.update_size(e.w, e.h)
					# Resize window to forced aspect ratio
					pygame.display.set_mode((SCALING.current_width, SCALING.current_height), pygame.RESIZABLE)
					# Update fonts and background
					self._update_fonts()
					self._update_background()

				if e.type == pygame.KEYDOWN:
					if e.key == pygame.K_ESCAPE:
						return None
					if e.key in (pygame.K_1, pygame.K_KP1):
						self.mode_idx = 0
					if e.key in (pygame.K_2, pygame.K_KP2):
						self.mode_idx = 1
					if e.key in (pygame.K_3, pygame.K_KP3):
						self.mode_idx = 2
					if e.key in (pygame.K_LEFT, pygame.K_a):
						self.per_team = max(1, self.per_team - 1)
					if e.key in (pygame.K_RIGHT, pygame.K_d):
						self.per_team = min(CFG.teams.get("max_per_team", 5), self.per_team + 1)
					if e.key in (pygame.K_RETURN, pygame.K_SPACE):
						return self.get_selection()

				if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
					pos = e.pos
					for i, r in enumerate(self._mode_rects):
						if r and r.collidepoint(pos):
							self.mode_idx = i
							break
					if self._minus_rect and self._minus_rect.collidepoint(pos):
						self.per_team = max(1, self.per_team - 1)
					if self._plus_rect and self._plus_rect.collidepoint(pos):
						self.per_team = min(CFG.teams.get("max_per_team", 5), self.per_team + 1)
					if self.mode_idx == 1 and hasattr(self, "_ai_rect") and self._ai_rect.collidepoint(pos):
						self.ai_diff_idx = (self.ai_diff_idx + 1) % len(self.ai_difficulties)
						self.ai_difficulty = self.ai_difficulties[self.ai_diff_idx]

					# timer +/- click areas
					if hasattr(self, "_tminus_rect") and self._tminus_rect and self._tminus_rect.collidepoint(pos):
						self.match_minutes = max(1, self.match_minutes - 1)
					if hasattr(self, "_tplus_rect") and self._tplus_rect and self._tplus_rect.collidepoint(pos):
						self.match_minutes = min(20, self.match_minutes + 1)
					if hasattr(self, "_start_rect") and self._start_rect and self._start_rect.collidepoint(pos):
						return self.get_selection()

					# sliders
					if self._bs_minus and self._bs_minus.collidepoint(pos):
						self.base_speed = max(100.0, self.base_speed - 10)
					if self._bs_plus and self._bs_plus.collidepoint(pos):
						self.base_speed = min(800.0, self.base_speed + 10)
					if self._fr_minus and self._fr_minus.collidepoint(pos):
						self.friction = max(0.950, round(self.friction - 0.001, 3))
					if self._fr_plus and self._fr_plus.collidepoint(pos):
						self.friction = min(0.999, round(self.friction + 0.001, 3))
					
					# player acceleration slider
					if self._pa_minus and self._pa_minus.collidepoint(pos):
						self.player_accel = max(self.player_min_accel, self.player_accel - 200)
					if self._pa_plus and self._pa_plus.collidepoint(pos):
						self.player_accel = min(self.player_max_accel, self.player_accel + 200)

			self.draw()
			pygame.display.flip()
			clock.tick(60)

	# def get_selection(self):
	# 	"""Get current menu selections as configuration dictionary"""
	# 	modes = ["multiplayer", "human_vs_ai", "two_plus_ai"]
	# 	return {"mode": modes[self.mode_idx], "per_team": int(self.per_team), "minutes": int(self.match_minutes), "base_speed": float(self.base_speed), "friction": float(self.friction), "player_accel": float(self.player_accel)}

	def get_selection(self):
		"""Get current menu selections as configuration dictionary"""
		modes = ["multiplayer", "human_vs_ai", "two_plus_ai"]
		return {
			"mode": modes[self.mode_idx],
			"per_team": int(self.per_team),
			"minutes": int(self.match_minutes),
			"base_speed": float(self.base_speed),
			"friction": float(self.friction),
			"player_accel": float(self.player_accel),
			"ai_difficulty": getattr(self, "ai_difficulty", "Normal"),  # default if not set
		}
    
	def draw(self):
		"""Render the menu interface with all interactive elements."""
		# Update fonts with current scaling
		self._update_fonts()
		
		# Draw background image if available
		if self.background:
			self.screen.blit(self.background, (0, 0))
		else:
			self.screen.fill(CFG.colors.get("bg", (20, 120, 20)))
		
		w, h = self.screen.get_size()
		offset = SCALING.get_offset()

		# Title with subtle backdrop - centered on screen
		title = self.big.render("Tiny Football", True, (255, 255, 255))
		shadow = self.big.render("Tiny Football", True, (0, 0, 0))
		title_y = int(60 + offset.y)
		tr = title.get_rect(center=(w // 2, title_y))
		self.screen.blit(shadow, tr.move(2, 2))
		self.screen.blit(title, tr)
		options = [
			"1) Multiplayer (two humans)",
			"2) Human vs AI",
			# "3) Two-Player + AI assistant",
		]
		mouse = pygame.mouse.get_pos()
		
		# Scale menu options with adaptive spacing based on window size
		scaled_width = int(400 * SCALING.uniform_scale)
		scaled_height = int(30 * SCALING.uniform_scale)
		# Adaptive spacing: larger spacing for larger windows
		base_spacing = max(40, min(80, 40 + (SCALING.uniform_scale - 1) * 20))
		scaled_spacing = int(base_spacing * SCALING.uniform_scale)
		start_x = w // 2 - scaled_width // 2
		start_y = int(120 + offset.y)  # Increased top margin
		
		for i, text in enumerate(options):
			row_rect = pygame.Rect(start_x, start_y + i * scaled_spacing, scaled_width, scaled_height)
			hover = row_rect.collidepoint(mouse)
			is_selected = i == self.mode_idx
			
			# Draw background for selected option or hover
			border_radius = int(6 * SCALING.uniform_scale)
			if is_selected:
				pygame.draw.rect(self.screen, (60, 160, 60), row_rect, border_radius=border_radius)
				pygame.draw.rect(self.screen, (100, 200, 100), row_rect, 2, border_radius=border_radius)
			elif hover:
				pygame.draw.rect(self.screen, (40, 90, 40), row_rect, border_radius=border_radius)
			
			# Color text based on selection
			if is_selected:
				color = (255, 255, 100)  # Bright yellow for selected
			elif hover:
				color = (255, 255, 255)  # White for hover
			else:
				color = (180, 180, 180)  # Gray for unselected
				
			surf = self.font.render(text, True, color)
			rect = surf.get_rect(center=row_rect.center)
			self.screen.blit(surf, rect)
			if len(self._mode_rects) < len(options):
				self._mode_rects.append(row_rect)
			else:
				self._mode_rects[i] = row_rect
				
		# Settings section - adaptive spacing based on window size
		# Calculate gap based on how much space the menu options take up
		menu_bottom = start_y + len(options) * scaled_spacing + scaled_height
		settings_gap = max(20, int(30 * SCALING.uniform_scale))  # Reduced gap to move settings higher
		settings_y_start = int(menu_bottom + settings_gap + offset.y)
		line_height = int(45 * SCALING.uniform_scale)  # Increased line height
		settings_width = int(600 * SCALING.uniform_scale)  # Increased width for more space
		settings_x = w // 2 - settings_width // 2
		button_size = int(24 * SCALING.uniform_scale)
		
		# Players per team - Line 1
		pt_label = self.font.render("Players per team:", True, (240, 240, 240))
		self.screen.blit(pt_label, (settings_x, settings_y_start))
		
		pt_val = self.font.render(str(self.per_team), True, (255, 255, 255))
		# Calculate proper spacing with margin
		spacing = int(20 * SCALING.uniform_scale)
		val_x = settings_x + pt_label.get_width() + spacing
		self.screen.blit(pt_val, (val_x, settings_y_start))
		
		# +/- buttons for players per team with proper spacing
		button_spacing = int(50 * SCALING.uniform_scale)
		self._minus_rect = pygame.Rect(val_x + pt_val.get_width() + spacing, settings_y_start, button_size, button_size)
		self._plus_rect = pygame.Rect(val_x + pt_val.get_width() + button_spacing, settings_y_start, button_size, button_size)
		pygame.draw.rect(self.screen, (240, 120, 120), self._minus_rect, 0, border_radius=int(4 * SCALING.uniform_scale))
		pygame.draw.rect(self.screen, (120, 240, 120), self._plus_rect, 0, border_radius=int(4 * SCALING.uniform_scale))
		minus_text = self.font.render("-", True, (255, 255, 255))
		plus_text = self.font.render("+", True, (255, 255, 255))
		self.screen.blit(minus_text, minus_text.get_rect(center=self._minus_rect.center))
		self.screen.blit(plus_text, plus_text.get_rect(center=self._plus_rect.center))

		# Player acceleration - Line 2
		pa_label = self.font.render("Player acceleration:", True, (240, 240, 240))
		self.screen.blit(pa_label, (settings_x, settings_y_start + line_height))
		
		pa_val = self.font.render(f"{int(self.player_accel)}", True, (255, 255, 255))
		pa_val_x = settings_x + pa_label.get_width() + int(15 * SCALING.uniform_scale)
		self.screen.blit(pa_val, (pa_val_x, settings_y_start + line_height))
		
		# +/- buttons for player acceleration
		self._pa_minus = pygame.Rect(pa_val_x + pa_val.get_width() + int(15 * SCALING.uniform_scale), settings_y_start + line_height, button_size, button_size)
		self._pa_plus = pygame.Rect(pa_val_x + pa_val.get_width() + button_spacing, settings_y_start + line_height, button_size, button_size)
		pygame.draw.rect(self.screen, (240, 120, 120), self._pa_minus, 0, border_radius=int(4 * SCALING.uniform_scale))
		pygame.draw.rect(self.screen, (120, 240, 120), self._pa_plus, 0, border_radius=int(4 * SCALING.uniform_scale))
		pa_minus_text = self.font.render("-", True, (255, 255, 255))
		pa_plus_text = self.font.render("+", True, (255, 255, 255))
		self.screen.blit(pa_minus_text, pa_minus_text.get_rect(center=self._pa_minus.center))
		self.screen.blit(pa_plus_text, pa_plus_text.get_rect(center=self._pa_plus.center))

		# Match length - Line 3
		match_label = self.font.render("Match length (minutes):", True, (240, 240, 240))
		self.screen.blit(match_label, (settings_x, settings_y_start + line_height * 2))
		
		match_val = self.font.render(str(self.match_minutes), True, (255, 255, 255))
		match_val_x = settings_x + match_label.get_width() + int(15 * SCALING.uniform_scale)
		self.screen.blit(match_val, (match_val_x, settings_y_start + line_height * 2))
  
		# AI Difficulty toggle (only for Human vs AI)
		if self.mode_idx == 1:
			diff_label = self.font.render("AI Difficulty:", True, (240, 240, 240))
			diff_val = self.font.render(self.ai_difficulty, True, (255, 255, 0))
			diff_y = settings_y_start + line_height * 3
			self.screen.blit(diff_label, (settings_x, diff_y))
			self.screen.blit(diff_val, (settings_x + diff_label.get_width() + 20, diff_y))
			self._ai_rect = diff_val.get_rect(
				topleft=(settings_x + diff_label.get_width() + 20, diff_y)
			)
		
		# +/- buttons for match length
		self._tminus_rect = pygame.Rect(match_val_x + match_val.get_width() + int(15 * SCALING.uniform_scale), settings_y_start + line_height * 2, button_size, button_size)
		self._tplus_rect = pygame.Rect(match_val_x + match_val.get_width() + button_spacing, settings_y_start + line_height * 2, button_size, button_size)
		pygame.draw.rect(self.screen, (240, 120, 120), self._tminus_rect, 0, border_radius=int(4 * SCALING.uniform_scale))
		pygame.draw.rect(self.screen, (120, 240, 120), self._tplus_rect, 0, border_radius=int(4 * SCALING.uniform_scale))
		match_minus_text = self.font.render("-", True, (255, 255, 255))
		match_plus_text = self.font.render("+", True, (255, 255, 255))
		self.screen.blit(match_minus_text, match_minus_text.get_rect(center=self._tminus_rect.center))
		self.screen.blit(match_plus_text, match_plus_text.get_rect(center=self._tplus_rect.center))
		
		# # Ball sliders
		# sec_y = 470
		# label = self.font.render("Ball base speed:", True, (240, 240, 240))
		# self.screen.blit(label, (w // 2 - 220, sec_y))
		# val = self.font.render(f"{int(self.base_speed)}", True, (255, 255, 255))
		# self.screen.blit(val, (w // 2 + 80, sec_y))
		# bs_minus = self.big.render("-", True, (20, 0, 0))
		# bs_plus = self.big.render("+", True, (0, 20, 0))
		# self._bs_minus = bs_minus.get_rect(center=(w // 2 - 20, sec_y + 10)).inflate(24, 12)
		# self._bs_plus = bs_plus.get_rect(center=(w // 2 + 20, sec_y + 10)).inflate(24, 12)
		# pygame.draw.rect(self.screen, (240, 120, 120), self._bs_minus, 0, border_radius=6)
		# pygame.draw.rect(self.screen, (120, 240, 120), self._bs_plus, 0, border_radius=6)
		# self.screen.blit(self.big.render("-", True, (255, 255, 255)), self._bs_minus.inflate(-24, -12))
		# self.screen.blit(self.big.render("+", True, (255, 255, 255)), self._bs_plus.inflate(-24, -12))
		
		# # friction
		# label2 = self.font.render("Ball friction:", True, (240, 240, 240))
		# self.screen.blit(label2, (w // 2 - 220, sec_y + 34))
		# val2 = self.font.render(f"{self.friction:.3f}", True, (255, 255, 255))
		# self.screen.blit(val2, (w // 2 + 80, sec_y + 34))
		# fr_minus = self.big.render("-", True, (20, 0, 0))
		# fr_plus = self.big.render("+", True, (0, 20, 0))
		# self._fr_minus = fr_minus.get_rect(center=(w // 2 - 20, sec_y + 44)).inflate(24, 12)
		# self._fr_plus = fr_plus.get_rect(center=(w // 2 + 20, sec_y + 44)).inflate(24, 12)
		# pygame.draw.rect(self.screen, (240, 120, 120), self._fr_minus, 0, border_radius=6)
		# pygame.draw.rect(self.screen, (120, 240, 120), self._fr_plus, 0, border_radius=6)
		# self.screen.blit(self.big.render("-", True, (255, 255, 255)), self._fr_minus.inflate(-24, -12))
		# self.screen.blit(self.big.render("+", True, (255, 255, 255)), self._fr_plus.inflate(-24, -12))
		
		# Start button with increased spacing from settings
		start_width = int(200 * SCALING.uniform_scale)
		start_height = int(44 * SCALING.uniform_scale)
		start_rect = pygame.Rect(0, 0, start_width, start_height)
		start_rect.center = (w // 2, int(h - 80 * SCALING.uniform_scale))  # Increased bottom margin
		mouse = pygame.mouse.get_pos()
		hover = start_rect.collidepoint(mouse)
		pygame.draw.rect(self.screen, (60, 140, 240) if hover else (40, 100, 200), start_rect, 0, border_radius=int(8 * SCALING.uniform_scale))
		label = self.font.render("Start", True, (255, 255, 255))
		self.screen.blit(label, label.get_rect(center=start_rect.center))
		self._start_rect = start_rect


def main() -> None:
	"""Main entry point: initialize pygame, show menu, and run game loop."""
	pygame.init()
	pygame.mixer.init()  # Explicitly initialize the mixer
	# Make window resizable with minimum size constraints
	screen = pygame.display.set_mode(CFG.size, pygame.RESIZABLE)
	pygame.display.set_caption("Tiny Football - Uniform Scaling")
	clock = pygame.time.Clock()
	
	# Set minimum window size
	pygame.display.set_mode((max(640, CFG.size[0]), max(480, CFG.size[1])), pygame.RESIZABLE)

	# Start menu
	menu = Menu(screen)
	selection = menu.loop()
	
	if selection is None:
		pygame.quit()
		sys.exit(0)

	# Apply selection into Game (mutate config for this run)
	CFG.ball["base_speed"] = selection["base_speed"]
	CFG.ball["friction"] = selection["friction"]
	CFG.player["accel"] = selection["player_accel"]
	
	# Pass AI difficulty from menu to game
	game = Game(screen, mode=selection["mode"], per_team=selection["per_team"], minutes=selection["minutes"], ai_difficulty=selection.get("ai_difficulty", "Normal"))
	running = True
	while running:
		running = game.run_frame()

	pygame.quit()
	sys.exit(0)


if __name__ == "__main__":
	main()

