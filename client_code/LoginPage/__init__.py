from ._anvil_designer import LoginPageTemplate
from anvil import *
import anvil.server
import anvil.users


class LoginPage(LoginPageTemplate):

  def login_click(self, **event_args):
    email = self.get_dom_node().querySelector("#login_email").value.strip()
    password = self.get_dom_node().querySelector("#login_password").value

    err = self.get_dom_node().querySelector("#login_error")
    if err:
      err.style.display = "none"

    try:
      anvil.server.call('login_email_password', email, password)
      open_form('Homepage')
    except Exception:
      if err:
        err.style.display = "block"
      else:
        alert("Invalid email or password. Please try again.")