from __future__ import annotations

from typing import Iterator

import pickle, json
from player import Player, build_player
from tile import Tile, Street, build_tile
from draw import draw
from deck import Deck

import random

class Board:
  _tiles: list[Tile]
  _colors: dict[str, set[Street]]

  def __init__(
    self,
    tiles_json_path: str,
    chance_json_path: str,
    community_chest_json_path: str,
    players_json_path: str,
  ):
    # We assume the items appear in the files in positional order, just
    # as they do in the files given to us.
    
    # load tiles
    self._tiles = list[Tile]()
    self._colors = dict[str, set[Street]]()
    with open(tiles_json_path, encoding = 'UTF-8') as file:
      for raw_tile in json.load(file):
        tile = build_tile(self, raw_tile)
        self._tiles.append(tile)

        if tile.tile_type() == 'property':
          assert isinstance(tile, Street)
  
          if tile.color not in self._colors: self._colors[tile.color] = set[Street]()
          self._colors[tile.color].add(tile)

    # load decks
    self._chance_deck = Deck(chance_json_path)
    self._community_deck = Deck(community_chest_json_path)

    # load players
    with open(players_json_path, encoding = 'UTF-8') as file:
      players = json.load(file)
      self._players = [build_player(self, players[i], i) for i in range(len(players))]
    
    self._turn_accumulator, self._index = 0, 0
    self._is_playing = True

    self._straight_doubles = 0

  def players(self) -> list[Player]: return self._players
  def current_player(self) -> Player: return self.players()[self._index]
  def tiles(self) -> list[Tile]: return self._tiles
  def dice(self) -> tuple[int, int]: return self._dice

  def num_tiles(self) -> int: return 40
  def num_players(self) -> int: return len(self.players())

  def color(self, color: str) -> set[Street]:
    '''Returns the set of streets on the board with the specified color.'''
    return self._colors[color]
  
  def jail_position(self) -> int: return 10

  def is_playing(self) -> bool: return self._is_playing

  def _throw_dice(self) -> None:
    '''Updates dice with two new random values.'''
    self._dice = random.randint(1, 6), random.randint(1, 6)

  def _handle_doubles(self) -> None:
    '''Updates the amount of straight doubles rolled and sends current player
    to prison if they have rolled three doubles in a row.'''
    self._doubles = self.dice()[0] == self.dice()[1]

    if self._doubles:
      self._straight_doubles += 1
      
      if self._straight_doubles == 3:
        self.current_player().imprison()

  def _make_way_for_next_player(self) -> None:
    '''Makes way for next player.'''
    self._straight_doubles = 0
    self._index += 1
    self._index %= self.num_players()

  def _play_turn(self):
    self._turn_accumulator += 1
    print(f'TURN {self._turn_accumulator}: {self.current_player().name()}\'s turn')

    if not self.current_player().can_play():
      self._make_way_for_next_player()
      return
    
    self._throw_dice()
    print(f'{self.current_player().name()} rolled {self._dice}')
    draw(self, f'imgs/turn-{self._turn_accumulator:04d}-a.svg')

    self._handle_doubles()
  
    if not self.current_player().can_play():
      self._make_way_for_next_player()
      return

    self.current_player().move_forward(sum(self.dice()))
    
    draw(self, f'imgs/turn-{self._turn_accumulator:04d}-b.svg')

    current_tile = self.tiles()[self.current_player().position()]

    print(f'{self.current_player().name()} has landed on {current_tile}')
    current_tile.land_on(self.current_player())

    draw(self, f'imgs/turn-{self._turn_accumulator:04d}-c.svg')

    if not self._doubles: self._make_way_for_next_player()
  
  def play(self) -> None:
    '''Plays the game until only one player is standing. Progressively
    generates illustrations of the board state for every turn, which are stored
    in ./imgs'''
    LIM = 21
    for _ in range(LIM): self._play_turn()

class DebugBoard(Board):
  '''Altered version of the normal board used for testing.
  Takes an iterator of die rolls for an input, instead of using a seed.
  Stops execution when there are no more die to roll.'''
  def __init__(
    self,
    tiles_json_path: str,
    chance_json_path: str,
    community_chest_json_path: str,
    players_json_path: str,
    die_inputs: Iterator[tuple[int, int]]
  ):
    super().__init__(tiles_json_path, chance_json_path, community_chest_json_path, players_json_path)
    self._die_inputs = die_inputs
  
  def _throw_dice(self) -> None:
    '''Updates dice to next tuple in die inputs.
    Raises StopIteration if there are no more inputs.'''
    self._dice = next(self._die_inputs)
  
  def play(self) -> None:
    try: super().play()
    except StopIteration: print('Dice rolls finished.')

def save_board(board: Board, pickle_path: str) -> None:
  with open(pickle_path, "wb") as f: pickle.dump(board, f)

def load_board(pickle_path: str) -> Board:
  with open(pickle_path, "rb") as f: return pickle.load(f)