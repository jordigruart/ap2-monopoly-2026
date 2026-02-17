from __future__ import annotations
from typing import TYPE_CHECKING, Any
from tile import Property

if TYPE_CHECKING:
  from board import Board

class Player:
  _board: Board
  _name: str
  _piece: str
  _color: str
  _index: int
  _position: int
  _money: int

  def __init__(
    self,
    board: Board,
    name: str,
    piece: str,
    color: str,
    index: int,
  ): ...

  def board(self) -> Board:
    return self._board

  def name(self) -> str:
    return self._name

  def piece(self) -> str:
    return self._piece

  def color(self) -> str:
    return self._color

  def index(self) -> int:
    return self._index

  def broke(self) -> bool:
    """Return True if the player has negative money."""
    return self._money < 0

  def money(self) -> int:
    return self._money

  def position(self) -> int:
    return self._position

  def get_out_of_jail_free_cards(self) -> int:
    return 0

  def turns_in_prison(self) -> int:
    return 0

  def owned_properties(self) -> list[Property]:
    return []

def build_player(board: Board, data: dict[str, Any], index: int) -> Player:
  """Build a Player from JSON-like dict with 'name', 'piece', and 'color' keys."""
  return Player(board, data["name"], data["piece"], data["color"], index)