import anvil.server
import anvil.http

BOT_API_BASE = "https://REPLACE_WITH_REAL_BASE_URL"
BOT_SHARED_SECRET = "7a-f3b9c1e4d8a2c6f0b5e9d3c7a1f8b4"

def _headers():
  return {
    "Authorization": f"Bearer {BOT_SHARED_SECRET}",
    "Content-Type": "application/json"
  }

@anvil.server.callable
def new_game(difficulty="easy"):
  return anvil.http.request(
    f"{BOT_API_BASE}/new_game",
    method="POST",
    headers=_headers(),
    json={"difficulty": difficulty}
  )

@anvil.server.callable
def make_move(game_id, column):
  return anvil.http.request(
    f"{BOT_API_BASE}/move",
    method="POST",
    headers=_headers(),
    json={"game_id": game_id, "column": int(column)}
  )