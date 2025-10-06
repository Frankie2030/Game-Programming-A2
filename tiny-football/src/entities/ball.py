"""Ball entity with physics integration and rendering helpers."""

import os
import random
import pygame
from pygame.math import Vector2 as V2
from typing import Optional
from settings import CFG
from scaling import SCALING


class Ball:
	"""Represents the single soccer ball with physics and rendering."""
	
	def __init__(self, play_rect: pygame.Rect):
		"""Initialize ball with physics properties and optional sprite.
		
		Args:
			play_rect: Rectangular boundary for ball movement
		"""
		print(f"\n=== BALL INIT DEBUG ===")
		print(f"Received play_rect for initialization: {play_rect}")
		print(f"Play rect width: {play_rect.width}, height: {play_rect.height}")
		print(f"Play rect center: ({play_rect.centerx}, {play_rect.centery})")
		
		self.play_rect = play_rect
		self.radius = int(CFG.ball.get("radius", 10))
		# Tune physics: slightly higher speed, lower damping
		self.friction = float(CFG.ball.get("friction", 0.992))
		self.max_speed = float(CFG.ball.get("max_speed", 620))
		self.color = CFG.colors.get("ball", (255, 112, 67))
		self.pos = V2(play_rect.center)
		self.vel = V2(0, 0)
		print(f"Ball initialized at center: ({self.pos.x:.1f}, {self.pos.y:.1f})")
		
		# Store percentage position for scaling (0.0 to 1.0) - ball uses left-top as reference
		if play_rect.width > 0 and play_rect.height > 0:
			self.percent_x = (self.pos.x - play_rect.left) / play_rect.width
			self.percent_y = (self.pos.y - play_rect.top) / play_rect.height
		else:
			self.percent_x = 0.5  # Default to center
			self.percent_y = 0.5
		
		# Load ball sprite
		self.sprite = None
		try:
			base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
			sprite_path = os.path.join(base_dir, "assets", "gfx", "ball.png")
			if os.path.exists(sprite_path):
				self.sprite = pygame.image.load(sprite_path).convert_alpha()
				# Scale sprite to fit ball radius
				size = self.radius * 2
				self.sprite = pygame.transform.scale(self.sprite, (size, size))
		except Exception:
			self.sprite = None

	def spawn(self, center: Optional[tuple] = None, direction_randomized: bool = True) -> None:
		"""Reset ball position and give it initial velocity.
		
		Args:
			center: Optional center position, defaults to play area center
			direction_randomized: Whether to randomize initial direction
		"""
		self.pos = V2(center if center else self.play_rect.center)
		base = float(CFG.ball.get("base_speed", 360))
		angle = random.uniform(-0.6, 0.6)
		dirv = V2(1, 0).rotate_rad(angle)
		if random.random() < 0.5:
			dirv.x *= -1
		self.vel = dirv * base

	def apply_force(self, vec: V2) -> None:
		"""Apply force vector to ball velocity with speed limiting.
		
		FORCE APPLICATION EQUATIONS:
		
		1. Impulse Addition (Newton's 2nd Law):
		   velocity_new = velocity_old + force_vector

		   This represents an instantaneous impulse (F*dt where dt=1)
		
		2. Speed Limiting (velocity magnitude capping):
		   if |velocity| > max_speed:
		       velocity = velocity * (max_speed / |velocity|)
			
		   Where: max_speed = 620 pixels/s (configurable)
		"""
		# Step 1: Apply impulse (instantaneous velocity change)
		self.vel += vec
		
		# Step 2: Limit maximum speed (velocity magnitude capping)
		spd = self.vel.length()
		if spd > self.max_speed:
			self.vel.scale_to_length(self.max_speed)
			
	def update_percentage_position(self) -> None:
		"""Update percentage position based on current absolute position."""
		if self.play_rect.width > 0 and self.play_rect.height > 0:
			self.percent_x = (self.pos.x - self.play_rect.left) / self.play_rect.width
			self.percent_y = (self.pos.y - self.play_rect.top) / self.play_rect.height
			# Clamp to valid range
			self.percent_x = max(0.0, min(1.0, self.percent_x))
			self.percent_y = max(0.0, min(1.0, self.percent_y))
			
	
	def set_position_from_percentage(self, new_play_rect: pygame.Rect) -> None:
		"""Set absolute position based on percentage position and play area size."""
		if new_play_rect.width > 0 and new_play_rect.height > 0:
			self.pos.x = new_play_rect.left + self.percent_x * new_play_rect.width
			self.pos.y = new_play_rect.top + self.percent_y * new_play_rect.height
			
		# Update play rect reference
		self.play_rect = new_play_rect
		
	def rescale_position(self, new_play_rect: pygame.Rect) -> None:
		"""Rescale ball position to fit the new play area."""
		print(f"\n=== BALL RESCALE DEBUG ===")
		print(f"Received new_play_rect for rescaling: {new_play_rect}")
		print(f"New play rect width: {new_play_rect.width}, height: {new_play_rect.height}")
		print(f"New play rect center: ({new_play_rect.centerx}, {new_play_rect.centery})")
		
		old_pos = self.pos.copy()
		old_percent_x = self.percent_x
		old_percent_y = self.percent_y
		
		# Simply use the stored percentage position to calculate new absolute position
		self.set_position_from_percentage(new_play_rect)
		
		print(f"  BALL:")
		print(f"    OLD: pos({old_pos.x:.1f},{old_pos.y:.1f}) percent({old_percent_x:.3f},{old_percent_y:.3f})")
		print(f"    NEW: pos({self.pos.x:.1f},{self.pos.y:.1f}) percent({self.percent_x:.3f},{self.percent_y:.3f})")

	def update(self, dt: float) -> None:
		"""Update ball position and apply physics (friction, speed limiting).
		
		BALL PHYSICS EQUATIONS:
		
		1. Position Integration (kinematic equation):
		   position_new = position_old + velocity * dt
		
		2. Friction/Drag (exponential velocity decay):
		   velocity_new = velocity_old * friction_coefficient
		   Where: friction_coefficient = 0.992 (0.8% speed loss per frame at 60 FPS)
		
		3. Minimum Velocity Threshold (stops very slow movement):
		   if |velocity|² < 0.01:
		       velocity = (0, 0)  (prevents micro-movements)
		
		4. Speed Limiting (velocity magnitude capping):
		   if |velocity| > max_speed:
		       velocity = velocity * (max_speed / |velocity|)
		   Where: max_speed = 620 pixels/s (configurable)
		"""
		# Step 1: Update position using velocity integration
		self.pos += self.vel * dt
		
		# Step 2: Apply friction (exponential velocity decay)
		self.vel *= self.friction
		
		# Step 3: Stop very slow movements (prevents micro-movements)
		if self.vel.length_squared() < 1e-2:  # 0.01 threshold
			self.vel.update(0, 0)
		
		# Step 4: Limit maximum speed (velocity magnitude capping)
		spd = self.vel.length()
		if spd > self.max_speed:
			self.vel.scale_to_length(self.max_speed)
		
		# Step 5: Update percentage position after movement
		self.update_percentage_position()

	def draw(self, surface: pygame.Surface, debug: bool = False) -> None:
		"""Render the ball on the given surface.
		
		Args:
			surface: Pygame surface to draw on
			debug: Whether to draw debug information (outline and velocity vector)
		"""
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
		
		if debug:
			# Show predicted ball position as a small dot where it will move to
			if self.vel.length() > 10:  # Only show prediction if ball is moving
				# Predict where ball will be in 0.5 seconds with current speed and acceleration
				# Simulate physics: position += velocity * time, then apply friction
				predicted_vel = self.vel * self.friction  # Apply friction to predicted velocity
				predicted_pos = self.pos + predicted_vel * 0.5
				# Since self.pos is already scaled, predicted_pos is also scaled
				scaled_predicted_pos = predicted_pos
				# Draw predicted position as a small filled dot
				dot_radius = max(2, int(SCALING.scale_radius(4)))  # Small dot, minimum 2 pixels
				pygame.draw.circle(surface, (255, 255, 0), (int(scaled_predicted_pos.x), int(scaled_predicted_pos.y)), dot_radius)
				# Draw direction arrow from current position to predicted position
				pygame.draw.line(surface, (255, 255, 0), scaled_pos, scaled_predicted_pos, 3)
				# Draw arrow head
				direction = (predicted_pos - self.pos).normalize()
				arrow_size = SCALING.scale_radius(8)
				arrow_head1 = scaled_predicted_pos - direction * arrow_size + V2(-direction.y, direction.x) * arrow_size * 0.3
				arrow_head2 = scaled_predicted_pos - direction * arrow_size + V2(direction.y, -direction.x) * arrow_size * 0.3
				pygame.draw.line(surface, (255, 255, 0), scaled_predicted_pos, arrow_head1, 2)
				pygame.draw.line(surface, (255, 255, 0), scaled_predicted_pos, arrow_head2, 2)

