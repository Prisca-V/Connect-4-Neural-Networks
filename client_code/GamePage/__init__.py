from ._anvil_designer import GamePageTemplate
from anvil import *
import anvil.server


class GamePage(GamePageTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Dropdown options
    self.game_mode = "cnn"

    # Build 6x7 cell grid
    self.cells = [[getattr(self, f"cell_{r}_{c}") for c in range(7)] for r in range(6)]

    # Game state
    self.game_mode = None
    self.board_game = [[0]*7 for _ in range(6)]
    self.current_player = 1

    self.render_board()


  # =========================
  # Navigation
  # =========================

  def btn_back_home_click(self, **event_args):
    open_form("Homepage")


  # =========================
  # Controls
  # =========================

  def game_mode_dropdown_change(self, **event_args):
    self.game_mode = self.game_mode_dropdown.selected_value


  def start_new_game_click(self, **event_args):
    if not self.game_mode_dropdown.selected_value:
      alert("Select a Game Mode first.")
      return

    self.game_mode = self.game_mode_dropdown.selected_value

    try:
      result = anvil.server.call("start_new_game")
      self.board_game = result["board"]
      self.current_player = result.get("current_player", 1)
    except Exception as e:
      alert(f"start_new_game failed:\n{e}")
      return

    self.render_board()


  def test_health_click(self, **event_args):
    try:
      result = anvil.server.call("ping")
      alert(f"Backend healthy\nTimestamp: {result.get('ts')}")
    except Exception as e:
      alert(f"Backend NOT reachable:\n{e}")


  # =========================
  # Column Buttons
  # =========================

  def button_1_click(self, **event_args): self.play_column(0)
  def button_2_click(self, **event_args): self.play_column(1)
  def button_3_click(self, **event_args): self.play_column(2)
  def button_4_click(self, **event_args): self.play_column(3)
  def button_5_click(self, **event_args): self.play_column(4)
  def button_6_click(self, **event_args): self.play_column(5)
  def button_7_click(self, **event_args): self.play_column(6)


  # =========================
  # Board Logic
  # =========================

  def render_board(self):
    for r in range(6):
      for c in range(7):
        v = self.board_game[r][c]
        cell = self.cells[r][c]

        if v == 0:
          cell.style["background"] = "#ffffff"
        elif v == 1:
          cell.style["background"] = "#ff4d4d"
        elif v == 2:
          cell.style["background"] = "#ffd24d"


  def drop_piece(self, col, player):
    for r in range(5, -1, -1):
      if self.board_game[r][col] == 0:
        self.board_game[r][col] = player
        return r
    return None


  def play_column(self, col):
    if not self.game_mode:
      alert("Select a Game Mode first.")
      return

    # Human move
    r = self.drop_piece(col, 1)
    if r is None:
      alert("Column full.")
      return

    self.render_board()

    # Bot move via Docker/Uplink
    try:
      result = anvil.server.call(
        "get_bot_move",
        self.board_game,
        self.game_mode.lower()
      )
      bot_col = result["column"]
    except Exception as e:
      alert(f"Bot call failed:\n{e}")
      return

    self.drop_piece(bot_col, 2)
    self.render_board()
