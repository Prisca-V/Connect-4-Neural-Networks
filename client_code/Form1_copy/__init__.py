from ._anvil_designer import Form1_copyTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server
import re


class Form1_copy(Form1_copyTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Dropdown options
    self.game_mode_dropdown.items = ["CNN", "Transformer"]

    # Map outlined_card_1..outlined_card_42 into a 6x7 grid
    self.init_board_cells()
    # self._wire_board_clicks()

    # Game state
    self.game_mode = None
    self.board_game = [[0] * 7 for _ in range(6)]  # 6 rows x 7 cols
    self.game_over = False

    # Default = human starts; only True when bot_first is clicked
    self.bot_starts = False

    # Prevent clicks during bot move
    self.bot_turn_in_progress = False

    # Hide overlay + messages initially
    self.result_overlay.visible = False
    self.win_msg.visible = False
    self.loser_msg.visible = False

    # Enable column buttons
    self._set_column_buttons_enabled(True)

    # Draw initial empty board
    self.render_board()

  # =========================
  # HELPERS
  # =========================

  # def _wire_board_clicks(self):
  #   for r in range(6):
  #     for c in range(7):
  #       cell = self.cells[r][c]          # this is a ColumnPanel
  #       cell.set_event_handler('mouse_down', self._make_cell_handler(c))

  # def _make_cell_handler(self, col):
  #   def handler(**event_args):
  #     self.play_column(col)
  #   return handler

  def _set_column_buttons_enabled(self, enabled: bool):
    for i in range(1, 8):
      getattr(self, f"button_{i}").enabled = enabled

  def _require_mode(self) -> bool:
    if not self.game_mode_dropdown.selected_value:
      alert("Select a Game Mode first (CNN or Transformer).")
      return False
    self.game_mode = self.game_mode_dropdown.selected_value
    return True

  # =========================
  # UI EVENTS
  # =========================

  @handle("game_mode_dropdown", "change")
  def game_mode_dropdown_change(self, **event_args):
    self.game_mode = self.game_mode_dropdown.selected_value

  @handle("start_new_game", "click")
  def start_new_game_click(self, **event_args):
    # Default behavior: clear/reset board; human starts unless bot_starts flag is set
    self._start_new_game()

  @handle("bot_first", "click")
  def bot_first_click(self, **event_args):
    # User chooses bot starts first for this round
    self.bot_starts = True
    self._start_new_game()

  # Column buttons (human move)
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
  # GAME START / RESET
  # =========================

  def _start_new_game(self):
    if not self._require_mode():
      return

    try:
      result = anvil.server.call("start_new_game")
      # If your server returns a blank board, great:
      self.board_game = result.get("board", [[0] * 7 for _ in range(6)])
    except Exception as e:
      alert(f"start_new_game() failed:\n{e}")
      return

    # Reset endgame UI/state
    self.game_over = False
    self.hide_result_overlay()

    # Render cleared board
    self.render_board()

    # If bot starts, make exactly ONE bot move immediately
    if self.bot_starts:
      self.bot_turn_in_progress = True
      self._set_column_buttons_enabled(False)

      self.bot_move_once()

      self._set_column_buttons_enabled(True)
      self.bot_turn_in_progress = False

    # Always reset to default (human starts next time)
    self.bot_starts = False

    # Optional: remove this alert if it annoys you
    # alert("New game started!")

  # =========================
  # BOT MOVE (ONE TURN ONLY)
  # =========================

  def bot_move_once(self):
    """Make exactly one bot move. No loops, no extra turns."""
    if self.game_over:
      return

    if not self.game_mode:
      return

    try:
      result = anvil.server.call(
        "get_bot_move", self.board_game, self.game_mode.lower()
      )
      bot_col = result["column"]
    except Exception as e:
      alert(f"Bot call failed:\n{e}")
      return

    if bot_col is None:
      alert("Bot did not return a column.")
      return

    placed_row = self.drop_piece(bot_col, 2)
    if placed_row is None:
      alert("Bot chose a full column.")
      return

    self.render_board()

    # Bot win?
    if self.check_winner(2):
      self.show_result_overlay(False, "GAME OVER! YOU LOST!")
      return

    # Draw?
    if self.board_full():
      self.show_result_overlay(False, "DRAW! No more moves.")
      return

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
          cell.background = "#ff4d4d"  # human
        elif v == 2:
          cell.background = "#ffd24d"  # bot

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
    if not self._require_mode():
      return

    if self.game_over:
      return

    if self.bot_turn_in_progress:
      return

    # Human move
    r = self.drop_piece(col, 1)
    if r is None:
      alert("That column is full.")
      return

    self.render_board()

    # Human win?
    if self.check_winner(1):
      self.show_result_overlay(True, "GAME OVER! YOU WON!")
      return

    # Draw?
    if self.board_full():
      self.show_result_overlay(False, "DRAW! No more moves.")
      return

    # Bot move (exactly one)
    self.bot_turn_in_progress = True
    self._set_column_buttons_enabled(False)

    self.bot_move_once()

    self._set_column_buttons_enabled(True)
    self.bot_turn_in_progress = False

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
        if all(B[r][c + i] == player for i in range(4)):
          return True

    # vertical
    for r in range(ROWS - 3):
      for c in range(COLS):
        if all(B[r + i][c] == player for i in range(4)):
          return True

    # diag down-right
    for r in range(ROWS - 3):
      for c in range(COLS - 3):
        if all(B[r + i][c + i] == player for i in range(4)):
          return True

    # diag up-right
    for r in range(3, ROWS):
      for c in range(COLS - 3):
        if all(B[r - i][c + i] == player for i in range(4)):
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
    self._start_new_game()

  @handle("close_overlay_btn", "click")
  def close_overlay_btn_click(self, **event_args):
    self.hide_result_overlay()
    self._set_column_buttons_enabled(True)
    self.game_over = False

  @handle("back_Homepage", "click")
  def back_Homepage_click(self, **event_args):
    open_form("Homepage")
