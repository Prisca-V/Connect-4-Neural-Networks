import anvil.server
import anvil.users

@anvil.server.callable
def login_email_password(email, password):
  return anvil.users.login_with_email(email, password)