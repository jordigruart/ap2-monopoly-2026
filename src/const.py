GO_SALARY = 200
START_MONEY = 1500
MAX_PLAYERS = 4

TILES_JSON_PATH = "src/data/tiles.json"
CHANCE_JSON_PATH = "src/data/chance.json"
COMMUNITY_CHEST_JSON_PATH = "src/data/community-chest.json"
PLAYERS_JSON_PATH = "src/data/players.json"

IMAGE_PATH = 'imgs/'
DEBUG_IMAGE_PATH = 'debug/imgs/'

SEED = 1383 # 22

MORTGAGE_INTEREST_RATE = 1.1 # rate applied to mortgage price when removed
SPENDING_THRESHOLD = 40
# A player will buy until some transaction puts them below this threshold and
# sell until they are above or at the threshold.

COLORS = [
  'brown', 'light_blue', 'pink', 'orange',
  'red', 'yellow', 'green', 'dark_blue'
  ] # sorted from least to most expensive

class EndTurn(Exception):
  '''Exception that, when raised, ends the current turn prematurely.
  Used when a player is imprisoned or eliminated.'''