"""Smarter AI advisor with per-player roles, attacking & defending logic, and difficulty scaling."""

import random
import pygame
from pygame.math import Vector2 as V2


class SimpleAI:
    """AI that controls a whole team with roles, attacking, defending, and difficulty scaling."""

    def __init__(self, side_left: bool, difficulty: str = "Normal"):
        self.left = side_left
        self.difficulty = difficulty
        self.targets = {}   # player -> Vector2 target
        self.hints = {}     # debug hints
        self.timer = 0.0

        self.set_difficulty(difficulty)

    def set_difficulty(self, difficulty: str) -> None:
        """Adjust AI reaction speed, accuracy, and awareness based on difficulty."""
        self.difficulty = difficulty
        if difficulty == "Easy":
            self.reaction = 0.1
            self.error_range = 9
            self.awareness = 0.7
        elif difficulty == "Hard":
            self.reaction = 0.03
            self.error_range = 2
            self.awareness = 0.95
        else:  # Normal
            self.reaction = 0.05
            self.error_range = 6
            self.awareness = 0.8

    # def update(self, dt: float, pitch_rect: pygame.Rect, ball_pos: V2, ball_vel: V2, players: list) -> None:
    #     """Update AI targets for each player based on roles and ball state."""
    #     self.timer += dt
    #     if self.timer < self.reaction:
    #         return
    #     self.timer = 0.0

    #     # Define goals (always attack opposite)
    #     if self.left:
    #         my_goal = V2(pitch_rect.left + 20, pitch_rect.centery)
    #         opp_goal = V2(pitch_rect.right - 20, pitch_rect.centery)
    #     else:
    #         my_goal = V2(pitch_rect.right - 20, pitch_rect.centery)
    #         opp_goal = V2(pitch_rect.left + 20, pitch_rect.centery)

    #     # Nearest player to ball = main actor
    #     nearest = min(players, key=lambda p: (p.pos - ball_pos).length_squared())

    #     for i, p in enumerate(players):
    #         has_ball = getattr(p, "has_ball", False)

    #         if has_ball:
    #             # 🚀 Ball carrier → go directly to opponent's goal
    #             goal_height = 100
    #             goal_y = opp_goal.y + random.uniform(-goal_height / 2, goal_height / 2)
    #             target = V2(opp_goal.x, goal_y)
    #             if (p.pos - opp_goal).length() < 200:  
    #                 target = opp_goal
				
    #         elif p is nearest:
    #             # 🏃 Nearest player w/o ball → ATTACK or DEFEND
    #             if self._ball_heading_to_goal(ball_pos, ball_vel, my_goal, pitch_rect):
    #                 if random.random() < self.awareness:
    #                     target = self._predict_intercept(ball_pos, ball_vel, my_goal, pitch_rect) or my_goal
    #                 else:
    #                     target = ball_pos + ball_vel * 0.2
    #             else:
    #                 # Attack ball
    #                 target = ball_pos + ball_vel * 0.4
    #         else:
    #             # Support → move in formation in own half, ready to support
    #             # Position support players in their own half, not opponent's half
    #             if self.left:
    #                 # Left team: position support players in left half
    #                 base_x = pitch_rect.left + pitch_rect.width * 0.3  # 30% from left edge
    #             else:
    #                 # Right team: position support players in right half  
    #                 base_x = pitch_rect.right - pitch_rect.width * 0.3  # 30% from right edge
                
    #             spacing = 80
    #             offset_y = (i * spacing) - (len(players) * spacing / 2)

    #             # Base formation in own half
    #             target = V2(
    #                 base_x,
    #                 pitch_rect.centery + offset_y
    #             )

    #         # Clamp target inside field
    #         target.x = max(pitch_rect.left + 20, min(pitch_rect.right - 20, target.x))
    #         target.y = max(pitch_rect.top + 20, min(pitch_rect.bottom - 20, target.y))

    #         # 🎯 Apply difficulty-based error (skip if defending near own goal)
    #         if not self._ball_heading_to_goal(ball_pos, ball_vel, my_goal, pitch_rect):
    #             target += V2(
    #                 random.uniform(-self.error_range, self.error_range),
    #                 random.uniform(-self.error_range, self.error_range),
    #             )

    #         self.targets[p] = target
    #         self.hints[p] = target
    
    def _find_open_teammate(self, players, ball_carrier):
        """Find nearest teammate not holding the ball for passing option."""
        candidates = [p for p in players if p is not ball_carrier]
        if not candidates:
            return None
        return min(candidates, key=lambda t: (t.pos - ball_carrier.pos).length_squared())
    
    def _get_collision_point(self, ball_pos: V2, target_pos: V2, player_radius: float, ball_radius: float) -> V2:
        """
        Compute the best approach position for a player to hit the ball toward a target.
        Places the player behind the ball along the line to the target.
        """
        direction = (target_pos - ball_pos).normalize()
        approach_distance = player_radius + ball_radius + 5  # a little buffer
        # Position behind the ball
        return ball_pos - direction * approach_distance
    
    def _ball_in_corner(self, ball_pos, pitch_rect, margin=50):
        return (
            (ball_pos.x < pitch_rect.left + margin and (ball_pos.y < pitch_rect.top + margin or ball_pos.y > pitch_rect.bottom - margin))
            or
            (ball_pos.x > pitch_rect.right - margin and (ball_pos.y < pitch_rect.top + margin or ball_pos.y > pitch_rect.bottom - margin))
        )
        
    def update(self, dt: float, pitch_rect: pygame.Rect, ball_pos: V2, ball_vel: V2, players: list) -> None:
        """Update AI targets with smarter shooting, passing, and team roles."""
        self.timer += dt
        if self.timer < self.reaction:
            return
        self.timer = 0.0
        corner_stuck = self._ball_in_corner(ball_pos, pitch_rect)
        # Define goals
        if self.left:
            my_goal = V2(pitch_rect.left + 20, pitch_rect.centery)
            opp_goal = V2(pitch_rect.right - 20, pitch_rect.centery)
        else:
            my_goal = V2(pitch_rect.right - 20, pitch_rect.centery)
            opp_goal = V2(pitch_rect.left + 20, pitch_rect.centery)

        # Sort players by distance to ball
        ordered_players = sorted(players, key=lambda p: (p.pos - ball_pos).length_squared())
        nearest = ordered_players[0] if ordered_players else None
        second_nearest = ordered_players[1] if len(ordered_players) > 1 else None

        for i, p in enumerate(players):
            has_ball = getattr(p, "has_ball", False)
            ball_radius = 10  # approx

            if corner_stuck and p is nearest:
                # 🚀 Nearest AI: don't hug the ball, move it out of the corner
                corner_escape_margin = 200  # how far to pull ball out into open space

                escape_x, escape_y = ball_pos.x, ball_pos.y

                # Move toward opponent's half (never back toward own goal)
                if self.left:  # attacking right
                    escape_x = min(pitch_rect.right - 100, ball_pos.x + corner_escape_margin)
                else:          # attacking left
                    escape_x = max(pitch_rect.left + 100, ball_pos.x - corner_escape_margin)

                # Move toward middle vertically (to avoid hugging top/bottom)
                if ball_pos.y < pitch_rect.centery:
                    escape_y = min(pitch_rect.centery, ball_pos.y + corner_escape_margin)
                else:
                    escape_y = max(pitch_rect.centery, ball_pos.y - corner_escape_margin)

                escape_target = V2(escape_x, escape_y)

                # Instead of going "behind ball", just move directly toward escape point
                target = escape_target

                # ✅ Once out of corner zone → resume normal striker role
                safe_margin = 150
                if (pitch_rect.left + safe_margin < ball_pos.x < pitch_rect.right - safe_margin and
                    pitch_rect.top + safe_margin < ball_pos.y < pitch_rect.bottom - safe_margin):
                    shoot_vec = (opp_goal - ball_pos).normalize()
                    target = ball_pos - shoot_vec * (p.radius + ball_radius + 5)

            elif corner_stuck and p is not nearest:
                # 🧑‍🤝‍🧑 Teammates hold formation away from corner until ball is freed
                safe_x, safe_y = pitch_rect.centerx, pitch_rect.centery
                angle = (i + 1) * (360 / len(players))
                offset = V2(200, 0).rotate(angle)
                target = V2(safe_x, safe_y) + offset


            elif has_ball:
                # Ball carrier: shoot or pass
                teammate = self._find_open_teammate(players, p)
                if teammate and random.random() < self.awareness:
                    target_point = teammate.pos
                else:
                    # Shoot with difficulty-based accuracy
                    if self.difficulty == "Hard":
                        goal_y = opp_goal.y + random.uniform(-20, 20)
                    elif self.difficulty == "Normal":
                        goal_y = opp_goal.y + random.uniform(-50, 50)
                    else:
                        goal_y = opp_goal.y + random.uniform(-100, 100)
                    target_point = V2(opp_goal.x, goal_y)

                # Compute collision approach
                shoot_vec = (target_point - ball_pos).normalize()
                target = ball_pos - shoot_vec * (p.radius + ball_radius + 5)

            elif p is nearest:
                # Striker (nearest without ball): go to collision point behind ball toward goal
                shoot_vec = (opp_goal - ball_pos).normalize()
                target = ball_pos - shoot_vec * (p.radius + ball_radius + 5)

            elif p is second_nearest:
                # Supporter: position for a pass (triangle support)
                direction = (opp_goal - ball_pos).normalize()
                perp = V2(-direction.y, direction.x)  # perpendicular vector
                side = 1 if random.random() > 0.5 else -1
                support_offset = perp * 120 * side
                target = ball_pos + support_offset

            else:
                # Defenders: stay in own half, aligned with ball
                if self.left:
                    base_x = pitch_rect.left + pitch_rect.width * 0.25
                else:
                    base_x = pitch_rect.right - pitch_rect.width * 0.25
                target = V2(base_x, ball_pos.y)

            # Clamp inside pitch
            target.x = max(pitch_rect.left + 20, min(pitch_rect.right - 20, target.x))
            target.y = max(pitch_rect.top + 20, min(pitch_rect.bottom - 20, target.y))

            # Add difficulty error
            if not self._ball_heading_to_goal(ball_pos, ball_vel, my_goal, pitch_rect):
                target += V2(
                    random.uniform(-self.error_range, self.error_range),
                    random.uniform(-self.error_range, self.error_range),
                )

            self.targets[p] = target
            self.hints[p] = target

    def _ball_heading_to_goal(self, ball_pos: V2, ball_vel: V2, my_goal: V2, pitch_rect: pygame.Rect) -> bool:
        """Check if ball is moving toward my half/goal."""
        if self.left and ball_vel.x < 0 and ball_pos.x < pitch_rect.centerx:
            return True
        if not self.left and ball_vel.x > 0 and ball_pos.x > pitch_rect.centerx:
            return True
        return False

    def _predict_intercept(self, ball_pos: V2, ball_vel: V2, my_goal: V2, pitch_rect: pygame.Rect) -> V2 | None:
        """Predict where to intercept ball before it hits our goal line."""
        if abs(ball_vel.x) < 1e-3:
            return None
        t = (my_goal.x - ball_pos.x) / ball_vel.x
        if t < 0:
            return None
        intercept_y = ball_pos.y + ball_vel.y * t
        intercept_y = max(pitch_rect.top + 30, min(pitch_rect.bottom - 30, intercept_y))
        return V2(my_goal.x, intercept_y)

    def advise_direction(self, player) -> V2:
        target = self.targets.get(player)
        if target is None:
            return V2(0, 0)
        d = target - player.pos
        return d.normalize() if d.length_squared() > 0 else V2(0, 0)

    def draw_hint(self, surface: pygame.Surface, debug: bool = False) -> None:
        if not debug:
            return
        for pos in self.hints.values():
            pygame.draw.circle(surface, (100, 180, 255), (int(pos.x), int(pos.y)), 6, 2)
