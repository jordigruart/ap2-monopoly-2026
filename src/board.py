from __future__ import annotations

from typing import Iterable, TYPE_CHECKING
import json, random, const, aitools, pickle

from deck import Deck
from draw import draw

if TYPE_CHECKING:
  from tile import Tile, Property, Street
  from player import Player
  from card import Card

class Board:
  _tiles: list[Tile]
  _color_sets: dict[str, set[Street]]

  def __init__(self):
    # We assume the items appear in the files in positional order, just
    # as they do in the files given to us.
    
    # load decks
    self._chance_deck = Deck(self, const.CHANCE_JSON_PATH)
    self._community_deck = Deck(self, const.COMMUNITY_CHEST_JSON_PATH)

    # load tiles
    self._tiles = []
    self._color_sets = {}
    with open(const.TILES_JSON_PATH, encoding = 'UTF-8') as file:
      from tile import build_tile
      for raw_tile in json.load(file):
        tile = build_tile(self, raw_tile)
        self._tiles.append(tile)

        if tile.tile_type() == 'property':
          color = tile.color
          if color not in self._color_sets: self._color_sets[color] = set()
          self._color_sets[tile.color].add(tile)

    # load players
    with open(const.PLAYERS_JSON_PATH, encoding = 'UTF-8') as file:
      from player import build_player
      players = json.load(file)
      self._players = [build_player(self, player, i) for i, player in enumerate(players)]

    self._image_path = const.IMAGE_PATH

    self._turn_accumulator, self._index = 0, 0
    self._is_playing = True

    self._straight_doubles = 0

    self._image_counter = 0

  def players(self) -> list[Player]:
    '''Returns the players in the order in which they play, starting with the
    one whose turn it first ever is. This includes players who are eliminated.'''
    return self._players
  
  def current_player(self) -> Player: return self.players()[self._index]
  def tiles(self) -> list[Tile]: return self._tiles
  def dice(self) -> tuple[int, int]: return self._dice

  def active_players(self) -> int: 
    '''Returns how many players are currently in the game (i.e. not eliminated).'''
    return sum(1 for player in self.players() if not player.is_bankrupt())

  def color_set(self, color: str) -> set[Street]:
    '''Returns the set of streets on the board with the specified color.'''
    return self._color_sets[color]
  
  def jail_position(self) -> int: return 10

  def throw_dice(self) -> None:
    '''Updates dice with two new random valuesd.
    
    Board-drawing: this function draws the board.'''
    self._dice = random.randint(1, 6), random.randint(1, 6)
    print(f'{self.current_player()} rolled {self._dice}')
    self.draw()

  def _handle_doubles(self) -> None:
    '''Updates the amount of straight doubles rolled and sends current player
    to prison if they have rolled three doubles in a row.'''
    self._doubles = self.dice()[0] == self.dice()[1]

    if self._doubles:
      self._straight_doubles += 1
      
      if self._straight_doubles == 3: self.current_player().imprison()

  def draw(self) -> None:
    '''Draws the board and increments the image counter.
    This function should be called whenever the board is updated.'''
    draw(self, self._image_path + f'{self._image_counter:05d}.svg')
    self._image_counter += 1

  def _make_way_for_next_player(self) -> None:
    '''Makes way for next player so that they may play next turn.'''
    self._straight_doubles = 0
    self._index += 1
    self._index %= const.MAX_PLAYERS

  def _prison_routine(self):
    '''Handles turn behavior when the player is in jail.
    
    If the player has a get out of jail free card, they are prompted to use it.
    Otherwise, they are made to roll their dice, and are only freed if they
    roll doubles, which they must then use to move. This double means they may
    play again next turn and counts towards the three doubles that lead to
    imprisonment as well.'''
    current_player = self.current_player()
    assert current_player.is_in_prison()    
    if current_player.get_out_of_jail_free_cards() > 0:
      aitools.prompt_use_goojfc(current_player)
      return
    
    self.throw_dice()
    if self.dice()[0] == self.dice()[1]:
      current_player.free()
      return


  def _play_turn(self):
    current_player = self.current_player()
    if current_player.is_bankrupt():
      self._make_way_for_next_player()
      return

    self._turn_accumulator += 1
    print(f'TURN {self._turn_accumulator}: {current_player}\'s turn')

    if current_player.is_in_prison(): self._prison_routine()
    else: self.throw_dice()

    if not current_player.is_in_prison(): # player may have been freed
      self._handle_doubles()
      current_player.move_forward(sum(self.dice()))
      
      current_tile = self.tiles()[current_player.position()]

      print(f'{current_player} has landed on {current_tile}')
      current_tile.land_on(current_player)

      if current_player.is_bankrupt():
        current_player.eliminate(
          creditor = current_tile.owner() if isinstance(current_tile, Property) else None)
        self._make_way_for_next_player()
        return

    aitools.post_turn_actions(current_player)

    if current_player.is_in_prison():
      current_player.log_a_turn_in_prison()
      if current_player.turns_in_prison() == 3:
        self.draw()
        current_player.free()
    
    if not self._doubles: self._make_way_for_next_player()
    return
  
  def play(self) -> None:
    '''Plays the game until only one player is standing. Progressively
    generates illustrations of the board state for every turn, which are stored
    in ./imgs'''
    lim = 300
    while self._turn_accumulator <= lim and self.active_players() > 1:
      try: self._play_turn()
      except const.EndTurn: self._make_way_for_next_player()

class DebugBoard(Board):
  '''Altered version of the normal board used for testing.
  Takes an iterable of die rolls for an input, instead of using a seed to generate inputs.
  Stops execution when there are no more dice to roll.'''
  def __init__(
    self,
    die_inputs: Iterable[tuple[int, int]],
    cards: Iterable[Card] = []
  ):
    super().__init__()
    self._die_inputs = iter(die_inputs)
    self._cards = iter(cards)
    
    self._image_path = const.DEBUG_IMAGE_PATH
  
  def throw_dice(self) -> None:
    '''Updates dice to next tuple in die inputs and draws board.
    Raises StopIteration if there are no more inputs.'''
    self._dice = next(self._die_inputs)
    self.draw()
  
  def play(self) -> None:
    '''Runs game until die inputs end or a player wins.'''
    try: super().play()
    except StopIteration: print('Die rolls or cards finished. Stopping play')

  def run(self, turns: int) -> None:
    '''Runs game for the specified number of turns.'''
    for _ in range(turns):
      try: self._play_turn()
      except const.EndTurn:
        if not self._doubles: self._make_way_for_next_player()

def save_board(board: Board, pickle_path: str) -> None:
  with open(pickle_path, "wb") as f: pickle.dump(board, f)

def load_board(pickle_path: str) -> Board:
  with open(pickle_path, "rb") as f: return pickle.load(f)