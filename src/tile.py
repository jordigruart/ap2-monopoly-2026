from __future__ import annotations
from typing import TYPE_CHECKING, Any, Literal, Optional
import const

if TYPE_CHECKING:
  from board import Board
  from player import Player

class Tile:
  """Base class for all board tiles."""
  _tile_type: str

  _board: Board
  _position: int
  _name: str

  def __init__(self, board: Board, position: int, name: str):
    self._board = board
    self._position = position
    self._name = name

    self._tile_type = 'special' # to be overridden in inheritance class

  def __str__(self) -> str: return self.name()

  def tile_type(self) -> str: return self._tile_type
  def name(self) -> str: return self._name
  def position(self) -> int: return self._position
  def board(self) -> Board: return self._board

  def land_on(self, player: Player) -> None:
    '''Handle what happens when a player lands on this tile. Do nothing by
    default.
    
    Note: GO bonus already handled by player.py's movement methods.'''
    if 'Go To Jail' in self.name(): player.imprison()    
    else: pass 

class Tax(Tile):
  _amount: int

  def __init__(self, board: Board, position: int, name: str,
    amount: int
    ):
    super().__init__(board, position, name)

    self._amount = amount
    self._tile_type = 'tax'
  
  def land_on(self, player: Player):
    player.deduct(self._amount)
    self.board().draw()

class DeckTile(Tile):
  def __init__(self, board: Board, position: int, name: str,
    tile_type: Literal['chance'] | Literal['community_chest']):
    super().__init__(board, position, name)
    
    self._tile_type = tile_type
  
  def land_on(self, player: Player):
    self.board().draw()

class Property(Tile):
  _price: int
  _mortgage: int

  _owner: Optional[Player]
  _is_mortgaged: bool

  def __init__(self, board: Board, position: int, name: str,
    price: int, mortgage: int):
    super().__init__(board, position, name)

    self._price = price
    self._mortgage = mortgage

    self._owner = None
    self._tile_type = 'property'

    self._is_mortgaged = False

  def price(self) -> int: return self._price
  def is_mortgaged(self) -> bool: return self._is_mortgaged
  
  def has_owner(self) -> bool:
    '''Returns whether the property is in somebody's possession.'''
    return self._owner is not None
  
  def owner(self) -> Optional[Player]:
    '''Returns the owner of the property, or None if it is not owned.'''
    return self._owner
  
  def rent(self) -> int:
    '''Returns the rent to be charged considering the current state of the
    board.'''
    # to be implemented in subclass
    raise NotImplementedError

  def reset(self) -> None:
    '''Resets property so that it may be claimed again. The previous owner
    gets no money from this operation.'''
    self._is_mortgaged = False
    self._owner = None
  
  def land_on(self, player: Player) -> None:
    if self.has_owner():
      if not self.is_mortgaged() and not player.owns(self):
        self.owner().entrust(player.deduct(self.rent())) # type: ignore
        print(f'{player.name()} has paid ${self.rent()} to {self.owner().name()}')
        self.board().draw()

    else:
      player.prompt_buy(self)

  def set_owner(self, player: Player):
    '''Sets this tile's owner to the specified player.
    This method does not charge the player any money.'''
    self._owner = player

  def mortgage(self):
    '''Mortgages tile, granting its owner the tile's corresponding mortgage
    bonus, which is half its price by definition.
    
    If the tile is a street, there must be no houses or hotels on the tile in
    order to be mortgaged.'''
    assert self.has_owner()
    assert not self.is_mortgaged()
    self._is_mortgaged = True
    self.owner().entrust(self._mortgage) # type: ignore

    self.board().draw()
  
  def demortgage(self):
    '''Demortgages tile and deducts 110% of its mortgage fee from its owner.'''
    assert self.has_owner()
    assert self.is_mortgaged()
    self._is_mortgaged = False
    self.owner().deduct(int(self._mortgage * const.MORTGAGE_INTEREST_RATE)) # type: ignore

    self.board().draw()

class Street(Property):
  _starting_rent: int
  _rent_with_color_set: int
  _rent_with_1_house: int
  _rent_with_2_houses: int
  _rent_with_3_houses: int
  _rent_with_4_houses: int
  _rent_with_hotel: int

  _house_cost: int
  _hotel_cost: int

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

    self._houses = 0 # amount of houses on property; 5 with hotel
    self._has_hotel = False

    self._tile_type = 'property'
  
  def houses(self):
    '''Returns the amount of houses currently on the tile.
    
    If there happens to be a hotel on the tile, it will return 5.'''
    return self._houses
  
  def has_hotel(self): return self._has_hotel

  def mortgage(self):
    assert self._houses == 0
    super().mortgage()

  def rent(self):
    if not self.has_owner(): return 0
    if self.is_mortgaged(): return 0

    if self._has_hotel: return self._rent_with_hotel
    if self.owner().owns_color(self.color): # type: ignore
      match self._houses:
        case 0: return self._rent_with_color_set
        case 1: return self._rent_with_1_house
        case 2: return self._rent_with_2_houses
        case 3: return self._rent_with_3_houses
        case 4: return self._rent_with_4_houses
        case _: raise ValueError('Too many houses')
    
    else: return self._starting_rent

  def build(self):
    '''Builds a house on the tile; or an hotel, in case there are 4 houses.
    
    In order to build on a tile, its owner must have its color set.
    A new house cannot be built on a street until every other street in the
    color set either has an hotel or has at least the number of houses on the
    street you want to build on.

    A tile may not be built on if any of the streets in its color set is
    mortgaged.
    
    A tile may not be built on further after having built an hotel on it.'''

    assert self.has_owner()
    assert self.owner().owns_color(self.color) # type: ignore

    assert all(not property.is_mortgaged()
      for property in self.board().color(self.color))
    assert self.houses() <= 4

    assert all(
      property.houses() >= self.houses()
      for property in self.board().color(self.color) #do we have to check if it is mortgage
    )

    if self.houses() == 4: # build hotel
      self.owner().deduct(self._hotel_cost) # type: ignore
      self._has_hotel = True

    else: self.owner().deduct(self._house_cost) # type: ignore

    self._houses += 1

    self.board().draw()
    print(f'''{self.owner().name()} has built on {self.name()}. The tile now has {'an hotel' if self.has_hotel() else str(self._houses) + ' houses'}.''')

  def sell(self):
    '''Sells a single house (or hotel) on the tile for half its price,
    and entrusts the amount to its owner.

    A house cannot be sold unless the number of houses in each street in the
    color set is less than or equal to the number of houses on the street you
    want to sell on. An hotel may always be sold.
    
    Cannot sell if there are no houses on the tile.'''
    assert self.has_owner()
    assert self.owner().owns_color(self.color) # type: ignore
  
    assert self.houses() > 0, 'No houses left to sell'

    assert all(
      property.houses() <= self.houses()
      for property in self.board().color(self.color) if not property.is_mortgaged()
    )

    if self._has_hotel:
      self.owner().entrust(self._hotel_cost//2) # type: ignore
      self._has_hotel = False

    else: self.owner().entrust(self._house_cost//2) # type: ignore

    self._houses -= 1
    self.board().draw()

  def reset(self):
    '''Resets property so that it may be claimed again. Removes all houses and
    hotels. The previous owner gets no money from this operation.'''
    super().reset()
    self._houses = 0
    self._has_hotel = False

class Station(Property):
  _starting_rent: int
  _rent_with_2_stations: int
  _rent_with_3_stations: int
  _rent_with_4_stations: int

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
  
  def rent(self) -> int:
    match self.owner().station_count(): # type: ignore
      case 1: return self._starting_rent
      case 2: return self._rent_with_2_stations
      case 3: return self._rent_with_3_stations
      case 4: return self._rent_with_4_stations
      case _: raise

class Utility(Property):
  _default_multiplier: int
  _multiplier_with_both: int

  def __init__(self, board: Board, position: int, name: str,
    price: int, mortgage: int,
    default_multiplier: int, multiplier_with_both: int
  ):
    super().__init__(board, position, name, price, mortgage)

    self._default_multiplier = default_multiplier
    self._multiplier_with_both = multiplier_with_both
    
    self._tile_type = 'utility'
  
  def rent(self) -> int:
    if not self.has_owner(): return 0

    self.board().throw_dice()
    return sum(self.board().dice()) * (self._default_multiplier if self.owner().utility_count() == 1 else self._multiplier_with_both)

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