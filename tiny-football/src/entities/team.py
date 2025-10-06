"""Team container with player selection and input handling."""

import pygame
from pygame.math import Vector2 as V2
from typing import List, Dict
from settings import CFG
from .player import Player


class Team:
	"""Holds players, selected index, and control bindings."""
	
	def __init__(self, left_side: bool, pitch_rect: pygame.Rect, controls: Dict[str, int], color_key: str):
		"""Initialize team with players and control configuration."""
		self.left_side = left_side
		self.controls = controls
		self.players: List[Player] = []
		self.selected_idx = 0
		self.pitch_rect = pitch_rect  # Store pitch rect for rescaling

		active_glow = CFG.colors.get("active_glow", (255, 213, 79))
		color = CFG.colors.get(color_key, (76, 175, 80))
		num = int(max(1, min(CFG.teams.get("per_team", 2), CFG.teams.get("max_per_team", 5))))

		print(f"\n=== TEAM {'P1' if left_side else 'P2'} INIT DEBUG ===")
		print(f"Received pitch_rect for initialization: {pitch_rect}")
		print(f"Pitch rect width: {pitch_rect.width}, height: {pitch_rect.height}")
		
		for i in range(num):
			# Position players in better positions on the field
			if left_side:
				# Left team: position at 15% from left edge (more towards center)
				x = pitch_rect.left + pitch_rect.width * 0.15
			else:
				# Right team: position at 15% from right edge (more towards center)
				x = pitch_rect.right - pitch_rect.width * 0.15
			
			y = pitch_rect.centery + (i - (num - 1) / 2) * (CFG.player.get("radius", 16) * 3)
			# Create player name based on team and player number
			team_num = "1" if left_side else "2"
			player_name = f"P{team_num}-{i+1}"
			print(f"  {player_name}: calculated pos({x:.1f}, {y:.1f})")
			self.players.append(Player(V2(x, y), color, active_glow, color_key, player_name, pitch_rect, left_side))

		self.players[self.selected_idx].is_active = True

	def handle_input(self, pressed: pygame.key.ScancodeWrapper, events: list, dt: float, pitch_rect: pygame.Rect, restrict_half: bool = False) -> V2:
		"""Process input events and update selected player movement."""
		move_vec = V2(0, 0)
		if not self.controls:
			return None
		if pressed[self.controls["up"]]:
			move_vec.y -= 1
		if pressed[self.controls["down"]]:
			move_vec.y += 1
		if pressed[self.controls["left"]]:
			move_vec.x -= 1
		if pressed[self.controls["right"]]:
			move_vec.x += 1

		# activation keys: numbers and cycle
		for e in events:
			if e.type == pygame.KEYDOWN:
				if e.key == self.controls.get("cycle"):
					self._cycle()
				
				# Separate number keys for each team
				if self.left_side:
					# Left team uses keys 1-5
					if pygame.K_1 <= e.key <= pygame.K_5:
						i = e.key - pygame.K_1
						self._select(i)
				else:
					# Right team uses keys 6-9-0 (6,7,8,9,0)
					if e.key == pygame.K_6:
						self._select(0)
					elif e.key == pygame.K_7:
						self._select(1)
					elif e.key == pygame.K_8:
						self._select(2)
					elif e.key == pygame.K_9:
						self._select(3)
					elif e.key == pygame.K_0:
						self._select(4)

		if move_vec.length_squared() > 0:
			move_vec = move_vec.normalize()
		
		# Movement only for selected player (removed group functionality)
		self.players[self.selected_idx].move(move_vec, dt, pitch_rect)
		if restrict_half:
			self._clamp_half(self.players[self.selected_idx], pitch_rect)
		return move_vec

	def try_kick(self, ball) -> bool:
		"""Attempt to kick the ball with any team player."""
		kicked = False
		for p in self.players:
			kicked = p.kick(ball) or kicked
		return kicked

	def _cycle(self) -> None:
		"""Cycle to the next player in the team."""
		self.players[self.selected_idx].is_active = False
		self.selected_idx = (self.selected_idx + 1) % len(self.players)
		self.players[self.selected_idx].is_active = True

	def _select(self, idx: int) -> None:
		"""Select a specific player by index."""
		if 0 <= idx < len(self.players):
			self.players[self.selected_idx].is_active = False
			self.selected_idx = idx
			self.players[self.selected_idx].is_active = True

	def draw(self, surface: pygame.Surface, debug: bool = False, game_finished: bool = False) -> None:
		"""Draw all team players on the surface."""
		for p in self.players:
			p.draw(surface, debug, game_finished)

	def _clamp_half(self, player: Player, pitch_rect: pygame.Rect) -> None:
		"""Prevent team players from crossing the center line."""
		# Prevent this team's players from crossing the center line
		cx = pitch_rect.centerx
		if self.left_side:
			player.pos.x = min(player.pos.x, cx - player.radius)
		else:
			player.pos.x = max(player.pos.x, cx + player.radius)
			
	def rescale_positions(self, new_pitch_rect: pygame.Rect) -> None:
		"""Rescale all player positions to fit the new field size."""
		team_name = "P1" if self.left_side else "P2"
		print(f"\n=== TEAM {team_name} RESCALE DEBUG ===")
		print(f"Received new_pitch_rect for rescaling: {new_pitch_rect}")
		print(f"New pitch rect width: {new_pitch_rect.width}, height: {new_pitch_rect.height}")
		
		for i, player in enumerate(self.players):
			old_pos = player.pos.copy()
			old_percent_x = player.percent_x
			old_percent_y = player.percent_y
			
			# Use the stored percentage positions to calculate new absolute positions
			player.set_position_from_percentage(new_pitch_rect)
			
			print(f"  {team_name}-{i+1}:")
			print(f"    OLD: pos({old_pos.x:.1f},{old_pos.y:.1f}) percent({old_percent_x:.3f},{old_percent_y:.3f})")
			print(f"    NEW: pos({player.pos.x:.1f},{player.pos.y:.1f}) percent({player.percent_x:.3f},{player.percent_y:.3f})")
		
		# Store new pitch rect for future reference
		self.pitch_rect = new_pitch_rect

