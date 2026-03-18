from __future__ import annotations
from typing import TYPE_CHECKING, Any
import const
import aitools

if TYPE_CHECKING:
  from board import Board
  from tile import Tile, Street, Station, Utility, Property

class Player:
  _board: Board
  _name: str
  _piece: str
  _color: str
  _index: int 

  _position = 0
  _money: int

  _in_prison: bool
  _turns_in_prison: int
  _get_out_of_jail_free_cards: int
  _is_eliminated: bool

  _streets: set[Street]
  _stations: set[Station]
  _utilities: set[Utility]

  def __init__(
    self,
    board: Board,
    name: str,
    piece: str,
    color: str,
    index: int,
  ):
    self._board = board
    self._name = name
    self._piece = piece
    self._color = color
    self._index = index 

    self._position = 0
    self._money = const.START_MONEY

    self._in_prison = False
    self._turns_in_prison = 0
    self._get_out_of_jail_free_cards = 0
    self._is_eliminated = False

    self._streets = set()
    self._stations = set()
    self._utilities = set()

  def __str__(self) -> str: return self.name()

  def board(self) -> Board: return self._board
  def name(self) -> str: return self._name
  def piece(self) -> str: return self._piece
  def color(self) -> str: return self._color
  def index(self) -> int: return self._index

  def current_tile(self) -> Tile:
    '''Returns the tile the player is currently on; not the position.'''
    return self.board().tiles()[self.position()]


  def balance(self) -> int: return self._money
  def is_bankrupt(self) -> bool:
    '''Returns whether the player's balance is below zero.
    Different from Player.is_eliminated.'''
    return self._money < 0
  
  def is_eliminated(self) -> bool:
    '''Returns whether the elimination logic has been run on the player.
    Different from Player.is_bankrupt.'''
    return self._is_eliminated

  def position(self) -> int: return self._position

  def is_in_prison(self) -> bool: return self._in_prison
  def turns_in_prison(self) -> int: return self._turns_in_prison

  @property
  def get_out_of_jail_free_cards(self) -> int: return self._get_out_of_jail_free_cards

  @get_out_of_jail_free_cards.setter
  def get_out_of_jail_free_cards(self, new_val: int) -> None:
    self._get_out_of_jail_free_cards = new_val

  def imprison(self) -> None: 
    '''Sends player to jail. Ends turn prematurely by raising const.EndTurn,
    which is handled by board.play(). Does not apply GO bonus.
    
    Board-drawing: this function draws the board.'''
    print(f'{self} has gone to jail')

    self._in_prison = True
    self._turns_in_prison = 0
    self.set_position(self._board.jail_position(), go_bonus = False)
    raise const.EndTurn

  def free(self) -> None:
    '''Frees a player from jail, allowing them to play normally.
    
    Board-drawing: This function draws the board.'''
    print(f'{self} has been freed from jail')
    self._in_prison = False
    self._turns_in_prison = 0
    
    self.board().draw()

  def update_turns_in_prison(self):
    '''Updates count of turns spent in prison.
    If the player has spent three turns in prison, they are freed.
    
    Board-drawing: This function draws the board whenever the player is freed.'''
    if self.is_in_prison():
      self._turns_in_prison += 1
      if self.turns_in_prison() == 3: self.free()
  

  def station_count(self) -> int:
    '''Returns how many stations are currently in the player's posession.'''
    return len(self._stations)
  
  def utility_count(self) -> int:
    '''Returns how many utilities are currently in the player's posession.'''
    return len(self._utilities)
  
  def owned_properties(self) -> set[Property]:
    '''Returns the set of properties currently owned by the player.'''
    return self._streets | self._stations | self._utilities # type: ignore
  
  def owned_streets(self) -> set[Street]:
    '''Returns the set of streets currently owned by the player.'''
    return self._streets

  def owns(self, property: Property) -> bool:
    '''Returns whether the player owns the specified property.'''
    return property.owner() == self
  
  def owns_color(self, color: str) -> bool:
    '''Returns whether the player owns every property in the specified color
    set.'''
    return all(self.owns(property) for property in self.board().color_set(color))


  def entrust(self, increment: int) -> None:
    '''Increments the player's balance by the specified amount.'''
    self._money += increment

  def deduct(self, decrement: int, creditor: Player | None = None) -> None:
    '''Decrements the player's balance by the specified amount.
    creditor is the player that the amount has been paid to.
    
    Runs elimination logic if player has gone bankrupt..'''
    self._money -= decrement
    if self.is_bankrupt():
      self.eliminate(creditor)
      if self.board().current_player() == self: raise const.EndTurn
  

  def move_forward(self, increment: int, go_bonus: bool = True) -> None:
    '''Moves player forward by the increment.
    
    If go_bonus is True, automatically applies the bonus given by passing the GO square if
    the resulting position passes the square.
    
    Board-drawing: this function draws the board.'''
    self._position += increment
    if self._position >= 40:
      self._position %= 40
      if go_bonus: self._money += const.GO_SALARY

    self.board().draw()
      
  def move_backwards(self, decrement: int, go_bonus: bool = False) -> None:
    '''Moves player backwards by the decrement.
    
    If go_bonus is True, automatically applies the bonus given by passing the GO square
    
    Board-drawing: this function draws the board.'''
    self._position -= decrement
    if self._position <= 0:
      self._position %= 40
      if go_bonus: self._money += const.GO_SALARY
    
    self.board().draw()

  def set_position(self, position: int, go_bonus: bool = False) -> None:
    '''Moves player to the specified position.
     
    If go_bonus is True, automatically applies the bonus given by passing the
    GO square if the destination is before the origin (as if the player had had
    to move forward to get there).
    
    Board-drawing: this function draws the board.'''
    if go_bonus and position <= self._position: self._money += const.GO_SALARY
    self._position = position
  
    self.board().draw()
  

  def entrust_property(self, property: Property):
    '''Gives the specified property to this player. Changes all the internal
    variables that handle ownership, both in the player and in the tile.
    
    Board-drawing: this function draws the board.'''
    property.__setattr__('_owner', self)

    match property.tile_type():
      case 'property': self._streets.add(property)    # type: ignore
      case 'station': self._stations.add(property)    # type: ignore
      case 'utility': self._utilities.add(property)   # type: ignore
      case _: raise
    
    self.board().draw()

  def buy(self, property: Property):
    '''Buys a property.
    
    Board-drawing: this function draws the board.'''
    assert self.balance() >= property.price(), 'Insufficient funds'
    self.deduct(property.price())
    self.entrust_property(property)

    print(f'{self.name()} has bought {property.name()}')

  def recieve_property_from_elimination(self, property: Property):
    '''When a player is eliminated from play, they give all their mortgaged
    properties to the owner of the space that made them bankrupt. The reciever
    then must choose whether to repay the mortgage or keep it by paying 10% of
    the mortgage value.
    
    This function changes the property's owner and handles that choice.'''
    assert property.is_mortgaged()
    self.entrust_property(property)
    
    aitools.decide_keep_or_demortgage(self, property)

  def eliminate(self, creditor: Player | None) -> None:
    '''Eliminates self from play. Gives all GOOJF cards and all mortgaged
    properties to creditor and takes away the rest of their properties. If
    creditor is None, behavior is as if they werent eliminated by a player,
    and all properties are taken away.
    
    Board-drawing: This function draws the board for every mortgaged property
    given to the creditor, and once more after eliminating the player.'''
    for attr in self._utilities, self._streets, self._stations:
      while attr:
        property = attr.pop()
        if creditor and property.is_mortgaged() and not creditor.is_eliminated():
          creditor.recieve_property_from_elimination(property)
        else: property.reset()
    
    print(f'{self} has been eliminated by {creditor}')
    self._is_eliminated = True
    self.board().draw()

def build_player(board: Board, data: dict[str, Any], index: int) -> Player:
  """Build a Player from JSON-like dict with 'name', 'piece', and 'color' keys."""
  return Player(board, data["name"], data["piece"], data["color"], index)