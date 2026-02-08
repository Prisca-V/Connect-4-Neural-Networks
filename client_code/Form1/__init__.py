from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.game_mode_dropdown.items = ["CNN", "Transformer"]

    # Any code you write here will run before the form opens.

  @handle("game_mode_dropdown_change", "change")
  def game_mode_dropdown_change_change(self, **event_args):
    self.game_mode = self.game_mode_dropdown.selected_value
    if self.game_mode == "CNN":
      anvil.server.call("run_cnn_model", board_state)
    elif self.game_mode == "Transformer":
      anvil.server.call("run_transformer_model", board_state)
    pass
