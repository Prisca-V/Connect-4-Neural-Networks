from ._anvil_designer import HomepageTemplate
from anvil import *
import anvil.users
import anvil.server
from ..EntryEdit import EntryEdit
from anvil import alert

class Homepage(HomepageTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    user = anvil.users.get_user()
    if not user:
      anvil.users.login_with_form()
      user = anvil.users.get_user()

    if not user:
      alert("You must sign in to access this page.")
      self.content_panel.visible = False
      return

    self.content_panel.visible = True
    self.refresh_entries()

  def btn_play_click(self, **event_args):
    open_form("GamePage")  # your game form name

  def btn_refresh_click(self, **event_args):
    self.refresh_entries()

  def add_entry_button_click(self, **event_args):
    new_entry = {}
    save_clicked = alert(
      content=EntryEdit(item=new_entry),
      title="Add Entry",
      large=True,
      buttons=[("Save", True), ("Cancel", False)]
    )
    if save_clicked:
      anvil.server.call('add_entry', new_entry)
      self.refresh_entries()

  def refresh_entries(self):
    self.entries_panel.items = anvil.server.call('get_entries')

  def delete_entry(self, entry, **event_args):
    anvil.server.call('delete_entry', entry)
    self.refresh_entries()

  def log_in_click(self, **event_args):
    anvil.users.login_with_form()
    if anvil.users.get_user():
      self.content_panel.visible = True
