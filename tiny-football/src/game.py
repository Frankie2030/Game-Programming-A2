"""Main game loop and state machine for Tiny Football.

Handles input, physics updates, scoring, timers, and rendering.
"""

import time
import pygame
from pygame.math import Vector2 as V2
from settings import CFG
from scaling import SCALING
from pitch import Pitch
from hud import HUD
from entities.ball import Ball
from entities.team import Team
from physics.collisions import clamp_ball_with_walls, ball_player_collision
from physics.force_field import ForceField
from ai.simple_ai import SimpleAI


class Game:
	"""Encapsulates a running match.

	Args:
		surface: Target display surface.
		mode: Gameplay mode string.
		per_team: Number of players per team.
		minutes: Match duration in minutes.
	"""

	def __init__(self, surface: pygame.Surface, mode: str = None, per_team: int = None, minutes: int = 2, ai_difficulty: str = "Normal"):
		self.surface = surface
		self.clock = pygame.time.Clock()
		self.pitch = Pitch(surface)
		# Ensure pitch rectangle is properly scaled before initializing other components
		self.pitch.reset_rects()
		self.hud = HUD()
		self.ball = Ball(self.pitch.get_scaled_inner())
		self.force = ForceField(self.pitch.get_scaled_inner())
		# sounds
		self.muted = False
		self.background_music_playing = False
		try:
			import os
			base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
			# Original sounds
			goal_path = os.path.join(base_dir, "assets", "sfx", "goal.wav")
			bounce_path = os.path.join(base_dir, "assets", "sfx", "bounce.wav")
			# New sounds
			goal_net_path = os.path.join(base_dir, "assets", "sfx", "a-football-hits-the-net-goal-313216.mp3")
			bg_music_path = os.path.join(base_dir, "assets", "sfx", "football-crowd-3-69245.mp3")
			crowd_cheer_path = os.path.join(base_dir, "assets", "sfx", "crowd-cheering-379666.mp3")
			
			# Initialize pygame mixer if not already initialized
			if not pygame.mixer.get_init():
				pygame.mixer.init()
			
			if os.path.exists(goal_net_path):
				self.sfx_goal = pygame.mixer.Sound(goal_net_path)
			elif os.path.exists(goal_path):
				self.sfx_goal = pygame.mixer.Sound(goal_path)
			else:
				self.sfx_goal = None
				
			if os.path.exists(bounce_path):
				self.sfx_bounce = pygame.mixer.Sound(bounce_path)
			else:
				self.sfx_bounce = None
				
			if os.path.exists(bg_music_path):
				self.bg_music_path = bg_music_path
			else:
				self.bg_music_path = None
				
			if os.path.exists(crowd_cheer_path):
				self.sfx_crowd_cheer = pygame.mixer.Sound(crowd_cheer_path)
			else:
				self.sfx_crowd_cheer = None
		except Exception as e:
			print(f"Error loading sounds: {e}")
			self.sfx_goal = None
			self.sfx_bounce = None
			self.bg_music_path = None
			self.sfx_crowd_cheer = None
		self.score_l = 0
		self.score_r = 0
		self.hits_l = 0
		self.hits_r = 0
		self.paused = False
		self.debug = False
		# self.mode = mode or str(CFG.raw.get("mode", "multiplayer"))
		self.mode = mode or str(CFG.raw.get("mode", "multiplayer"))
		self.ai_difficulty = ai_difficulty
		if per_team is not None:
			CFG.teams["per_team"] = int(per_team)
		self.match_time = max(1, int(minutes)) * 60.0
		self.time_left = self.match_time
		self.state = "countdown"  # countdown | playing | goal_pause | finished
		self.countdown_timer = 3.0
		self.reset_positions(kickoff=True)
		self.last_time = time.time()
		self.dt = 1.0 / max(1, CFG.fps)
		self.ai_enabled = bool(CFG.raw.get("ai", {}).get("enabled", True))
		if self.ai_enabled:
			self.ai_l = SimpleAI(True, difficulty=self.ai_difficulty)
			self.ai_r = SimpleAI(False, difficulty=self.ai_difficulty)

		# Start background music
		self.start_background_music()
		
		# Goal sound timing
		self.goal_sound_playing = False
		self.goal_sound_timer = 0.0

	def reset_positions(self, kickoff: bool = False) -> None:
		"""Recreate teams and position the ball and players for kickoff."""
		if kickoff:
			self.ball.spawn(self.pitch.get_scaled_inner().center, direction_randomized=False)
			self.ball.vel.update(0, 0)  # Remove initial ball speed and direction
		else:
			self.ball.spawn(self.pitch.get_scaled_inner().center, direction_randomized=True)
		controls_p1 = {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d, "cycle": pygame.K_TAB}
		# For P2, use 'K' to cycle as requested
		controls_p2 = {"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT, "cycle": pygame.K_k}
		self.team_l = Team(True, self.pitch.get_scaled_inner(), controls_p1, "p1")
		# self.team_r = Team(False, self.pitch.get_scaled_inner(), controls_p2, "p2")
		# If human_vs_ai, make right team's non-nearest players stay on line
		# self.human_vs_ai = (self.mode == "human_vs_ai")
		if self.mode == "human_vs_ai":
			# Right team: AI controlled
			self.team_r = Team(False, self.pitch.get_scaled_inner(), controls_p2, "p2")
			for player in self.team_r.players:
				player.is_ai = True
				player.ai_difficulty = self.ai_difficulty
		else:
			# Default (multiplayer)
			self.team_r = Team(False, self.pitch.get_scaled_inner(), controls_p2, "p2")
		
	def rescale_game_elements(self) -> None:
		"""Rescale all game elements to match the new window size."""
		# Update ball properties and position
		self.ball.radius = SCALING.scale_radius(10)  # Base radius from config
		self.ball.max_speed = SCALING.scale_speed(520)  # Base max speed
		self.ball.rescale_position(self.pitch.get_scaled_inner())

		# Rescale team positions to fit new field
		self.team_l.rescale_positions(self.pitch.get_scaled_inner())
		self.team_r.rescale_positions(self.pitch.get_scaled_inner())

		# Update player properties
		for player in self.team_l.players + self.team_r.players:
			player.radius = SCALING.scale_radius(16)  # Base radius from config
			player.max_speed = SCALING.scale_speed(260)  # Base max speed
			player.accel = SCALING.scale_acceleration(1400)  # Base acceleration

	def start_background_music(self):
		"""Start the background music if available and not muted."""
		if self.bg_music_path and not self.muted:
			try:
				# Ensure mixer is initialized
				if not pygame.mixer.get_init():
					pygame.mixer.init()
				
				# Stop any currently playing music first
				if self.background_music_playing:
					pygame.mixer.music.stop()
					
				pygame.mixer.music.load(self.bg_music_path)
				pygame.mixer.music.play(-1)  # Loop indefinitely
				self.background_music_playing = True
			except Exception as e:
				print(f"Error starting background music: {e}")
				self.background_music_playing = False

	def stop_background_music(self):
		"""Stop the background music."""
		if self.background_music_playing:
			try:
				pygame.mixer.music.stop()
				self.background_music_playing = False
			except Exception as e:
				print(f"Error stopping background music: {e}")
				self.background_music_playing = False

	def update(self, dt: float) -> None:
		"""Advance simulation by dt seconds and handle state transitions."""
		# Handle goal sound timing - both sound and countdown happen simultaneously
		if self.goal_sound_playing:
			self.goal_sound_timer -= dt
			if self.goal_sound_timer <= 0:
				self.goal_sound_playing = False
			# Don't return here - let countdown logic handle the state transition
		
		# Handle different game states and their transitions
		if self.state == "countdown":
			# 3-2-1 countdown before match starts
			self.countdown_timer -= dt
			if self.countdown_timer <= 0:
				self.state = "playing"
			return
		if self.state == "goal_pause":
			# Brief pause after scoring
			self.countdown_timer -= dt
			if self.countdown_timer <= 0:
				self.state = "playing"
			return
		if self.state == "finished":
			# Game over - no updates
			return
			
		# Update match timer and check for end of match
		self.time_left -= dt
		if self.time_left <= 0:
			self.state = "finished"
			self.time_left = 0
			# Stop background music and play crowd cheering
			self.stop_background_music()
			if self.sfx_crowd_cheer and not self.muted:
				self.sfx_crowd_cheer.play()
			return
			
		# Update ball physics (position, velocity, friction)
		self.ball.update(dt)
		
		# Apply force field effects (gravity, wind, etc.)
		self.force.apply(self.ball, dt)
		
		# Handle ball-wall collisions with sound effects
		if clamp_ball_with_walls(self.ball) and getattr(self, "sfx_bounce", None) and not getattr(self, "muted", False):
			self.sfx_bounce.play()
			
		# Update AI predictions for both teams
		if self.ai_enabled:
			# Pass home_x for line-locked prediction (left uses its players' home_x; right similarly)
			lx = self.team_l.players[-1].home_x if self.team_l.players else self.pitch.get_scaled_inner().left + 80
			rx = self.team_r.players[-1].home_x if self.team_r.players else self.pitch.get_scaled_inner().right - 80
			self.ai_l.update(dt, self.pitch.get_scaled_inner(), V2(self.ball.pos), V2(self.ball.vel), self.team_l.players)
			self.ai_r.update(dt, self.pitch.get_scaled_inner(), V2(self.ball.pos), V2(self.ball.vel), self.team_r.players)

			
		# Check ball-player collisions and update hit counters
		# Also update ball possession tracking for AI decision-making
		for p in self.team_l.players:
			if ball_player_collision(self.ball, p):
				self.hits_l += 1
			# Update possession based on proximity (for AI to know who has ball)
			delta = self.ball.pos - p.pos
			possession_margin = p.radius + self.ball.radius + 8  # slightly larger than kick range
			p.has_ball = (delta.length_squared() <= possession_margin * possession_margin)
		for p in self.team_r.players:
			if ball_player_collision(self.ball, p):
				self.hits_r += 1
			# Update possession based on proximity
			delta = self.ball.pos - p.pos
			possession_margin = p.radius + self.ball.radius + 8
			p.has_ball = (delta.length_squared() <= possession_margin * possession_margin)
				
		# Check for goals: ball center must enter the sensor rectangle
		if self.pitch.left_goal.collidepoint(int(self.ball.pos.x), int(self.ball.pos.y)):
			self.score_r += 1
			self._goal_scored()
		elif self.pitch.right_goal.collidepoint(int(self.ball.pos.x), int(self.ball.pos.y)):
			self.score_l += 1
			self._goal_scored()

	def _goal_scored(self) -> None:
		"""Enter a brief pause after scoring and reset for kickoff."""
		# stop ball at center and play goal sound
		self.ball.spawn(self.pitch.get_scaled_inner().center, direction_randomized=False)
		self.ball.vel.update(0, 0)
		
		# Play goal sound and set countdown - both happen simultaneously for 3 seconds
		if self.sfx_goal and not self.muted:
			try:
				self.sfx_goal.play()
				# Both goal sound and countdown happen together for 3 seconds
				self.goal_sound_timer = 3.0
				self.goal_sound_playing = True
				self.countdown_timer = 3.0  # Countdown also runs for 3 seconds
			except Exception as e:
				print(f"Error playing goal sound: {e}")
				self.countdown_timer = 3.0  # Still do 3-second countdown even without sound
				self.goal_sound_playing = False
		else:
			self.countdown_timer = 3.0  # 3-second countdown even without sound
			self.goal_sound_playing = False
			
		self.state = "goal_pause"
		self.reset_positions(kickoff=False)
	def _handle_system_events(self, events):
		"""Window resize and system-level handling."""
		for event in events:
			if event.type == pygame.VIDEORESIZE:
				SCALING.update_size(event.w, event.h)
				pygame.display.set_mode((SCALING.current_width, SCALING.current_height), pygame.RESIZABLE)
				self.pitch.reset_rects()
				self.ball.play_rect = self.pitch.get_scaled_inner()
				self.force.pitch_rect = self.pitch.get_scaled_inner()
				self.rescale_game_elements()

	def _handle_game_state_events(self, events):
		"""Pause, restart, mute/unmute."""
		for e in events:
			if e.type == pygame.KEYDOWN:
				if e.key == pygame.K_p:
					self.paused = not self.paused
				elif e.key == pygame.K_r:
					self._restart_game()
				elif e.key == pygame.K_m:
					self.muted = not self.muted
					if self.muted:
						self.stop_background_music()
					else:
						self.start_background_music()

	def _handle_debug_events(self, events):
		"""Toggle debug info and HUD stats."""
		for e in events:
			if e.type == pygame.KEYDOWN and e.key == pygame.K_b:
				self.hud.toggle_live_stats()
				self.debug = not self.debug
				self.hud.debug = self.debug

	def _handle_ai_team(self, team, ai):
		"""AI controls all players in a team."""
		for p in team.players:
			direction = ai.advise_direction(p)
			p.move(direction, self.dt, self.pitch.get_scaled_inner())

	def _handle_kicks(self, events):
		"""Handle manual and automatic kicking."""
		if any(e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE for e in events):
			self.team_l.try_kick(self.ball)
		if any(e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN for e in events):
			self.team_r.try_kick(self.ball)

		# Auto kick when overlapping
		self.team_l.try_kick(self.ball)
		self.team_r.try_kick(self.ball)

	def _restart_game(self):
		"""Restart or reset match."""
		if self.state == "finished":
			self.score_l = self.score_r = 0
			self.hits_l = self.hits_r = 0
			self.time_left = self.match_time
			self.state = "countdown"
			self.countdown_timer = 3.0
			self.goal_sound_playing = False
			self.goal_sound_timer = 0.0
			self.reset_positions(kickoff=True)
			if not self.muted:
				self.start_background_music()
		else:
			self.reset_positions(kickoff=True)

	def handle_input(self, events: list) -> None:
		"""Process all input events including keyboard, game state changes, and AI behavior."""

		# --- 1. Handle system-level events (resize, quit, etc.) ---
		self._handle_system_events(events)

		# If paused, allow only unpause
		if self.paused:
			if any(e.type == pygame.KEYDOWN and e.key == pygame.K_p for e in events):
				self.paused = False
			return

		pressed = pygame.key.get_pressed()

		# --- 2. Handle debug, pause, restart, mute ---
		self._handle_game_state_events(events)
		self._handle_debug_events(events)

		# --- 3. Human team input ---
		# restrict = CFG.teams.get("per_team", 2) > 1
		restrict = False
		self.team_l.handle_input(pressed, events, self.dt, self.pitch.get_scaled_inner(), restrict_half=restrict)

		# Right team → AI or human depending on mode
		if self.mode == "human_vs_ai":
			self._handle_ai_team(self.team_r, self.ai_r)
		elif self.mode == "multiplayer_ai":
			self._handle_ai_team(self.team_l, self.ai_l)
			self._handle_ai_team(self.team_r, self.ai_r)
		else:  # default multiplayer
			self.team_r.handle_input(pressed, events, self.dt, self.pitch.get_scaled_inner(), restrict_half=restrict)

		# --- 4. Handle manual & auto kicking ---
		self._handle_kicks(events)

	def draw(self, fps_val: float) -> None:
		"""Render the current frame contents."""
		self.surface.fill(CFG.colors.get("bg", (18, 110, 18)))
		# Disable debug indicators when game is finished
		show_debug = self.debug and self.state != "finished"
		game_finished = (self.state == "finished")
		self.pitch.draw(debug=show_debug)
		self.ball.draw(self.surface, debug=show_debug)
		self.team_l.draw(self.surface, debug=show_debug, game_finished=game_finished)
		self.team_r.draw(self.surface, debug=show_debug, game_finished=game_finished)
		# draw AI hint markers
		if self.ai_enabled:
			self.ai_l.draw_hint(self.surface, debug=show_debug)
			self.ai_r.draw_hint(self.surface, debug=show_debug)
		force_label = ""
		if self.force.enabled:
			force_label = f"{self.force.kind.title()} ON: {self.force.strength:.0f}"
		self.hud.draw(self.surface, self.score_l, self.score_r, self.hits_l, self.hits_r, fps_val, force_label, time_left=self.time_left if self.state != "countdown" else self.match_time)
		# Draw live stats if enabled
		self.hud.draw_live_stats(self.surface, self.ball, [self.team_l, self.team_r])
		# overlay countdown or winner screen
		if self.state in ("countdown", "goal_pause"):
			# Fix countdown display: use ceiling for proper 3-2-1 timing
			import math
			countdown_display = math.ceil(self.countdown_timer)
			self._draw_center_text(f"{countdown_display}")
		elif self.state == "finished":
			winner = "Draw" if self.score_l == self.score_r else ("P1 Wins" if self.score_l > self.score_r else "P2 Wins")
			self._draw_center_text(f"{winner}")
			self._draw_sub_text("Press R to restart or Esc to quit")
			# Debug stats are disabled when game is finished for clean finish screen

	def _draw_center_text(self, text: str) -> None:
		"""Draw a large centered text overlay."""
		font_size = SCALING.scale_font_size(96)
		font = pygame.font.SysFont(None, font_size)
		surf = font.render(text, True, (255, 255, 255))
		# Center on the actual screen center
		center_pos = SCALING.apply_offset(SCALING.scale_position(V2(self.pitch.inner.center)))
		rect = surf.get_rect(center=(int(center_pos.x), int(center_pos.y)))
		self.surface.blit(surf, rect)

	def _draw_sub_text(self, text: str) -> None:
		"""Draw smaller text under the main overlay message."""
		font_size = SCALING.scale_font_size(28)
		font = pygame.font.SysFont(None, font_size)
		surf = font.render(text, True, (240, 240, 240))
		# Position below center text
		center_pos = SCALING.apply_offset(SCALING.scale_position(V2(self.pitch.inner.center)))
		offset_y = SCALING.scale_radius(80)
		rect = surf.get_rect(center=(int(center_pos.x), int(center_pos.y + offset_y)))
		self.surface.blit(surf, rect)

	def run_frame(self) -> bool:
		"""Process one frame. Returns False to exit the program loop."""
		events = pygame.event.get()
		# compute dt first so input-driven movement uses this frame's dt
		frame_ms = self.clock.tick(CFG.fps)
		self.dt = frame_ms / 1000.0 if frame_ms > 0 else self.dt
		for e in events:
			if e.type == pygame.QUIT:
				return False
			if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
				return False
		self.handle_input(events)
		if not self.paused:
			# sub-steps for very fast ball
			steps = 2 if self.ball.vel.length() > 0.75 * self.ball.max_speed else 1
			for _ in range(steps):
				self.update(self.dt / steps)
		else:
			pass
		fps_val = self.clock.get_fps()
		self.draw(fps_val)
		pygame.display.flip()
		return True
