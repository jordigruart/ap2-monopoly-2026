from __future__ import annotations

from typing import Iterable

import pickle, json
from player import Player, build_player
from tile import Tile, Street, build_tile
from draw import draw
from deck import Deck
from card import Card

import random, const

class Board:
  _tiles: list[Tile]
  _colors: dict[str, set[Street]]

  def __init__(self):
    # We assume the items appear in the files in positional order, just
    # as they do in the files given to us.
    
    # load tiles
    self._tiles = list[Tile]()
    self._colors = dict[str, set[Street]]()
    with open(const.TILES_JSON_PATH, encoding = 'UTF-8') as file:
      for raw_tile in json.load(file):
        tile = build_tile(self, raw_tile)
        self._tiles.append(tile)

        if tile.tile_type() == 'property':
          assert isinstance(tile, Street)
  
          if tile.color not in self._colors: self._colors[tile.color] = set[Street]()
          self._colors[tile.color].add(tile)

    # load decks
    self._chance_deck = Deck(const.CHANCE_JSON_PATH)
    self._community_deck = Deck(const.COMMUNITY_CHEST_JSON_PATH)

    # load players
    with open(const.PLAYERS_JSON_PATH, encoding = 'UTF-8') as file:
      players = json.load(file)
      self._players = [build_player(self, player, i) for i, player in enumerate(players)]
    
    self._turn_accumulator, self._index = 0, 0
    self._is_playing = True

    self._straight_doubles = 0

    self._image_counter = 0

  def players(self) -> list[Player]: return self._players
  def current_player(self) -> Player: return self.players()[self._index]
  def tiles(self) -> list[Tile]: return self._tiles
  def dice(self) -> tuple[int, int]: return self._dice

  def num_players(self) -> int: return len(self.players())

  def color(self, color: str) -> set[Street]:
    '''Returns the set of streets on the board with the specified color.'''
    return self._colors[color]
  
  def jail_position(self) -> int: return 10

  def throw_dice(self) -> None:
    '''Updates dice with two new random values and redraws board.'''
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
    This function is called whenever the board is updated substantially.'''
    draw(self, f'imgs/{self._image_counter:05d}.svg')
    self._image_counter += 1

  def _make_way_for_next_player(self) -> None:
    '''Makes way for next player.'''
    self._straight_doubles = 0
    self._index += 1
    self._index %= self.num_players()

  def _prison_routine(self):
    assert self.current_player().is_in_prison()

    if self.current_player().turns_in_prison() == 3:
      self.current_player().free()
      return

    self.throw_dice()
    if self.dice()[0] == self.dice()[1]:
      self.current_player().free()
      return
    
    if self.current_player().get_out_of_jail_free_cards() > 0:
      self.current_player().prompt_use_goojfc()
      return
    
    self.current_player().log_a_turn_in_prison()
    raise const.EndTurn

  def _play_turn(self):
    if self.current_player().is_bankrupt(): raise const.EndTurn

    self._turn_accumulator += 1
    print(f'TURN {self._turn_accumulator}: {self.current_player()}\'s turn')

    if self.current_player().is_in_prison(): self._prison_routine()
    
    self.throw_dice()

    self._handle_doubles()
    self.current_player().move_forward(sum(self.dice()))
    
    self.draw()

    current_tile = self.tiles()[self.current_player().position()]

    print(f'{self.current_player()} has landed on {current_tile}')
    current_tile.land_on(self.current_player())

    self.current_player().post_turn_actions()

    raise const.EndTurn
  
  def play(self) -> None:
    '''Plays the game until only one player is standing. Progressively
    generates illustrations of the board state for every turn, which are stored
    in ./imgs'''
    lim = 1000
    for _ in range(lim):
      try: self._play_turn()
      except const.EndTurn:
        if (self._straight_doubles == 3
          or not self._doubles): self._make_way_for_next_player()

class DebugBoard(Board):
  '''Altered version of the normal board used for testing.
  Takes an iterator of die rolls for an input, instead of using a seed to generate inputs.
  Stops execution when there are no more dice to roll.'''
  def __init__(
    self,
    die_inputs: Iterable[tuple[int, int]],
    cards: Iterable[Card] = list[Card]()
  ):
    super().__init__()
    self._die_inputs = iter(die_inputs)
    self._cards = iter(cards)
  
  def throw_dice(self) -> None:
    '''Updates dice to next tuple in die inputs.
    Raises StopIteration if there are no more inputs.'''
    self._dice = next(self._die_inputs)
    self.draw()
  
  def play(self) -> None:
    '''Runs game until die inputs end.'''
    try: super().play()
    except StopIteration: print('Die rolls or cards finished. Stopping play')

  def run(self, turns: int) -> None:
    '''Runs game for a limited number of turns.'''
    for _ in range(turns):
      try: self._play_turn()
      except const.EndTurn:
        if not self._doubles: self._make_way_for_next_player()

def save_board(board: Board, pickle_path: str) -> None:
  with open(pickle_path, "wb") as f: pickle.dump(board, f)

def load_board(pickle_path: str) -> Board:
  with open(pickle_path, "rb") as f: return pickle.load(f)