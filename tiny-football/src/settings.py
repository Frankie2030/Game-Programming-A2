import json
import os
from dataclasses import dataclass
from typing import Dict, Tuple, Any


def _hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
	"""Convert hex color string to RGB tuple."""
	hex_str = hex_str.strip().lstrip('#')
	if len(hex_str) == 3:
		hex_str = ''.join(ch * 2 for ch in hex_str)
	r = int(hex_str[0:2], 16)
	g = int(hex_str[2:4], 16)
	b = int(hex_str[4:6], 16)
	return (r, g, b)

# This is the default configuration file if the user does not have a config.json file
DEFAULT_CFG: Dict[str, Any] = {
	"window": {"width": 960, "height": 540, "fps": 60},
	"field": {"margin": 40, "wall_thickness": 8, "goal_width": 140, "goal_depth": 20},
	"ball": {"radius": 10, "base_speed": 320, "max_speed": 520, "restitution": 0.98, "friction": 0.995},
	"player": {"radius": 16, "speed": 260, "accel": 2600, "drag": 0.90},
	"teams": {"per_team": 2, "max_per_team": 5},
	"colors": {"p1": "#4CAF50", "p2": "#2196F3", "active_glow": "#FFD54F", "ball": "#FF7043", "bg": "#0B4F26", "lines": "#DDDDDD"},
	"force_field": {"enabled": False, "type": "wind", "strength": 80},
	"ai": {"enabled": True, "line_locked": True},
	"mode": "multiplayer",  # multiplayer | human_vs_ai | two_plus_ai
	"hud": {"font_size": 20, "show_fps": True},
}


class Settings:
	"""Manages game configuration loaded from config.json with fallback defaults."""
	
	def __init__(self, cfg: Dict[str, Any]):
		"""Initialize settings from configuration dictionary"""
		self.raw = cfg
		self.window = cfg.get("window", {})
		self.field = cfg.get("field", {})
		self.ball = cfg.get("ball", {})
		self.player = cfg.get("player", {})
		self.teams = cfg.get("teams", {})
		self.force_field = cfg.get("force_field", {})
		self.hud = cfg.get("hud", {})
		self.colors_hex = cfg.get("colors", {})
		self.colors = {k: _hex_to_rgb(v) for k, v in self.colors_hex.items()}
		# derived defaults for menu
		self.default_minutes = int(cfg.get("match", {}).get("minutes", 2)) if cfg.get("match") else 2

	@property
	def size(self) -> Tuple[int, int]:
		"""Get window dimensions as (width, height) tuple."""
		return int(self.window.get("width", 960)), int(self.window.get("height", 540))

	@property
	def fps(self) -> int:
		"""Get target frames per second for the game loop."""
		return int(self.window.get("fps", 60))


def load_settings() -> Settings:
	"""Load game settings from config.json, falling back to defaults if file is missing or malformed"""
	base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	config_path = os.path.join(base_dir, "config.json")
	cfg = DEFAULT_CFG.copy()
	try:
		if os.path.exists(config_path):
			with open(config_path, "r", encoding="utf-8") as f:
				user_cfg = json.load(f)
				# Shallow merge user overrides into defaults
				for k, v in user_cfg.items():
					if isinstance(v, dict) and isinstance(cfg.get(k), dict):
						cfg[k].update(v)
					else:
						cfg[k] = v
	except Exception:
		# Fall back to defaults if config is malformed
		pass
	return Settings(cfg)


# Singleton-like config access
CFG = load_settings()

