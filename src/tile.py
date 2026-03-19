from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional
import const, aitools

if TYPE_CHECKING:
  from deck import Deck
  from board import Board
  from player import Player

class Tile:
  """Base class for all board tiles."""
  _tile_type: str

  _board: Board
  _position: int
  _name: str

  def __init__(self, board: Board, position: int, name: str, type: str):
    '''Initializes constants shared among all tiles:
     - board is the Board instance the tile belongs to
     - position is its position on the board
     - name is tile name
     - type is tile type
    '''
    self._board = board
    self._position = position
    self._name = name

    self._tile_type = type

  def __str__(self) -> str: return self.name()

  def tile_type(self) -> str: return self._tile_type
  def name(self) -> str: return self._name
  def position(self) -> int: return self._position
  def board(self) -> Board:
    '''Returns the board the tile belongs to.'''
    return self._board

  def land_on(self, player: Player) -> None:
    '''Handle what happens when player lands on this tile.
    
    Note: GO bonus already handled by player.py's movement methods.
    Board-drawing: this function draws the board if something interesting
    happens. Check the readme for all the cases where the board is drawn.'''
    print(f'{player} has landed on {self}')

class Special(Tile):
  '''Class for special tiles (Go, Free Parking, Jail, Go to Jail)'''
  def __init__(self, board: Board, position: int, name: str, type: str,
    description: str):
    '''See Tile's __init__ method for board, position, name, type
    - description is a description of the tile's action
    '''
    super().__init__(board, position, name, type)
  
  def land_on(self, player: Player):
    super().land_on(player)
    if 'Go To Jail' in self.name(): player.imprison()    
    else: pass

class Tax(Tile):
  _amount: int

  def __init__(self, board: Board, position: int, name: str, type: str,
    amount: int, description: str):
    '''See Tile's __init__ method for board, position, name, type
     - amount is amount to be charged when landed on'''
    super().__init__(board, position, name, type)
    self._amount = amount
  
  def land_on(self, player: Player):
    super().land_on(player)
    player.deduct(self._amount, None)
    self.board().draw()

class DeckTile(Tile):
  _deck: Deck

  def __init__(self, board: Board, position: int, name: str, type: str,
    description: str): 
    '''See Tile's __init__ method for board, position, name, type
    - description is a description of the tile's action
    '''
    super().__init__(board, position, name, type)

  def deck(self):
    '''Returns the Deck object that is drawn from when this line is landed on.'''
    return (
      self.board().chance_deck() if self._tile_type == 'chance'
      else self.board().community_deck()
    )

  def land_on(self, player: Player):
    super().land_on(player)

    card = self.deck().extract()
    print(f'{player} has drawn {card.title}: {card.description}')
    card.execute(player)

class Property(Tile):
  '''Base class for ownable properties (Street, Station and Utility).'''
  _price: int;  _mortgage: int
  _owner: Optional[Player]; _is_mortgaged: bool

  def __init__(self, board: Board, position: int, name: str, type: str,
    price: int, mortgage: int):
    '''See Tile's __init__ method for board, position, name, type
     - price is the price of the property
     - mortgage is the bonus granted for mortgaging the property'''
    super().__init__(board, position, name, type)

    self._price = price; self._mortgage = mortgage
    self._owner = None; self._is_mortgaged = False

  @property
  def owner(self) -> Optional[Player]:
    '''Owner of the property, or None if it is not owned.'''
    return self._owner
  @owner.setter
  def owner(self, newval: Player) -> None:
    self._owner = newval
  def price(self) -> int: return self._price
  def is_mortgaged(self) -> bool: return self._is_mortgaged
  def mortgage_bonus(self) -> int:
    '''Returns the amount to be earned from mortgaging the property.'''
    return self._mortgage
  def demortgage_fee(self) -> int:
    '''Returns the amount to be paid to demortgage the property.'''
    return int(self.mortgage_bonus() * const.MORTGAGE_INTEREST_RATE)
  def rent(self) -> int:
    '''Returns the rent to be charged when this tile is landed on, considering
    the current state of the board.'''
    raise NotImplementedError # to be implemented in subclass
  
  def land_on(self, player: Player, rent_multiplier: float = 1) -> None:
    '''Handles what happens when player lands on this tile. If the property is
    unowned, it prompts the player AI to buy it. Else, the player is charged 
    rent, unless they own the property. Optionally, rent_multiplier may be
    given, which has the base rent multiplied by the specified amount.

    Runs elimination logic if player goes bankrupt.
    
    Board-drawing: This function draws the board if the player is charged rent
    or buys the property.'''
    super().land_on(player)
    if self.owner is not None:
      if not self.is_mortgaged() and not player.owns(self):
        rent = int(rent_multiplier * self.rent())

        self.owner.entrust(rent) # type: ignore
        player.deduct(rent, self.owner)
        print(f'{player} has paid ${rent} to {self.owner}')
        self.board().draw()

    else: aitools.prompt_buy(player, self)

  def mortgage(self):
    '''Mortgages tile, granting its owner the tile's corresponding mortgage
    bonus, which is half its price by definition.
        
    Board-drawing: This function draws the board.'''
    assert self.owner is not None
    assert not self.is_mortgaged()
    self._is_mortgaged = True
    self.owner.entrust(self._mortgage) # type: ignore

    print(f'{self.owner} has mortgaged {self}')
    self.board().draw()
  
  def demortgage(self):
    '''Demortgages tile and deducts 110% of its mortgage fee from its owner.'''
    assert self.owner is not None
    assert self.is_mortgaged()
    self._is_mortgaged = False
    self.owner.deduct(int(self._mortgage * const.MORTGAGE_INTEREST_RATE)) # type: ignore

    self.board().draw()

  def reset(self) -> None:
    '''Resets property so that it may be claimed again. The previous owner
    gets no money from this operation.'''
    self._is_mortgaged = False
    self._owner = None

class Street(Property):
  _starting_rent: int
  _color_set_rents: list[int] # contains rent with color set and 0 houses, 1 houses, etc.
  _rent_with_hotel: int

  _house_cost: int;  _hotel_cost: int

  def __init__(self, board: Board, position: int, name: str, type: str,
    price: int, mortgage: int,

    color: str,

    rent: int, rentWithColorSet: int, rentWith1House: int,
    rentWith2Houses: int, rentWith3Houses: int, rentWith4Houses: int,
    rentWithHotel: int,

    houseCost: int, hotelCost: int
    ):
    '''See Property class for board, position, name, type, price, mortgage
     - color is the tile's color
     - rent is the rent charged by default
     - rentWithColorSet is rent charged when the color set is owned by one player
     - rentWith1House, rentWith2Houses, ...
     - rentWithHotel
     - houseCost and hotelCost are the amount to be paid to build'''
    
    super().__init__(board, position, name, type,
      price, mortgage)

    self._color = color

    self._starting_rent = rent
    self._color_set_rents = [rentWithColorSet] + [rentWith1House, rentWith2Houses,
      rentWith3Houses, rentWith4Houses]
    self._rent_with_hotel = rentWithHotel 

    self._house_cost = houseCost; self._hotel_cost = hotelCost 

    self._houses = 0 # amount of houses on property; 5 with hotel
    self._has_hotel = False
  
  @property
  def color(self) -> str: return self._color
  def color_set(self) -> set[Street]:
    '''Returns the set of streets on the board with the same color as this tile.'''
    return self.board().color_set(self._color)
  def houses(self):
    '''Returns the amount of houses currently on the tile.
    There are no houses on the tile if it has a hotel.'''
    return self._houses
  def has_hotel(self): return self._has_hotel

  def building_cost(self):
    '''Returns the cost of building a building on the tile, considering its
    current state.'''
    return self._hotel_cost if self.has_hotel() else self._house_cost
  
  def selling_bonus(self):
    '''Returns the amount earned from selling a building on this tile,
    considering its current state.
    It is half the building cost.'''
    return self.building_cost()//2

  def rent(self) -> int:
    if self.owner is None: return 0
    if self.is_mortgaged(): return 0
    if self.has_hotel(): return self._rent_with_hotel
    if self.owner.owns_color(self.color): # type: ignore
      return self._color_set_rents[self._houses] # where item i is rent with i houses
    else: return self._starting_rent

  def build(self):
    '''Builds a house on the tile; or an hotel, in case there are 4 houses.
    
    In order to build on a tile, its owner must have its color set.
    A new house cannot be built on a street until every other street in the
    color set either has an hotel or has at least the number of houses on the
    street you want to build on.

    A tile may not be built on if any of the streets in its color set is
    mortgaged.
    
    A tile may not be built on further after having built an hotel on it.
    
    Board-drawing: This function draws the board.'''

    assert self.owner is not None
    assert self.owner.owns_color(self.color) # type: ignore
    assert all(not property.is_mortgaged() for property in self.color_set())
    assert not self.has_hotel()
    assert all(property.houses() >= self.houses() or property.has_hotel() for property in self.color_set())
    assert self.owner.balance() >= self.building_cost() # type: ignore
    
    if self.houses() == 4:
      self._has_hotel = True
    self._houses += 1
    self.owner.deduct(self.building_cost()) # type: ignore
    self.board().draw()
    print(f'{self.owner} has built on {self}. The tile now has',
      'an hotel' if self.has_hotel() else (str(self._houses) + ' houses.'))

  def sell(self):
    '''Sells a single house (or hotel) on the tile for half its price,
    and entrusts the amount to its owner.

    A house cannot be sold unless the number of houses in each street in the
    color set is less than or equal to the number of houses on the street you
    want to sell on. An hotel may always be sold.
    
    Cannot sell if there are no houses on the tile.
    
    Board-drawing: This function draws the board.'''
    assert self.owner
    assert self.owner.owns_color(self.color) # type: ignore
    assert self.houses() > 0, 'No houses left to sell'
    assert all(
      property.houses() <= self.houses() for property in self.color_set() if not property.is_mortgaged()
    )
    if self._has_hotel:
      self._has_hotel = False
    self._houses -= 1
    self.owner.entrust(self.selling_bonus()) # type: ignore
    self.board().draw()
    print(f'{self.owner} has sold on {self}. The tile now has {self._houses} houses.')

  def mortgage(self):
    '''Mortgages tile, granting its owner the tile's corresponding mortgage
    bonus, which is half its price by definition. There must be no houses or
    hotels on any tile in the color set in order to be mortgaged.
    
    Board-drawing: This function draws the board.'''
    assert all(property.houses() == 0 for property in self.color_set())
    super().mortgage()

  def reset(self):
    '''Resets property so that it may be claimed again. Removes all houses and
    hotels. The previous owner gets no money from this operation.'''
    super().reset()
    self._houses = 0
    self._has_hotel = False

class Station(Property):
  _rents: list[int] # contains rent with 1 station, rent with 2 stations, etc...

  def __init__(self, board: Board, position: int, name: str, type: str,
    price: int, mortgage: int,

    rent: int, rentWith2Stations: int, rentWith3Stations: int,
    rentWith4Stations: int,
  ):
    '''See Property class for board, position, name, type, price, mortgage
     - rent is the rent to be charged with only one station owned
     - rentWith2Stations, rentWith3Stations, ...'''
    super().__init__(board, position, name, type, price, mortgage)
    
    self._rents = [
      0, rent, rentWith2Stations, rentWith3Stations, rentWith4Stations
    ]
    
    self._tile_type = 'station'
  
  def rent(self) -> int:
    if self.owner is None: return 0
    return self._rents[self.owner.station_count()] # type: ignore

class Utility(Property):
  '''Utility tile. Ownable tile. Player must own'''
  _default_multiplier: int
  _multiplier_with_both: int

  def __init__(self, board: Board, position: int, name: str, type: str,
    price: int, mortgage: int,

    rentMultiplier: int, rentMultiplierWithBoth: int, description: str
  ):
    '''See Property class for board, position, name, type, price, mortgage
     - rentMultiplier is the amount
     - rentWith2Stations, rentWith3Stations, ...
     - description is a description of the tile's actions.'''
    super().__init__(board, position, name, type, price, mortgage)

    self._default_multiplier = rentMultiplier
    self._multiplier_with_both = rentMultiplierWithBoth
      
  def rent(self) -> int:
    if self.owner is None: return 0

    self.board().throw_dice()
    return sum(self.board().dice()) * (
      self._default_multiplier if self.owner.utility_count() == 1 else self._multiplier_with_both # type: ignore
      )

TILE_TYPES: dict[str, type[Tile]] = {
  'property': Street,
  'station': Station,
  'utility': Utility,
  'chance': DeckTile,
  'community_chest': DeckTile,
  'tax': Tax
}

def build_tile(board: Board, **data: Any) -> Tile:
  '''Returns a tile of valid type. Preguntar a en jordi petit com és que s'especifica'''
  tile_type = TILE_TYPES.get(data['type'], Special)
  return tile_type(board, **data)