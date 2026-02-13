from ._anvil_designer import LoginPageTemplate
from anvil import *
import anvil.users

class LoginPage(LoginPageTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # create error label
    self.error_lbl = Label(
      text="",
      visible=False,
      foreground="red",
      align="center"
    )
    self.add_component(self.error_lbl)

  def show_error(self, msg):
    self.error_lbl.text = msg
    self.error_lbl.visible = True

  def clear_error(self):
    self.error_lbl.visible = False
    self.error_lbl.text = ""

  @handle("login_btn", "click")
  def login_btn_click(self, **event_args):
    self.clear_error()

    email = (self.Email.text or "").strip()
    password = self.password.text or ""

    if not email or not password:
      self.show_error("Please enter both email and password.")
      return

    try:
      # attempt login
      user = anvil.users.login_with_email(email, password)

      if user:
        open_form("Homepage")   # change if your home form name differs

    except anvil.users.AuthenticationFailed:
      # covers wrong email OR wrong password
      self.show_error("Incorrect email or password.")

    except Exception as e:
      self.show_error(f"Login error: {e}")
