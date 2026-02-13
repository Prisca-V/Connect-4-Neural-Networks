from ._anvil_designer import Form1Template
from anvil import *
import anvil.users
import anvil.server
import re


class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Dropdown options
    self.game_mode_dropdown.items = ["CNN", "Transformer"]

    # Map outlined_card_1..outlined_card_42 into a 6x7 grid
    self.init_board_cells()

    # Game state (DO NOT name this 'board')
    self.game_mode = None
    self.board_game = [[0]*7 for _ in range(6)]  # 6 rows x 7 cols
    self.current_player = 1  # 1 = human, 2 = bot
    self.game_over = False   # ✅ IMPORTANT: define this at startup

    # Hide overlay + messages initially
    self.result_overlay.visible = False
    self.win_msg.visible = False
    self.loser_msg.visible = False

    self._set_column_buttons_enabled(True)

    # Draw initial empty board
    self.render_board()

  def _set_column_buttons_enabled(self, enabled: bool):
    for i in range(1, 8):
      getattr(self, f"button_{i}").enabled = enabled

  # =========================
  # UI EVENTS
  # =========================

  @handle("game_mode_dropdown", "change")
  def game_mode_dropdown_change(self, **event_args):
    self.game_mode = self.game_mode_dropdown.selected_value

  @handle("start_new_game", "click")
  def start_new_game_click(self, **event_args):
    if not self.game_mode_dropdown.selected_value:
      alert("Select a Game Mode first (CNN or Transformer).")
      return

    self.game_mode = self.game_mode_dropdown.selected_value

    try:
      result = anvil.server.call("start_new_game")
      self.board_game = result["board"]
      self.current_player = result.get("current_player", 1)
    except Exception as e:
      alert(f"start_new_game() failed:\n{e}")
      return

    # ✅ reset endgame UI/state
    self.game_over = False
    self.hide_result_overlay()
    self._set_column_buttons_enabled(True)

    self.render_board()
    alert("New game started!")

  @handle("button_1", "click")
  def button_1_click(self, **event_args):
    self.play_column(0)

  @handle("button_2", "click")
  def button_2_click(self, **event_args):
    self.play_column(1)

  @handle("button_3", "click")
  def button_3_click(self, **event_args):
    self.play_column(2)

  @handle("button_4", "click")
  def button_4_click(self, **event_args):
    self.play_column(3)

  @handle("button_5", "click")
  def button_5_click(self, **event_args):
    self.play_column(4)

  @handle("button_6", "click")
  def button_6_click(self, **event_args):
    self.play_column(5)

  @handle("button_7", "click")
  def button_7_click(self, **event_args):
    self.play_column(6)

  # =========================
  # BOARD MAPPING + RENDERING
  # =========================

  def _collect_outlined_cards(self):
    cards = []
    for name, comp in self.__dict__.items():
      if name.startswith("outlined_card_"):
        m = re.match(r"outlined_card_(\d+)$", name)
        if m:
          cards.append((int(m.group(1)), comp))

    cards.sort(key=lambda x: x[0])
    return [c for _, c in cards]

  def init_board_cells(self):
    cards = self._collect_outlined_cards()

    if len(cards) != 42:
      raise Exception(f"Expected 42 outlined cards (6x7), found {len(cards)}")

    self.cells = []
    idx = 0
    for r in range(6):
      row = []
      for c in range(7):
        row.append(cards[idx])
        idx += 1
      self.cells.append(row)

  def render_board(self):
    for r in range(6):
      for c in range(7):
        cell = self.cells[r][c]
        v = self.board_game[r][c]

        if v == 0:
          cell.background = "white"
        elif v == 1:
          cell.background = "#ff4d4d"   # human
        elif v == 2:
          cell.background = "#ffd24d"   # bot

  # =========================
  # GAMEPLAY
  # =========================

  def drop_piece(self, col, player):
    for r in range(5, -1, -1):
      if self.board_game[r][col] == 0:
        self.board_game[r][col] = player
        return r
    return None

  def play_column(self, col):
    if not self.game_mode:
      alert("Select a Game Mode first (CNN or Transformer).")
      return

    if self.game_over:
      return

    # Human move
    r = self.drop_piece(col, 1)
    if r is None:
      alert("That column is full.")
      return

    self.render_board()

    # Check if human won
    if self.check_winner(1):
      self.show_result_overlay(True, "GAME OVER! YOU WON!")
      return

    # Draw
    if self.board_full():
      self.show_result_overlay(False, "DRAW! No more moves.")
      return

    # Bot move (Docker uplink)
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

    # Check if bot won
    if self.check_winner(2):
      self.show_result_overlay(False, "GAME OVER! YOU LOST!")
      return

    # Draw
    if self.board_full():
      self.show_result_overlay(False, "DRAW! No more moves.")
      return

  # =========================
  # HEALTH CHECK
  # =========================

  @handle("test_health", "click")
  def test_health_click(self, **event_args):
    try:
      result = anvil.server.call("ping")
      alert(
        f"✅ Backend healthy\n\n"
        f"Status: {result.get('status', 'ok')}\n"
        f"Timestamp: {result.get('ts')}"
      )
    except Exception as e:
      alert(f"❌ Backend NOT reachable:\n{e}")

  # =========================
  # WIN / DRAW CHECKS
  # =========================

  def check_winner(self, player: int) -> bool:
    B = self.board_game
    ROWS, COLS = 6, 7

    # horizontal
    for r in range(ROWS):
      for c in range(COLS - 3):
        if all(B[r][c+i] == player for i in range(4)):
          return True

    # vertical
    for r in range(ROWS - 3):
      for c in range(COLS):
        if all(B[r+i][c] == player for i in range(4)):
          return True

    # diag down-right
    for r in range(ROWS - 3):
      for c in range(COLS - 3):
        if all(B[r+i][c+i] == player for i in range(4)):
          return True

    # diag up-right
    for r in range(3, ROWS):
      for c in range(COLS - 3):
        if all(B[r-i][c+i] == player for i in range(4)):
          return True

    return False

  def board_full(self) -> bool:
    return all(self.board_game[0][c] != 0 for c in range(7))

  # =========================
  # OVERLAY + PLAY AGAIN
  # =========================

  def show_result_overlay(self, won: bool, text: str):
    self.game_over = True
    self._set_column_buttons_enabled(False)

    self.result_overlay.visible = True
    self.win_msg.visible = won
    self.loser_msg.visible = not won

    if won:
      self.win_msg.text = text
      self.loser_msg.text = ""
    else:
      self.loser_msg.text = text
      self.win_msg.text = ""

  def hide_result_overlay(self):
    self.result_overlay.visible = False
    self.win_msg.visible = False
    self.loser_msg.visible = False
    self.win_msg.text = ""
    self.loser_msg.text = ""

  @handle("play_again_button", "click")
  def play_again_button_click(self, **event_args):
    # Just call the same start function (it resets everything)
    self.start_new_game_click()

  @handle("close_overlay_btn", "click")
  def close_overlay_btn_click(self, **event_args):
    self.hide_result_overlay()

  @handle("back_Homepage", "click")
  def back_Homepage_click(self, **event_args):
    open_form('Homepage')
    pass

 
