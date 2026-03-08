GO_SALARY = 200
START_MONEY = 1500
MAX_PLAYERS = 4

TILES_JSON_PATH = "src/data/tiles.json"
CHANCE_JSON_PATH = "src/data/chance.json"
COMMUNITY_CHEST_JSON_PATH = "src/data/community-chest.json"
PLAYERS_JSON_PATH = "src/data/players.json"

MORTGAGE_INTEREST_RATE = 1.1
LOWER_SPENDING_THRESHOLD = 100 # if a player's balance is under this threshold,
# they will attempt to sell/mortgage until they're above it

UPPER_SPENDING_THRESHOLD = 500 # if a player's balance is under this threshold,
# they will not buy anything

COLORS = [
  'brown', 'light_blue', 'pink', 'orange',
  'red', 'yellow', 'green', 'dark_blue'
  ] # sorted from least to most expensive

class EndTurn(Exception):
  '''Exception that, when raised, ends the current turn.
  Whether to make way for the next player is only handled when this exception
  is called.'''