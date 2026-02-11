from ._anvil_designer import LoginPageTemplate
from anvil import *
import anvil.users

class LoginPage(LoginPageTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # If already logged in, go straight home
    if anvil.users.get_user():
      open_form("Homepage")

  def btn_login_click(self, **event_args):
    anvil.users.login_with_form()
    if anvil.users.get_user():
      open_form("Homepage")

  def btn_go_home_click(self, **event_args):
    open_form("Homepage")
