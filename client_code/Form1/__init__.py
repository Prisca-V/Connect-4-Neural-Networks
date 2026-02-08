from ._anvil_designer import Form1Template
from anvil import *
import anvil.server


class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Dropdown options
    self.game_mode_dropdown.items = ["CNN", "Transformer"]

    # Game state
    self.game_mode = None
    self.board = [[0]*7 for _ in range(6)]  # 6 rows x 7 cols (top row first)
    self.current_player = 1  # 1 = human, 2 = bot

    # Optional: draw initial empty board if you have a render function
    # self.render_board()

  def game_mode_dropdown_change(self, **event_args):
    # Just store the mode for now (DO NOT call server yet)
    self.game_mode = self.game_mode_dropdown.selected_value

  def start_new_game_click(self, **event_args):
    # Require mode selected
    if not self.game_mode_dropdown.selected_value:
      alert("Select a Game Mode first (CNN or Transformer).")
      return

    # Reset state
    self.game_mode = self.game_mode_dropdown.selected_value
    self.board = [[0]*7 for _ in range(6)]
    self.current_player = 1

    # Check uplink is alive
    try:
      anvil.server.call("ping")
    except Exception as e:
      alert(f"Uplink not reachable: {e}")
      return

    # TODO: Clear the UI board here when you have the cell references
    # self.render_board()

    alert("New game started!")