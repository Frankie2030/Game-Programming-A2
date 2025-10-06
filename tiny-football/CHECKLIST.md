# DREAM LEAGUE SOCCER 2030 – Checklist

## ✅ Platform & Tech

* [ ] Add **run instructions** in `README.md` (how to launch, dependencies, OS notes).

---

## 🎮 Player Control

* [ ] **Player 1** visible and controllable
* [ ] **Player 2** visible and controllable
* [ ] Support controlling a **group of players** (multiplayer/AI/stationary/extra avatars).
* [ ] Players move smoothly and respect playfield bounds.
* **Rubric Goal**: Full credit if both players/groups are visible, move smoothly, and stay in bounds.

#### Bug: 
- (1) Speed of players a little bit slow? Can it be customized with the minimum speed still satisfies players? 
  - Done. 
  - Change the max speed of the user can reach in the config file, player.speed 
  - On the starting screen, we can change the ACCELERATION of the user --> this would help the player to faster reach the high speed

- (2) Why players in game are not allow to go to the other fields ?
  - Done: "Function not bug :v"
  - Now in the multiplayer mode, if the number player each team is one, allow cross other fields for solo BUT if member in team > 1 we do not allow that for FAIRNESS

- (3) What is the red dot when control players for?
  - Done: in general it just debug modes
  - When click B to open the debug mode, we would see that for example the ball is moving from left to right, then a small dot would indicates the position of the ball that it would move to (if has enough speed + accelerate)


---

## ⌨️ Keyboard Input & Activation (3 pts)

* [ ] **WASD keys** move one player or selected group (2 pts).
* [ ] **Arrow keys** move one player or selected group (2 pts).
* [ ] **Activation/selection** of specific player or group (e.g., keys 1/2/3, Tab cycle, or mouse click) (1 pt).
* [ ] Show a **clear visual indicator** when a player/group is activated.
* **Rubric Goal**: Full credit if both key sets are reliable and activation is obvious. Partial if only one key set works or activation unclear.

#### Bug:
- (4) The feature change player not as expected: why click 1 2 change both side at a time? Tab only work for left side? -> can it work as each side has section to change player (left using 1 2 3 ..., right using 6 7 8 ...)

  - Done 
  - Left player uses ASWD to play, TAB to switch circular, and 1 2 3 4 5 to choose specific player 
  - Right player uses top-down-left-right button to play, K to switch circular and 6 7 8 9 0 to choose specific player

  - Le said that this not fix yet (27/06)
---

## ⚽ Collision & Physics

* [ ] Rectangular playfield with **4 screen edges (walls)**.
* [ ] One ball with **velocity** and collision behavior.
* [ ] Ball–wall collision implemented (1 pt).
* [ ] Ball–wall reflection correct (angle in ≈ angle out, speed roughly preserved) (1 pt).
* [ ] Ball–object (player) collision implemented (1 pt).
* **Rubric Goal**: Collisions should feel believable & consistent. Avoid sticking, tunneling, or wrong reflections.

---

## 🏆 Scoring & Displaying

* [ ] Display **score or counts** (goals, hits, misses).
* [ ] Score updates correctly when events happen.
* [ ] HUD remains **clear and legible** throughout gameplay.
- The scoring board is not impressive
- Why enter ESC then it closes the game? Why not go back to the menu?

#### Bug:

- (5) The windows of the game is not resizable
  - Done 
  - CLM ditconme cai lone nay fix kho vl ton nhieu prompt xong doc lai loi con c

- (6) Not showing number of the current controlling player (for easier and faster choosing other player in the team)
  - Done
  - Now each player would has the name on their head, and the highlighted circle around them to indicate the current controlled players 


- (7) The goal is not well detected (i mean the rectangle which indicates the position if the ball moves to and mark as A GOAL is not well designed)
  - Done
  - Manually fix in the config file: field.goal_width and field.goal_depth

---

## 👥 Two-Player & AI Play

* [ ] Two humans can play at the same time:

  * Player 1 → **WASD**
  * Player 2 → **Arrow keys**
* [ ] Inputs **do not interfere** with each other.
* **Rubric Goal**: Full credit if both players control independently. Partial if both key sets move the same player or mappings conflict.

#### Bugs (NOT DO YET):

- (8) AI đang là GK thôi, mình cần là AI điều khiển 1 team
- (9) Đang chưa có chỉnh độ khó cho AI (điểm cộng) - AI cần nhấp nhả tuỳ mức

---

## 🌟 Extra Credit (Optional)

* [ ] **External force/field** affecting ball trajectory (+0.5 to +1.0).

  * [ ] Force field is **visible**.
  * [ ] Clearly **documented**.
  * [ ] Consistently alters ball trajectory.
* [ ] **Player vs Computer (AI)** (+1.0 to +2.0).

  * [ ] Basic AI tracking/defense (+1.0).
  * [ ] Anticipation/prediction of ball path (+2.0).
  * [ ] Includes difficulty levels/cooldowns for fairness.
  * [ ] Avoids obvious exploits.
* [ ] **Polish/Creativity/Game feel** → potential discretionary credit.
