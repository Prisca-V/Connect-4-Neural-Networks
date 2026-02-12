import anvil.server
import anvil.users

@anvil.server.callable
def login_email_password(email, password):
  return anvil.users.login_with_email(email, password)
def start_game(difficulty="easy"):
  # Calls the uplink worker function
  return anvil.server.call("new_game", difficulty)

@anvil.server.callable
def play_move(game_id, column):
  return anvil.server.call("move", game_id, column)  