from ._anvil_designer import HomepageTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..LoginPage import LoginPage
from anvil import alert
class Homepage(HomepageTemplate):
  def __init__(self, **properties):
  
    pass

  @handle("Play_game", "click")
  def Play_game_click(self, **event_args):
    open_form('Form1_copy')
    pass

