from __future__ import annotations

from typing import Iterable, Iterator, TYPE_CHECKING
import json, random, const, aitools, pickle
from draw import draw

from deck import Deck, DebugDeck
from player import build_player
from tile import Street, build_tile

if TYPE_CHECKING:
  from tile import Tile
  from player import Player

class Board:
  '''Class that simulates a game board. Initialization argument image_path is
  the directory (with respect to the root) where generated images are stored.'''
  _tiles: list[Tile]; _players: list[Player]; _chance_deck: Deck; _community_deck: Deck
  _color_sets: dict[str, set[Street]]
  _dice: tuple[int, int]; _doubles: bool; _straight_doubles: int
  _turn_index: int; _turn_accumulator: int
  _image_path: str;  _image_counter: int
  
  def __init__(self, image_path: str = const.IMAGE_PATH):
    # We assume the items appear in the files in positional order, just
    # as they do in the files given to us.
    
    # load decks
    self._chance_deck = Deck(self, const.CHANCE_JSON_PATH)
    self._community_deck = Deck(self, const.COMMUNITY_CHEST_JSON_PATH)

    # load tiles
    self._tiles = []
    self._color_sets = {}
    with open(const.TILES_JSON_PATH, encoding = 'UTF-8') as file:
      for raw_tile in json.load(file):
        tile = build_tile(self, **raw_tile)
        self._tiles.append(tile)

    # load tiles into color sets
    self._color_sets = {color: set[Street]() for color in const.COLORS}
    for tile in self._tiles:
      if isinstance(tile, Street): self._color_sets[tile.color].add(tile)

    # load players
    with open(const.PLAYERS_JSON_PATH, encoding = 'UTF-8') as file:
      players = json.load(file)
      self._players = [build_player(self, i, **player) for i, player in enumerate(players)]

    self._image_path = image_path
    self._image_counter = 0
    self._turn_accumulator, self._turn_index = 0, 0
    self._straight_doubles = 0

  def players(self) -> list[Player]:
    '''Returns the players in the order in which they play, starting with the
    one whose turn it first ever is. This includes players who are eliminated.'''
    return self._players
  
  def current_player(self) -> Player:
    '''Returns the player whose turn it currently is.'''
    return self.players()[self._turn_index]
  
  def tiles(self) -> list[Tile]: 
    '''Returns the tiles in the order in which they appear on the board,
    starting from GO at index 0.'''
    return self._tiles
  
  def dice(self) -> tuple[int, int]:
    '''Returns the dice last rolled.'''
    return self._dice

  def chance_deck(self) -> Deck:
    '''Returns the chance deck.'''
    return self._chance_deck
  
  def community_deck(self) -> Deck:
    '''Returns the community deck.'''
    return self._community_deck

  def active_players(self) -> list[Player]: 
    '''Returns list of players currently in the game (i.e. not eliminated).'''
    return list(filter(lambda player: not player.is_eliminated(), self.players()))
  
  def color_set(self, color: str) -> set[Street]:
    '''Returns the set of streets on the board with the specified color.'''
    return self._color_sets[color]
  
  def jail_position(self) -> int:
    '''Returns the position where the jail tile is.'''
    return 10

  def throw_dice(self) -> None:
    '''Updates dice with two new random values.
    
    Board-drawing: this function draws the board.'''
    self._dice = random.randint(1, 6), random.randint(1, 6)
    print(f'{self.current_player()} has rolled {self._dice}')
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
    self._turn_index += 1
    self._turn_index %= len(self.players())

  def _prison_routine(self, player: Player):
    '''Handles turn behavior when the player is in jail.
    
    If the player has a get out of jail free card, they are prompted to use it.
    Otherwise, they are made to roll their dice, and are only freed if they
    roll doubles, which they must then use to move.'''
    assert player.is_in_prison()    
    if player.get_out_of_jail_free_cards > 0:
      aitools.prompt_use_goojfc(player)
      self.throw_dice()
      return
    
    self.throw_dice()
    if self.dice()[0] == self.dice()[1]:
      player.free()

  def _free_routine(self, player: Player):
    '''Handles turn behavior after player rolls dice and is free:
    moves forward and runs tile logic.'''
    assert not player.is_in_prison()
    player.move_forward(sum(self.dice()))
    
    current_tile = player.current_tile()
    current_tile.land_on(player)
  
  def _play_turn(self):
    current_player = self.current_player()
    if current_player.is_eliminated():
      self._make_way_for_next_player()
      return
    
    else:
      self._turn_accumulator += 1
      print(f'TURN {self._turn_accumulator}: {current_player}\'s turn')
    
    if current_player.is_in_prison(): self._prison_routine(current_player)
    else: self.throw_dice()

    self._handle_doubles()
    if not current_player.is_in_prison(): self._free_routine(current_player)
    aitools.post_turn_actions(current_player)
    current_player.update_turns_in_prison()
    if not self._doubles: self._make_way_for_next_player()
  
  def play(self) -> bool:
    '''Plays the game until only one player is standing or until 400 turns have
    been played. Progressively generates illustrations of the board state for
    every turn, which are stored in ./imgs by default.
    
    Returns True if the game has ended by normal means, and False if it reached
    the 400 turn cap.
    '''
    lim = 400
    while self._turn_accumulator <= lim and len(self.active_players()) > 1:
      try: self._play_turn()
      except const.EndTurn: self._make_way_for_next_player()
    
    return len(self.active_players()) == 1

class DebugBoard(Board):
  '''Altered version of the normal board used for testing.
  Takes a list of die rolls for an input, instead of using a seed to generate inputs.
  Also takes a list of card IDs that will be drawn sequencially when players
  land on card tiles. Both decks exhaust the same iterator.
  Stops execution when there are no more dicee to roll or when cards run out.'''
  _die_inputs: Iterator[tuple[int, int]]
  def __init__(
    self,
    die_inputs: Iterable[tuple[int, int]],
    cards: Iterable[int] = []
  ):
    super().__init__(image_path = const.DEBUG_IMAGE_PATH)
    self._die_inputs = iter(die_inputs)
    card_ids = iter(cards)
    self._chance_deck = DebugDeck(card_ids, board = self, path = const.CHANCE_JSON_PATH)
    self._community_deck = DebugDeck(card_ids, board = self, path = const.COMMUNITY_CHEST_JSON_PATH)
      
  def throw_dice(self) -> None:
    '''Updates dice to next tuple in die inputs and draws board.
    Raises StopIteration if there are no more inputs.'''
    self._dice = next(self._die_inputs)
    self.draw()
  
  def play(self) -> bool:
    '''Runs game until die inputs end or a player wins.'''
    try: super().play()
    except StopIteration: print('Die rolls or cards finished. Stopping play')

    return True

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