"""Pitch rendering and goal sensor rectangles."""

import os
import pygame
from pygame import Rect
from typing import Tuple
from settings import CFG
from scaling import SCALING


class Pitch:
	"""Responsible for drawing the field and exposing play rectangles."""
	
	def __init__(self, surface: pygame.Surface):
		"""Initialize pitch with field dimensions and goal areas."""
		self.surface = surface
		self.base_width = 960
		self.base_height = 540
		w, h = CFG.size
		m = int(CFG.field.get("margin", 40))
		self.inner = Rect(m, m, w - 2 * m, h - 2 * m)
		self.wall_thickness = int(CFG.field.get("wall_thickness", 8))
		self.goal_width = int(CFG.field.get("goal_width", 140))
		self.goal_depth = int(CFG.field.get("goal_depth", 20))

		# optional images
		self.field_img = None
		self.original_field_img = None
		try:
			base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
			img_path = os.path.join(base_dir, "assets", "gfx", "field_960x540.png")
			if os.path.exists(img_path):
				self.original_field_img = pygame.image.load(img_path).convert()
				self._update_field_image()
		except Exception:
			self.field_img = None
			self.original_field_img = None
		
		# Initialize goals with proper scaling (after field image is set up)
		self.reset_rects()

	def _update_field_image(self):
		"""Update field image with current scaling."""
		if self.original_field_img:
			# Scale the image to current window size
			new_size = (int(self.base_width * SCALING.uniform_scale), 
						int(self.base_height * SCALING.uniform_scale))
			self.field_img = pygame.transform.smoothscale(self.original_field_img, new_size)

	def draw(self, debug: bool = False) -> None:
		"""Render the soccer field with walls, center line, and goal areas.
		
		Args:
			debug: Whether to show debug outlines around goal areas
		"""
		# Clear screen with background color
		bg = CFG.colors.get("bg", (18, 110, 18))
		self.surface.fill(bg)
		
		# Get offset for centering
		offset = SCALING.get_offset()
		
		if self.field_img:
			# Draw scaled field image centered
			self.surface.blit(self.field_img, offset)
			# draw only sensor outlines when using a baked field image and debug is enabled
			if debug:
				# Use red color for goal detection areas to make them more visible
				goal_color = (255, 0, 0)  # Red color
				# Draw pitch rectangle outline
				scaled_inner = SCALING.scale_rect(self.inner)
				scaled_inner.x += offset.x
				scaled_inner.y += offset.y
				pygame.draw.rect(self.surface, goal_color, scaled_inner, 3)
				# Goals are already in scaled coordinate system, just apply offset
				scaled_left_goal = self.left_goal.copy()
				scaled_right_goal = self.right_goal.copy()
				scaled_left_goal.x += offset.x
				scaled_left_goal.y += offset.y
				scaled_right_goal.x += offset.x
				scaled_right_goal.y += offset.y
				pygame.draw.rect(self.surface, goal_color, scaled_left_goal, 3)
				pygame.draw.rect(self.surface, goal_color, scaled_right_goal, 3)
			return
		
		# fallback vector field - draw scaled
		scaled_inner = SCALING.scale_rect(self.inner)
		scaled_inner.x += offset.x
		scaled_inner.y += offset.y
		pygame.draw.rect(self.surface, bg, scaled_inner)

		# Outer walls
		lines = CFG.colors.get("lines", (220, 220, 220))
		wt = int(self.wall_thickness * SCALING.uniform_scale)
		pygame.draw.rect(self.surface, lines, Rect(scaled_inner.left - wt, scaled_inner.top - wt, scaled_inner.width + 2 * wt, wt))
		pygame.draw.rect(self.surface, lines, Rect(scaled_inner.left - wt, scaled_inner.bottom, scaled_inner.width + 2 * wt, wt))
		pygame.draw.rect(self.surface, lines, Rect(scaled_inner.left - wt, scaled_inner.top, wt, scaled_inner.height))
		pygame.draw.rect(self.surface, lines, Rect(scaled_inner.right, scaled_inner.top, wt, scaled_inner.height))
		
		# Mid line and center circle
		center_x = scaled_inner.centerx
		center_y = scaled_inner.centery
		circle_radius = int(60 * SCALING.uniform_scale)
		pygame.draw.line(self.surface, lines, (center_x, scaled_inner.top), (center_x, scaled_inner.bottom), 2)
		pygame.draw.circle(self.surface, lines, (center_x, center_y), circle_radius, 2)
		
		# Goal boxes (sensor areas) - only show when debug is enabled
		if debug:
			# Use red color for goal detection areas to make them more visible
			goal_color = (255, 0, 0)  # Red color
			# Draw pitch rectangle outline
			pygame.draw.rect(self.surface, goal_color, scaled_inner, 3)
			# Goals are already in scaled coordinates, just apply offset for fallback vector field
			scaled_left_goal = self.left_goal.copy()
			scaled_right_goal = self.right_goal.copy()
			scaled_left_goal.x += offset.x
			scaled_left_goal.y += offset.y
			scaled_right_goal.x += offset.x
			scaled_right_goal.y += offset.y
			pygame.draw.rect(self.surface, goal_color, scaled_left_goal, 3)
			pygame.draw.rect(self.surface, goal_color, scaled_right_goal, 3)

	def reset_rects(self):
		"""Recompute field rectangles if window size or config changed dynamically."""
		# Store pitch rectangle in unscaled coordinates - SCALING.scale_rect() will handle scaling
		w, h = self.base_width, self.base_height
		m = CFG.field.get("margin", 40)
		self.inner = Rect(m, m, w - 2 * m, h - 2 * m)
		# Calculate goals using scaled coordinates to match teams and ball
		scaled_inner = self.get_scaled_inner()
		gw = int(CFG.field.get("goal_width", 140) * SCALING.uniform_scale)
		gd = int(CFG.field.get("goal_depth", 20) * SCALING.uniform_scale)
		y_goal = scaled_inner.centery - gw // 2
		# Position goals at the goal line (edge of the field) instead of inside
		self.left_goal = Rect(scaled_inner.left, y_goal, gd, gw)
		self.right_goal = Rect(scaled_inner.right - gd, y_goal, gd, gw)
		
		
		# Update field image if it exists
		self._update_field_image()
	
	def get_scaled_inner(self) -> pygame.Rect:
		"""Get the pitch rectangle in scaled coordinates for game logic."""
		return SCALING.scale_rect(self.inner)

