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
  ): ...

  def land_on(self, player: Player) -> None:
    """Handle what happens when a player lands on this tile."""
    pass

  def type(self) -> str: ...
  def name(self) -> str: ...
  def description(self) -> str: ...
  def position(self) -> int: ...
  def board(self) -> Board: ...

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

def build_tile(board: Board, data: dict[str, Any]) -> Tile: ...