"""Player entity for Tiny Football, with movement and kick methods."""

import os
import pygame
from pygame.math import Vector2 as V2
from settings import CFG
from scaling import SCALING


class Player:
	"""A controllable round player pawn with movement and kicking abilities."""
	
	def __init__(self, pos: V2, color, active_glow, team_key: str = "p1", player_name: str = "", pitch_rect: pygame.Rect = None, is_left_team: bool = True):
		"""Initialize player with physics properties and optional sprite."""
		self.pos = V2(pos)
		self.vel = V2(0, 0)
		self.radius = int(CFG.player.get("radius", 16))
		self.accel = float(CFG.player.get("accel", 2600))
		self.max_speed = float(CFG.player.get("speed", 260))
		self.drag = float(CFG.player.get("drag", 0.90))
		self.color = color
		self.active_glow = active_glow
		self.is_active = False
		self.player_name = player_name
		self.team_key = team_key
		self.is_left_team = is_left_team
		
		# Ball possession tracking for AI decision-making
		self.has_ball = False

		# Home x coordinate used by AI line-lock and half-field clamping visuals
		self.home_x = float(self.pos.x)
		
		# Store percentage-based position for scaling
		if pitch_rect and pitch_rect.width > 0 and pitch_rect.height > 0:
			if is_left_team:
				# Left team: percentage from left edge and top edge
				self.percent_x = (pos.x - pitch_rect.left) / pitch_rect.width
				self.percent_y = (pos.y - pitch_rect.top) / pitch_rect.height
			else:
				# Right team: percentage from right edge and top edge
				self.percent_x = (pitch_rect.right - pos.x) / pitch_rect.width
				self.percent_y = (pos.y - pitch_rect.top) / pitch_rect.height
		else:
			self.percent_x = 0.1  # Default positions
			self.percent_y = 0.5
		
		# Load player sprite
		self.sprite = None
		try:
			base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
			sprite_path = os.path.join(base_dir, "assets", "gfx", f"player_{team_key}.png")
			if os.path.exists(sprite_path):
				self.sprite = pygame.image.load(sprite_path).convert_alpha()
				# Scale sprite to fit player radius
				size = self.radius * 2
				self.sprite = pygame.transform.scale(self.sprite, (size, size))
		except Exception:
			self.sprite = None

	def move(self, input_dir: V2, dt: float, pitch_rect: pygame.Rect) -> None:
		"""Update player position based on input direction and physics.
		
		PHYSICS EQUATIONS:
		
		1. Input Normalization:
		   input_dir = input_dir / |input_dir|  (unit vector for consistent acceleration)
		
		2. Acceleration (Newton's 2nd Law: F = ma, but here a = F/m is constant):
		   v_new = v_old + (input_dir * acceleration * dt)
		   Where: acceleration = 1400 pixels/s² (configurable)
		
		3. Drag/Friction (exponential velocity decay):
		   v_new = v_old * drag_coefficient
		   Where: drag_coefficient = 0.90 (10% speed loss per frame at 60 FPS)
		
		4. Speed Limiting (velocity magnitude capping):
		   if |velocity| > max_speed:
		       velocity = velocity * (max_speed / |velocity|)
		   Where: max_speed = 260 pixels/s (configurable)
		
		5. Position Integration (kinematic equation):
		   position_new = position_old + velocity * dt
		
		6. Boundary Collision (position clamping):
		   pos.x = clamp(pos.x, left_bound + radius, right_bound - radius)
		   pos.y = clamp(pos.y, top_bound + radius, bottom_bound - radius)
		"""
		# Step 1: Normalize input direction for consistent acceleration
		if input_dir.length_squared() > 0:
			input_dir = input_dir.normalize()
			# Step 2: Apply acceleration (F = ma, but a is constant)
			self.vel += input_dir * self.accel * dt
		
		# Step 3: Apply drag/friction (exponential velocity decay)
		self.vel *= self.drag
		
		# Step 4: Limit maximum speed (velocity magnitude capping)
		spd = self.vel.length()
		if spd > self.max_speed:
			self.vel.scale_to_length(self.max_speed)
		
		# Step 5: Update position (kinematic integration)
		self.pos += self.vel * dt
		
		# Step 6: Boundary collision detection and response (position clamping)
		r = self.radius
		self.pos.x = max(pitch_rect.left + r, min(pitch_rect.right - r, self.pos.x))
		self.pos.y = max(pitch_rect.top + r, min(pitch_rect.bottom - r, self.pos.y))
		
		# Update percentage position after movement
		self.update_percentage_position(pitch_rect)
	
	def update_percentage_position(self, pitch_rect: pygame.Rect) -> None:
		"""Update percentage position based on current absolute position."""
		if pitch_rect.width > 0 and pitch_rect.height > 0:
			if self.is_left_team:
				# Left team: percentage from left edge (ax distance)
				self.percent_x = (self.pos.x - pitch_rect.left) / pitch_rect.width
				self.percent_y = (self.pos.y - pitch_rect.top) / pitch_rect.height
			else:
				# Right team: percentage from right edge (bx distance) 
				self.percent_x = (pitch_rect.right - self.pos.x) / pitch_rect.width
				self.percent_y = (self.pos.y - pitch_rect.top) / pitch_rect.height
				
			# Clamp to valid range
			self.percent_x = max(0.0, min(1.0, self.percent_x))
			self.percent_y = max(0.0, min(1.0, self.percent_y))
			
	
	def set_position_from_percentage(self, pitch_rect: pygame.Rect) -> None:
		"""Set absolute position based on percentage position and pitch size."""
		if pitch_rect.width > 0 and pitch_rect.height > 0:
			if self.is_left_team:
				# Left team: maintain ax distance from left edge
				self.pos.x = pitch_rect.left + self.percent_x * pitch_rect.width
				self.pos.y = pitch_rect.top + self.percent_y * pitch_rect.height
			else:
				# Right team: maintain bx distance from right edge
				self.pos.x = pitch_rect.right - self.percent_x * pitch_rect.width
				self.pos.y = pitch_rect.top + self.percent_y * pitch_rect.height
			
			# Update home_x for AI
			self.home_x = self.pos.x

	def kick(self, ball) -> bool:
		"""Attempt to kick the ball if within reach.
		
		KICK MECHANICS:
		
		1. Distance Check (collision detection):
		   distance = |ball_pos - player_pos|
		   reach = player_radius + ball_radius + tolerance
		   if distance <= reach: kick is possible
		
		2. Kick Direction (unit vector from player to ball):
		   direction = (ball_pos - player_pos) / |ball_pos - player_pos|
		   if ball_pos == player_pos: direction = (1, 0)  (default rightward)
		
		3. Force Application (impulse to ball):
		   force = direction * kick_strength
		   Where: kick_strength = 220 pixels/s²
		"""
		# Step 1: Calculate distance between player and ball centers
		delta = ball.pos - self.pos
		reach = self.radius + ball.radius + 2  # +2 for small tolerance
		
		# Step 2: Check if ball is within kicking range
		if delta.length_squared() <= reach * reach:
			# Step 3: Calculate kick direction (unit vector)
			d = delta.normalize() if delta.length_squared() > 0 else V2(1, 0)
			# Step 4: Apply force to ball
			ball.apply_force(d * 220)  # 220 pixels/s² kick strength
			return True
		return False

	def draw(self, surface: pygame.Surface, debug: bool = False, game_finished: bool = False) -> None:
		"""Render the player on the given surface."""
		# Position is already scaled, just use it directly
		scaled_pos = self.pos
		scaled_radius = SCALING.scale_radius(self.radius)
		
		if self.sprite:
			# Scale sprite if it exists
			scaled_sprite_size = int(self.radius * 2 * SCALING.uniform_scale)
			if scaled_sprite_size != self.sprite.get_width():
				scaled_sprite = pygame.transform.scale(self.sprite, (scaled_sprite_size, scaled_sprite_size))
			else:
				scaled_sprite = self.sprite
			# Draw sprite centered on position
			rect = scaled_sprite.get_rect(center=(int(scaled_pos.x), int(scaled_pos.y)))
			surface.blit(scaled_sprite, rect)
		else:
			# Fallback to circle drawing
			pygame.draw.circle(surface, self.color, (int(scaled_pos.x), int(scaled_pos.y)), int(scaled_radius))
			pygame.draw.circle(surface, (10, 10, 10), (int(scaled_pos.x), int(scaled_pos.y)), int(scaled_radius), 2)
		
		# Show active player highlight only when game is not finished
		if self.is_active and not game_finished:
			pygame.draw.circle(surface, self.active_glow, (int(scaled_pos.x), int(scaled_pos.y)), int(scaled_radius + 4), 3)
		
		# Always show player name above the player
		if self.player_name:
			font_size = SCALING.scale_font_size(20)
			font = pygame.font.SysFont(None, font_size)
			# Color the name based on whether player is active (but not when game is finished)
			if self.is_active and not game_finished:
				text_color = (255, 255, 100)  # Bright yellow for active player
				# Add background rectangle for active player name
				text_surf = font.render(self.player_name, True, text_color)
				text_rect = text_surf.get_rect(center=(int(scaled_pos.x), int(scaled_pos.y) - scaled_radius - 15))
				# Draw background for better visibility
				bg_rect = text_rect.inflate(8, 4)
				pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect, border_radius=4)
				surface.blit(text_surf, text_rect)
			else:
				text_color = (220, 220, 220)  # Light gray for inactive players
				text_surf = font.render(self.player_name, True, text_color)
				text_rect = text_surf.get_rect(center=(int(scaled_pos.x), int(scaled_pos.y) - scaled_radius - 15))
				surface.blit(text_surf, text_rect)
		
		if debug:
			pygame.draw.circle(surface, (255, 255, 0), (int(scaled_pos.x), int(scaled_pos.y)), int(scaled_radius), 1)
			end = scaled_pos + SCALING.scale_position(self.vel * 0.1)
			pygame.draw.line(surface, (255, 255, 0), scaled_pos, end, 2)

