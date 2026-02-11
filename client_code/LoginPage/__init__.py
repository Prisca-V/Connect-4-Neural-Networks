from ._anvil_designer import LoginPageTemplate
from anvil import *
import anvil.users

class LoginPage(LoginPageTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    if anvil.users.get_user():
      open_form("Homepage")

  def btn_login_click(self, **event_args):
    email = (self.tb_email.text or "").strip()
    password = self.tb_password.text or ""

    if not email or not password:
      alert("Enter your email and password.")
      return

    try:
      anvil.users.login_with_email(email, password)
    except Exception:
      alert("Login failed. Check your email/password and try again.")
      return

    open_form("Homepage")