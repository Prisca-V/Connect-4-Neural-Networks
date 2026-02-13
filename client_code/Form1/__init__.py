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

    # Draw initial empty board
    self.render_board()

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

    # Human move
    r = self.drop_piece(col, 1)
    if r is None:
      alert("That column is full.")
      return

    self.render_board()

    # 🔎 DEBUG: print board being sent to bot
    print("Board being sent to bot:")
    for row in self.board_game:
      print(row)

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

  @handle("outlined_1", "pressed_enter")
  def outlined_1_pressed_enter(self, **event_args):
    pass

  @handle("test_health", "pressed_enter")
  def test_health_pressed_enter(self, **event_args):
    pass

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

