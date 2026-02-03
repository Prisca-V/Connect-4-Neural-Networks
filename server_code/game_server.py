import anvil.server

@anvil.server.callable
def start_game(difficulty="easy"):
  # Calls the uplink worker function
  return anvil.server.call("new_game", difficulty)

@anvil.server.callable
def play_move(game_id, column):
  return anvil.server.call("move", game_id, column)