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
    
    Note: GO bonus already handled by player.py's movement methods.

    Board-drawing: this function only draws the board if something substantial
    happens when the tile is landed on. Tiles that do not have any
    interesting behavior (Free Parking, Go, Just Visiting) do not cause the
    board to be redrawn.'''
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

  _rent: int

  def __init__(self, board: Board, position: int, name: str,
    price: int, mortgage: int):
    super().__init__(board, position, name)

    self._price = price
    self._mortgage = mortgage

    self._owner = None
    self._tile_type = 'property'

    self._is_mortgaged = False
    self._rent = 0

  def price(self) -> int: return self._price
  def is_mortgaged(self) -> bool: return self._is_mortgaged
  
  def mortgage_bonus(self) -> int: return self._mortgage
  def demortgage_fee(self) -> int: return int(self.mortgage_bonus() * const.MORTGAGE_INTEREST_RATE)

  def owner(self) -> Optional[Player]:
    '''Returns the owner of the property, or None if it is not owned.'''
    return self._owner
  
  def rent(self) -> int:
    '''Returns the rent to be charged considering the current state of the board.'''
    # to be implemented in subclass
    raise NotImplementedError

  def reset(self) -> None:
    '''Resets property so that it may be claimed again. The previous owner
    gets no money from this operation.'''
    self._is_mortgaged = False
    self._owner = None
  
  def land_on(self, player: Player) -> None:
    if self.owner() is not None:
      if not self.is_mortgaged() and not player.owns(self):
        rent = self.rent()

        self.owner().entrust(player.deduct(rent)) # type: ignore
        print(f'{player} has paid ${rent} to {self.owner()}')
        self.board().draw()

    else:
      player.prompt_buy(self)

  def mortgage(self):
    '''Mortgages tile, granting its owner the tile's corresponding mortgage
    bonus, which is half its price by definition.
    
    If the tile is a street, there must be no houses or hotels on the tile in
    order to be mortgaged.
    
    Board-drawing: This function draws the board.'''
    assert self.owner() is not None
    assert not self.is_mortgaged()
    self._is_mortgaged = True
    self.owner().entrust(self._mortgage) # type: ignore

    print(f'{self.owner()} has mortgaged {self}')
    self.board().draw()
  
  def demortgage(self):
    '''Demortgages tile and deducts 110% of its mortgage fee from its owner.'''
    assert self.owner() is not None
    assert self.is_mortgaged()
    self._is_mortgaged = False
    self.owner().deduct(int(self._mortgage * const.MORTGAGE_INTEREST_RATE)) # type: ignore

    self.board().draw()

class Street(Property):
  _starting_rent: int
  _color_set_rents: list[int] # contains rent with color set and 0 houses, 1 houses, etc.
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
    self._color_set_rents = [rent_with_color_set] + [rent_with_1_house, rent_with_2_houses,
      rent_with_3_houses, rent_with_4_houses]
    self._rent_with_hotel = rent_with_hotel 

    self._house_cost = house_cost 
    self._hotel_cost = hotel_cost 

    self._houses = 0 # amount of houses on property; 5 with hotel
    self._has_hotel = False

    self._tile_type = 'property'
  
  def color_set(self) -> set[Street]:
    '''Returns the set of streets on the board with the same color as this tile.'''
    return self.board().color_set(self.color)

  def houses(self):
    '''Returns the amount of houses currently on the tile.
    
    If there happens to be a hotel on the tile, it will return 5.'''
    return self._houses
  
  def has_hotel(self): return self._has_hotel

  def mortgage(self):
    assert all(property.houses() == 0 for property in self.color_set())
    super().mortgage()

  def rent(self) -> int:
    if self.owner() is None: return 0
    if self.is_mortgaged(): return 0

    if self._has_hotel: return self._rent_with_hotel
    if self.owner().owns_color(self.color): return self._color_set_rents[self._houses]
    
    else: return self._starting_rent

  def building_cost(self):
    '''Returns the cost of building a building on the tile.'''
    return self._hotel_cost if self.has_hotel() else self._house_cost
  
  def selling_bonus(self):
    '''Returns the amount earned from selling a building on this tile.
    It is half the building cost.'''
    return self.building_cost()//2

  def build(self):
    '''Builds a house on the tile; or an hotel, in case there are 4 houses.
    
    In order to build on a tile, its owner must have its color set.
    A new house cannot be built on a street until every other street in the
    color set either has an hotel or has at least the number of houses on the
    street you want to build on.

    A tile may not be built on if any of the streets in its color set is
    mortgaged.
    
    A tile may not be built on further after having built an hotel on it.'''

    assert self.owner() is not None
    assert self.owner().owns_color(self.color) # type: ignore

    assert all(not property.is_mortgaged()
      for property in self.color_set())
    assert self.houses() <= 4

    assert all(property.houses() >= self.houses()
      for property in self.color_set()
    )

    if self.houses() == 4: self._has_hotel = True
    self._houses += 1

    assert self.owner().balance() >= self.building_cost() # type: ignore
    self.owner().deduct(self.building_cost()) # type: ignore

    self.board().draw()
    print(f'{self.owner()} has built on {self}. The tile now has',
      'an hotel' if self.has_hotel() else (str(self._houses) + ' houses.'))

  def sell(self):
    '''Sells a single house (or hotel) on the tile for half its price,
    and entrusts the amount to its owner.

    A house cannot be sold unless the number of houses in each street in the
    color set is less than or equal to the number of houses on the street you
    want to sell on. An hotel may always be sold.
    
    Cannot sell if there are no houses on the tile.'''
    assert self.owner() is not None
    assert self.owner().owns_color(self.color) # type: ignore
  
    assert self.houses() > 0, 'No houses left to sell'

    assert all(
      property.houses() <= self.houses()
      for property in self.color_set() if not property.is_mortgaged()
    )  

    if self._has_hotel: self._has_hotel = False

    self.owner().entrust(self.selling_bonus()) # type: ignore
    self._houses -= 1

    self.board().draw()
    print(f'{self.owner()} has sold on {self}. The tile now has',
      'an hotel' if self.has_hotel() else (str(self._houses) + ' houses.'))

  def reset(self):
    '''Resets property so that it may be claimed again. Removes all houses and
    hotels. The previous owner gets no money from this operation.'''
    super().reset()
    self._houses = 0
    self._has_hotel = False

class Station(Property):
  _rents: list[int] # contains rent with 1 station, rent with 2 stations, etc...

  def __init__(self, board: Board, position: int, name: str,
    price: int, mortgage: int,

    starting_rent: int, rent_with_2_stations: int, rent_with_3_stations: int,
    rent_with_4_stations: int,
  ):
    super().__init__(board, position, name, price, mortgage)
    
    self._rents = [0, starting_rent, rent_with_2_stations, rent_with_3_stations, rent_with_4_stations]
    
    self._tile_type = 'station'
  
  def rent(self) -> int:
    if self.owner() is None: return 0
    return self._rents[self.owner().station_count()]

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
    if self.owner() is None: return 0

    self.board().throw_dice()
    return sum(self.board().dice()) * (
      self._default_multiplier if self.owner().utility_count() == 1 else self._multiplier_with_both # type: ignore
      )

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