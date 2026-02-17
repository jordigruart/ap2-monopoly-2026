from __future__ import annotations

import pickle, json
from player import Player, build_player
from tile import Tile, build_tile

class Board:
  _turn: int

  def __init__(
    self,
    tiles_json_path: str,
    chance_json_path: str,
    community_chest_json_path: str,
    players_json_path: str,
  ):
    '''We assume the tiles appear in tiles_json_path in positional order, just
    as they do in the file given to us.'''
    with open(tiles_json_path, encoding = 'UTF-8') as file:
      self._tiles = [build_tile(self, tile) for tile in json.load(file)]
    
    with open(players_json_path, encoding = 'UTF-8') as file:
      players = json.load(file)
      self._players = [build_player(self, players[i], i) for i in range(len(players))]
    
    self._turn = 0

  def players(self) -> list[Player]:
    return self._players

  def tiles(self) -> list[Tile]:
    return self._tiles

  def dice(self) -> tuple[int, int]:
    return (1, 1)

  def current_player(self) -> Player:
    return self.players()[self.turn() % self.num_players()]

  def num_tiles(self) -> int:
    return 40
  
  def num_players(self) -> int: return len(self.players())

  def jail_position(self) -> int:
    return 10

  def play(self) -> None: ...

  def turn(self): return self._turn

def save_board(board: Board, pickle_path: str) -> None:
  with open(pickle_path, "wb") as f: pickle.dump(board, f)

def load_board(pickle_path: str) -> Board:
  with open(pickle_path, "rb") as f: return pickle.load(f)
