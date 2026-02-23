from __future__ import annotations

import pickle, json
from player import Player, build_player
from tile import Tile, build_tile
from draw import draw
from deck import Deck

import random

class Board:
  _turn: int

  def _build(self, path: str, builder: function) -> list:
    with open(path, encoding = 'UTF-8') as file:
      return [builder.__call__(self, item) for item in json.load(file)]

  def __init__(
    self,
    tiles_json_path: str,
    chance_json_path: str,
    community_chest_json_path: str,
    players_json_path: str,
  ):    
    # We assume the items appear in the files in positional order, just
    # as they do in the files given to us.'''
    
    self._tiles: list[Tile] = self._build(tiles_json_path, build_tile)

    self._chance_deck = Deck(chance_json_path)
    self._community_deck = Deck(community_chest_json_path)    

    with open(players_json_path, encoding = 'UTF-8') as file:
      players = json.load(file)
      self._players = [build_player(self, players[i], i) for i in range(len(players))]
    
    self._turn_accumulator, self._index = 0, 0
    self._is_playing = True

    self._straight_doubles = 0

  def players(self) -> list[Player]:
    return self._players

  def tiles(self) -> list[Tile]:
    return self._tiles

  def dice(self) -> tuple[int, int]:
    return self._dice
    
  def current_player(self) -> Player:
    return self.players()[self._index]

  def num_tiles(self) -> int:
    return 40
  
  def num_players(self) -> int: return len(self.players())

  def jail_position(self) -> int:
    return 10

  def is_playing(self) -> bool: return self._is_playing

  def _doubles(self) -> bool: return self.dice()[0] == self.dice()[1]

  def _throw_dice(self) -> None:
    self._dice = random.randint(1, 6), random.randint(1, 6)

  def _handle_doubles(self) -> None:
    if self._doubles():
      self._straight_doubles += 1
      
    if self._straight_doubles == 3:
      self.current_player().imprison()

  def _make_way_for_next_player(self) -> None:
    self._stright_doubles = 0
    self._index += 1
    self._index %= self.num_players()

  def _play_turn(self):
    self._turn_accumulator += 1

    if not self.current_player().can_play():
      self._make_way_for_next_player()
      return
    
    self._throw_dice()
    draw(self, f'imgs/turn-{self._turn_accumulator:04d}-a.svg')

    self._handle_doubles()

    if not self.current_player().can_play():
      self._make_way_for_next_player()
      return

    self.current_player().move_forward(sum(self.dice()))
    
    draw(self, f'imgs/turn-{self._turn_accumulator:04d}-b.svg')

    current_tile = self.tiles()[self.current_player().position()]
    current_tile.land_on(self.current_player())

    if not self._doubles(): self._make_way_for_next_player()
  
  def play(self) -> None:
    LIM = 16
    for _ in range(LIM): self._play_turn()

def save_board(board: Board, pickle_path: str) -> None:
  with open(pickle_path, "wb") as f: pickle.dump(board, f)

def load_board(pickle_path: str) -> Board:
  with open(pickle_path, "rb") as f: return pickle.load(f)