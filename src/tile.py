from __future__ import annotations
from typing import TYPE_CHECKING, Any, Literal, Optional

if TYPE_CHECKING:
  from board import Board
  from player import Player
  from deck import Deck

class Tile:
  """Base class for all board tiles."""
  _board: Board
  _position: int
  _name: str

  _tile_type: str

  def __init__(self, board: Board, position: int, name: str):
    self._board = board
    self._position = position
    self._name = name

    self._tile_type = 'special' # to be overridden in inheritance class

  def tile_type(self) -> str: return self._tile_type
  def name(self) -> str: return self._name
  def position(self) -> int: return self._position
  def board(self) -> Board: return self._board

  def land_on(self, player: Player) -> None:
    '''Handle what happens when a player lands on this tile. Do nothing by
    default. Behaviour may be modified in inheritance class.
    
    Note: GO bonus already handled by player.py's movement methods.'''
    pass

class Tax(Tile):
  def __init__(self, board: Board, position: int, name: str,
    amount: int
    ):
    super().__init__(board, position, name)

    self._amount = amount
    self._tile_type = 'tax'

class DeckTile(Tile):
  _deck: Deck

  def __init__(self, board: Board, position: int, name: str,
    tile_type: Literal['chance'] | Literal['community_chest'],
  ):
    super().__init__(board, position, name)
    
    self._tile_type = tile_type

class Property(Tile):
  def __init__(self, board: Board, position: int, name: str,
    price: int, mortgage: int
    ):
    super().__init__(board, position, name)

    self._price = price
    self._mortgage = mortgage

    self._owner: Optional[Player] = None
    self._tile_type = 'property'
  
  def has_owner(self) -> bool:
    '''Returns whether the tile is in somebody's possession.'''
    return self._owner is not None
  
  def owner(self) -> Optional[Player]:
    '''Returns the owner of the tile.'''
    return self._owner
  
  def rent(self) -> int:
    '''Returns the rent to be charged considering the current state of the
    board. To be inclemented in inheritance class.'''
    raise NotImplementedError
    
class Street(Property):
  def __init__(self, board: Board, position: int, name: str,
    price: int, mortgage: int,

    color: str,

    starting_rent: int, rent_with_color_set: int, rent_with_1_house: int,
    rent_with_2_houses: int, rent_with_3_houses: int, rent_with_4_houses: int,
    rent_with_hotel: int,

    house_cost: int, hotel_cost: int
    ):
    super().__init__(board, position, name, price, mortgage)

    self.color = color

    self._starting_rent = starting_rent
    self._rent_with_color_set = rent_with_color_set
    self._rent_with_1_house = rent_with_1_house 
    self._rent_with_2_houses = rent_with_2_houses 
    self._rent_with_3_houses = rent_with_3_houses 
    self._rent_with_4_houses = rent_with_4_houses 
    self._rent_with_hotel = rent_with_hotel 

    self._house_cost = house_cost 
    self._hotel_cost = hotel_cost 

    self._tile_type = 'property'

class Station(Property):
  def __init__(self, board: Board, position: int, name: str,
    price: int, mortgage: int,

    starting_rent: int, rent_with_2_stations: int, rent_with_3_stations: int,
    rent_with_4_stations: int,
  ):
    super().__init__(board, position, name, price, mortgage)
    
    self._starting_rent = starting_rent
    self._rent_with_2_stations = rent_with_2_stations
    self._rent_with_3_stations = rent_with_3_stations
    self._rent_with_4_stations = rent_with_4_stations

    self._tile_type = 'station'

class Utility(Property):
  def __init__(self, board: Board, position: int, name: str,
    price: int, mortgage: int,
    default_multiplier: int, multiplier_with_both: int
  ):
    super().__init__(board, position, name, price, mortgage)

    self._tile_type = 'utility'

def build_tile(board: Board, data: dict[str, Any]) -> Tile:
  tile_type = data['type']

  match tile_type:
    case 'property': return Street(
      board, data['position'], data['name'], data['price'], data['mortgage'],
      data['color'], data['rent'], data['rentWithColorSet'],
      data['rentWith1House'], data['rentWith2Houses'], data['rentWith3Houses'],
      data['rentWith4Houses'], data['rentWithHotel'], data['houseCost'],
      data['hotelCost']
    )

    case 'station': return Station(
      board, data['position'], data['name'], data['price'], data['mortgage'],
      data['rent'], data['rentWith2Stations'], data['rentWith3Stations'],
      data['rentWith4Stations'], 
    )

    case 'utility': return Utility(
      board, data['position'], data['name'], data['price'], data['mortgage'],
      data['rentMultiplier'], data['rentMultiplierWithBoth']
    )

    case 'chance' | 'community_chest': return DeckTile(
      board, data['position'], data['name'], tile_type
    )

    case 'tax': return Tax(
      board, data['position'], data['name'], data['amount']
    )

    case _: return Tile(
      board, data['position'], data['name']
    )