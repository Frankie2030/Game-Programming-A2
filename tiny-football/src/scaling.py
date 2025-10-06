import pygame
from pygame.math import Vector2 as V2
from settings import CFG

class ScalingManager:
	def __init__(self, base_width: int, base_height: int):
		self.base_width = base_width
		self.base_height = base_height
		self.current_width = base_width
		self.current_height = base_height
		self.scale_x = 1.0
		self.scale_y = 1.0
		self.uniform_scale = 1.0
		
	def update_size(self, new_width: int, new_height: int):
		"""Update scaling factors based on new window size, forcing uniform scaling."""
		# Calculate aspect ratios
		base_aspect = self.base_width / self.base_height
		new_aspect = new_width / new_height
		
		# Force uniform scaling by constraining to aspect ratio
		if new_aspect > base_aspect:
			# Window is too wide - constrain width
			adjusted_width = int(new_height * base_aspect)
			adjusted_height = new_height
		else:
			# Window is too tall - constrain height
			adjusted_width = new_width
			adjusted_height = int(new_width / base_aspect)
		
		self.current_width = adjusted_width
		self.current_height = adjusted_height
		
		# Use uniform scaling only
		self.uniform_scale = adjusted_width / self.base_width  # Same as adjusted_height / self.base_height
		self.scale_x = self.uniform_scale
		self.scale_y = self.uniform_scale
		
		# Update CFG size for other components
		CFG.window["width"] = adjusted_width
		CFG.window["height"] = adjusted_height
	
	def scale_position(self, pos: V2) -> V2:
		"""Scale a position vector using uniform scaling to maintain aspect ratio."""
		return V2(
			pos.x * self.uniform_scale,
			pos.y * self.uniform_scale
		)
	
	def scale_radius(self, radius: float) -> float:
		"""Scale a radius value using uniform scaling."""
		return radius * self.uniform_scale
	
	def scale_speed(self, speed: float) -> float:
		"""Scale a speed value using uniform scaling."""
		return speed * self.uniform_scale
	
	def scale_acceleration(self, accel: float) -> float:
		"""Scale acceleration values using uniform scaling."""
		return accel * self.uniform_scale
	
	def get_offset(self) -> V2:
		"""Get offset to center uniformly scaled content in the window."""
		# Calculate how much space we have after uniform scaling
		scaled_width = self.base_width * self.uniform_scale
		scaled_height = self.base_height * self.uniform_scale
		
		# Center the scaled content
		offset_x = (self.current_width - scaled_width) / 2
		offset_y = (self.current_height - scaled_height) / 2
		
		return V2(offset_x, offset_y)
	
	def apply_offset(self, pos: V2) -> V2:
		"""Apply uniform scaling and offset to a position."""
		scaled_pos = self.scale_position(pos)
		offset = self.get_offset()
		return scaled_pos + offset
	
	def scale_rect(self, rect: pygame.Rect) -> pygame.Rect:
		"""Scale a rectangle using uniform scaling."""
		return pygame.Rect(
			rect.x * self.uniform_scale,
			rect.y * self.uniform_scale,
			rect.width * self.uniform_scale,
			rect.height * self.uniform_scale
		)
	
	def scale_font_size(self, font_size: int) -> int:
		"""Scale font size using uniform scaling."""
		return int(font_size * self.uniform_scale)
	
	def create_scaled_surface(self, size: tuple) -> pygame.Surface:
		"""Create a surface scaled to current window size."""
		scaled_size = (int(size[0] * self.uniform_scale), int(size[1] * self.uniform_scale))
		return pygame.Surface(scaled_size)

# Initialize with default window size from CFG
SCALING = ScalingManager(CFG.size[0], CFG.size[1])
