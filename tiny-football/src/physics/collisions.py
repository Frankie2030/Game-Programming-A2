"""Collision utilities for wall and circle interactions.

All functions in this module use tab indentation to match the codebase.
"""

import pygame
from pygame.math import Vector2 as V2
from typing import Tuple
from settings import CFG



def clamp_ball_with_walls(ball) -> bool:
	"""Clamp the ball to the play rectangle and reflect its velocity on impact.

	WALL COLLISION PHYSICS:
	
	1. Collision Detection (distance from wall):
	   For horizontal walls: ball.pos.x ± radius vs wall.x

	   For vertical walls: ball.pos.y ± radius vs wall.y
	
	2. Position Correction (clamping to prevent overlap):
	   ball.pos.x = clamp(ball.pos.x, wall_left + radius, wall_right - radius)

	   ball.pos.y = clamp(ball.pos.y, wall_top + radius, wall_bottom - radius)
	
	3. Velocity Reflection (elastic collision):
	   For horizontal walls: velocity_new = velocity_old.reflect(V2(1, 0))

	   For vertical walls: velocity_new = velocity_old.reflect(V2(0, 1))
	
	4. Restitution (energy loss):
	   speed_new = speed_old * restitution_coefficient

	   Where: restitution_coefficient = 0.98 (2% energy loss per bounce)
	
	Returns True if a reflection occurred this update, False otherwise.
	"""
	restitution = float(CFG.ball.get("restitution", 0.98))
	inner = ball.play_rect
	r = ball.radius
	reflected = False
	
	# Check horizontal wall collisions (left and right walls)
	if ball.pos.x - r < inner.left:
		# Ball hit left wall - clamp position and reflect velocity
		ball.pos.x = inner.left + r
		ball.vel.reflect_ip(V2(1, 0))  # Reflect off vertical surface
		reflected = True
	elif ball.pos.x + r > inner.right:
		# Ball hit right wall - clamp position and reflect velocity
		ball.pos.x = inner.right - r
		ball.vel.reflect_ip(V2(1, 0))  # Reflect off vertical surface
		reflected = True
		
	# Check vertical wall collisions (top and bottom walls)
	if ball.pos.y - r < inner.top:
		# Ball hit top wall - clamp position and reflect velocity
		ball.pos.y = inner.top + r
		ball.vel.reflect_ip(V2(0, 1))  # Reflect off horizontal surface
		reflected = True
	elif ball.pos.y + r > inner.bottom:
		# Ball hit bottom wall - clamp position and reflect velocity
		ball.pos.y = inner.bottom - r
		ball.vel.reflect_ip(V2(0, 1))  # Reflect off horizontal surface
		reflected = True
		
	# Apply restitution (energy loss) after collision
	if reflected:
		try:
			spd = ball.vel.length()
			if spd > 0:
				ball.vel.scale_to_length(spd * restitution)
		except Exception:
			# Fallback to simple multiplication if scaling fails
			ball.vel *= restitution
	return reflected



def ball_player_collision(ball, player) -> bool:
	"""Resolve circle-circle collision between ball and a player.

	CIRCLE-CIRCLE COLLISION PHYSICS:
	
	1. Collision Detection (distance between centers):
	
	   distance = |ball_pos - player_pos| 

	   collision = distance < (ball_radius + player_radius)
	
	2. Collision Normal (unit vector from player to ball):
	   normal = (ball_pos - player_pos) / |ball_pos - player_pos|

	   Edge case: if distance = 0, use default direction (1, 0)
	
	3. Position Correction (separate overlapping objects):
	   ball_pos = player_pos + normal * (radius_sum + small_offset)

	   Where: radius_sum = ball_radius + player_radius
	
	4. Velocity Reflection (elastic collision with normal):
	   ball_velocity = ball_velocity.reflect(collision_normal)
	
	5. Restitution (energy loss):
	   speed_new = speed_old * restitution_coefficient

	   Where: restitution_coefficient = 0.98 (2% energy loss per collision)
	
	6. Momentum Transfer (realistic ball-player interaction):
	   ball_velocity += player_velocity * 0.25

	   This transfers 25% of player's momentum to the ball
	
	Returns True when a collision was resolved.
	"""
	restitution = float(CFG.ball.get("restitution", 0.98))
	r_sum = ball.radius + player.radius
	delta = ball.pos - player.pos
	dist = delta.length()
	
	# Handle edge case where objects are exactly on top of each other
	if dist == 0:
		delta = V2(1, 0)
		dist = 1.0
		
	# Check if collision occurred (distance between centers < sum of radii)
	if dist < r_sum:
		# Calculate collision normal (direction from player to ball)
		n = delta / dist
		
		# Separate objects by moving ball outside player
		ball.pos = player.pos + n * (r_sum + 0.01)
		
		# Store original speed for restitution calculation
		prev_speed = ball.vel.length() or 0.0
		
		# Reflect ball velocity off the collision normal
		ball.vel.reflect_ip(n)
		
		# Apply restitution (energy loss) to reflected velocity
		if prev_speed > 0:
			ball.vel.scale_to_length(prev_speed * restitution)
			
		# Transfer some player velocity to ball for realistic feel
		ball.vel += player.vel * 0.25
		return True
	return False

