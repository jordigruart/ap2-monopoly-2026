import pickle
from player import Player
from tile import Tile

class Board:
  def __init__(
    self,
    tiles_json_path: str,
    chance_json_path: str,
    community_chest_json_path: str,
    players_json_path: str,
  ): ...

  def players(self) -> list[Player]:
    return []

  def tiles(self) -> list[Tile]:
    return []

  def dice(self) -> tuple[int, int]:
    return (1, 1)

  def current_player(self) -> Player: ...

  def num_tiles(self) -> int:
    return 40

  def jail_position(self) -> int:
    return 10

  def play(self) -> None: ...

def save_board(board: Board, pickle_path: str) -> None:
  with open(pickle_path, "wb") as f: pickle.dump(board, f)

def load_board(pickle_path: str) -> Board:
  with open(pickle_path, "rb") as f: return pickle.load(f)
