from ._anvil_designer import LoginPageTemplate
from anvil import *
import anvil.server
import anvil.users


class LoginPage(LoginPageTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def login_click(self, **event_args):
    print("LOGIN BUTTON CLICKED")  # this WILL show in Running App Console

    email = (self.email_box.text or "").strip()
    password = self.password_box.text or ""

    try:
      anvil.server.call('login_email_password', email, password)
      open_form('Homepage')
    except Exception as e:
      alert("Invalid email or password. Please try again.")
      print("Login error:", e)