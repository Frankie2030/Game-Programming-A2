import math
import pygame
from pygame.math import Vector2 as V2
from settings import CFG


class ForceField:
	"""Applies gravitational force effects to the ball."""
	
	def __init__(self, rect: pygame.Rect):
		"""Initialize force field with configuration from settings."""
		self.rect = rect
		self.enabled = bool(CFG.force_field.get("enabled", False))
		self.kind = "gravity"  # force gravity-only per request
		self.strength = float(CFG.force_field.get("strength", 80))
		self.center = V2(rect.center)

	def apply(self, ball, dt: float) -> None:
		"""Apply gravitational force to the ball if enabled.
		
		GRAVITATIONAL FORCE EQUATIONS:
		=============================
		
		1. Distance Vector (from ball to force field center):
		   distance_vector = center_pos - ball_pos
		
		2. Distance Squared (for inverse square law):
		   distance_squared = |distance_vector|²
		   Minimum distance: 50 pixels² (prevents division by zero)
		
		3. Gravitational Force (inverse square law):
		   force = distance_vector * (strength / distance_squared) * dt
		   Where: strength = 80 (configurable gravitational constant)
		
		4. Force Application (impulse to ball):
		   ball.apply_force(force)  (adds force to ball's velocity)
		
		The inverse square law creates realistic gravitational attraction:
		- Close to center: strong force
		- Far from center: weak force
		- Force direction: always toward the center
		
		Args:
			ball: Ball object to apply force to
			dt: Delta time in seconds (typically 1/60 = 0.0167s)
		"""
		if not self.enabled:
			return

		if self.kind == "gravity":
			# Step 1: Calculate distance vector from ball to force field center
			d = self.center - ball.pos
			
			# Step 2: Calculate distance squared with minimum threshold
			d2 = max(d.length_squared(), 50.0)  # 50 pixels² minimum
			
			# Step 3: Apply inverse square gravitational force
			force = d * (self.strength / d2) * dt
			
			# Step 4: Apply force as impulse to ball
			ball.apply_force(force)

	def draw(self, surface: pygame.Surface, t: float) -> None:
		"""Draw visual representation of the force field."""
		if not self.enabled:
			return
			
		if self.kind == "gravity":
			color = (200, 180, 255)
			r = 24 + int(6 * math.sin(t * 3))
			pygame.draw.circle(surface, color, (int(self.center.x), int(self.center.y)), r, 2)

