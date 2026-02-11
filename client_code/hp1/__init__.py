from ._anvil_designer import hp1Template
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..EntryEdit import EntryEdit
from anvil import alert
class hp1(hp1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    user = anvil.users.get_user()
    if not user:
      anvil.users.login_with_form()
      user = anvil.users.get_user()

    if not user:
      alert("You must sign in to access this page.")
      self.content_panel.visible = False
      return

    # Logged in
    self.content_panel.visible = True
    # Any code you write here will run when the form opens.
  

  def add_entry_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Initialise an empty dictionary to store the user inputs
    new_entry = {}
    # Open an alert displaying the 'EntryEdit' Form
    save_clicked = alert(
      content=EntryEdit(item=new_entry),
      title="Add Entry",
      large=True,
      buttons=[("Save", True), ("Cancel", False)]
    )
    # If the alert returned 'True', the save button was clicked.
    if save_clicked:
      anvil.server.call('add_entry', new_entry)
      self.refresh_entries()
    
  def refresh_entries(self):
     # Load existing entries from the Data Table, 
     # and display them in the RepeatingPanel
     self.entries_panel.items = anvil.server.call('get_entries')

  def delete_entry(self, entry, **event_args):
    # Delete the entry
    anvil.server.call('delete_entry', entry)
    # Refresh entry to remove the deleted entry from the Homepage
    self.refresh_entries()

  @handle("log_in", "click")
  def log_in_click(self, **event_args):
    anvil.users.login_with_form()
    if anvil.users.get_user():
      self.content_panel.visible = True
    pass

<div class="app-shell-bg">
<div class="page-wrap">
<div class="article-card">
<div style="display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; align-items:flex-end;">
         <div>
          <div class="hip-title">Model Report</div>
<div class="body-text">A medium-style writeup of training, results, and recommendations.</div>
</div>

<div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
<anvil-button anvil-name="btn_play" class="btn-primary-cute" text="Play Connect 4"></anvil-button>
<anvil-button anvil-name="log_in" class="btn-cute" text="Sign in"></anvil-button>
</div>
</div>

<div class="divider"></div>

<!-- Content panel you already use in Python -->
<anvil-panel anvil-name="content_panel">
<div class="section-title">Overview</div>
<div class="body-text">
<anvil-rich-text anvil-name="rt_overview"></anvil-rich-text>
</div>

<div class="divider"></div>

<div class="section-title">Model Training</div>
<div class="body-text">
<anvil-rich-text anvil-name="rt_training"></anvil-rich-text>
        </div>

        <div style="margin-top:14px;">
          <div class="section-title" style="margin-top:0;">Training Images</div>
          <div class="body-text" style="margin-bottom:10px;">Drop figures/screenshots here.</div>

          <!-- Image slots -->
          <div style="display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap:12px;">
            <anvil-image anvil-name="img_train_1" style="width:100%; border-radius:14px; border:1px solid rgba(0,0,0,0.12); box-shadow: var(--shadow-soft);"></anvil-image>
            <anvil-image anvil-name="img_train_2" style="width:100%; border-radius:14px; border:1px solid rgba(0,0,0,0.12); box-shadow: var(--shadow-soft);"></anvil-image>
          </div>
        </div>

        <div class="divider"></div>

        <div class="section-title">Entries</div>
        <div class="body-text" style="margin-bottom:10px;">
          Add notes/observations here.
        </div>

        <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-bottom:12px;">
          <anvil-button anvil-name="add_entry_button" class="btn-cute" text="Add Entry"></anvil-button>
          <anvil-button anvil-name="btn_refresh" class="btn-cute" text="Refresh"></anvil-button>
        </div>

        <anvil-repeating-panel anvil-name="entries_panel"></anvil-repeating-panel>
      </anvil-panel>
    </div>
  </div>
</div>