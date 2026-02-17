from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
  from board import Board
  from player import Player

class Tile:
  """Base class for all board tiles."""

  def __init__(
    self,
    board: Board,
    position: int,
    name: str,
    tile_type: str,
    description: str,
  ):
    self._board = board
    self._position = position
    self._name = name
    self._tile_type = tile_type
    self._description = description

  def land_on(self, player: Player) -> None:
    '''Handle what happens when a player lands on this tile. To be implemented in subclass.'''
    pass

  def type(self) -> str: return self._tile_type
  def name(self) -> str: return self._name
  def description(self) -> str: return self._description
  def position(self) -> int: return self._position
  def board(self) -> Board: return self._board

class Property(Tile):
  def __init__(
    self,
    board: Board,
    position: int,
    name: str,
    tile_type: str,
    price: int,
    rent: int,
    mortgage: int,
    description: str,
  ): ...

class Street(Property):
  def __init__(
    self,
    board: Board,
    position: int,
    name: str,
    tile_type: str,
    color: str,
    price: int,
    rent: int,
    rent_with_color_set: int,
    rent_with_1_house: int,
    rent_with_2_houses: int,
    rent_with_3_houses: int,
    rent_with_4_houses: int,
    rent_with_hotel: int,
    house_cost: int,
    hotel_cost: int,
    mortgage: int,
    description: str,
  ): ...

# more subclasses
...

def build_tile(board: Board, data: dict[str, Any]) -> Tile:
  return Tile(
    board, data.get('position', 0), data.get('name', ''), data.get('type', 'default'), data.get('description', '')
  )