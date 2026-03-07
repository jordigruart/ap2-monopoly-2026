from __future__ import annotations
from typing import TYPE_CHECKING, Any
from tile import Street, Station, Utility, Property
import const
import aitools

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
  ):
    self._board = board
    self._name = name
    self._piece = piece
    self._color = color
    self._index = index 

    self._position = 0
    self._money = const.START_MONEY
    self._in_prison = False

    self._streets = set[Street]()
    self._stations = set[Station]()
    self._utilities = set[Utility]()

  def board(self) -> Board: return self._board
  def name(self) -> str: return self._name
  def piece(self) -> str: return self._piece
  def color(self) -> str: return self._color
  def index(self) -> int: return self._index

  def position(self) -> int: return self._position

  def balance(self) -> int: return self._money
  def owned_properties(self) -> set[Property]:
    return self._streets | self._stations | self._utilities # type: ignore

  def owns(self, property: Property) -> bool:
    '''Returns whether the player owns the specified property.'''
    return property.owner() == self
  
  def owns_color(self, color: str) -> bool:
    '''Returns whether the player owns every property in the specified color
    set.'''
    return all(self.owns(property) for property in self.board().color(color))

  def is_bankrupt(self) -> bool: return self._money < 0
  
  def get_out_of_jail_free_cards(self) -> int: return 0
  def turns_in_prison(self) -> int: return 0

  def can_play(self) -> bool: return True

  def station_count(self) -> int:
    '''Returns how many stations are currently in this player's posession.'''
    return len(self._stations)
  
  def utility_count(self) -> int:
    '''Returns how many utilities are currently in this player's posession.'''
    return len(self._utilities)

  def entrust(self, increment: int) -> None:
    '''Increments the player's balance by the specified amount.'''
    self._money += increment

  def deduct(self, decrement: int) -> int:
    '''Decrements the player's balance by the specified amount and returns the
    amount deducted.'''
    self._money -= decrement
    return decrement

  def move_forward(self, increment: int, go_bonus: bool = True) -> None:
    '''Moves player forward by the increment.
    
    If go_bonus is True, automatically applies the bonus given by passing the GO square if
    the resulting position passes the square'''
    self._position += increment
    if go_bonus and self._position >= 40:
      self._position %= 40
      self._money += const.GO_SALARY
      
  def move_backwards(self, decrement: int, go_bonus: bool = False) -> None:
    '''Moves player backwards by the decrement.
    
    If go_bonus is True, automatically applies the bonus given by passing the GO square.'''
    self._position -= decrement
    if go_bonus and self._position <= 0:
      self._position %= 40
      self._money += const.GO_SALARY

  def set_position(self, position: int, go_bonus: bool = False) -> None:
    '''Moves player to the specified position.
     
    If go_bonus is True, automatically applies the bonus given by passing the
    GO square if the destination is before the origin (as if the player had had
    to move forward to get there).'''
    if go_bonus and position <= self._position: self._money += const.GO_SALARY
    self._position = position
  
  def buy(self, property: Property):
    self.deduct(property.price())
    property.give_to(self)

    match property.tile_type():
      case 'property': self._streets.add(property)    # type: ignore
      case 'station': self._stations.add(property)    # type: ignore
      case 'utility': self._utilities.add(property)   # type: ignore
      case _: raise

    print(f'{self.name()} has bought {property.name()}')
  
  def prompt_buy(self, property: Property):
    '''Prompts a player to buy.'''
    if self.balance() >= const.UPPER_SPENDING_THRESHOLD: self.buy(property)
  
  def _selling_actions(self):
    '''Tries to go above spending threshold.'''
    # sell buildings
    for color in filter(self.owns_color, const.COLORS):
      color = self.board().color(color)

      for property in aitools.selling_order(color):
        property.sell()
        if self.balance() >= const.LOWER_SPENDING_THRESHOLD: return
    
    # if still critical, mortgage until not
    for property in self.owned_properties():
      property.mortgage()
      if self.balance() >= const.LOWER_SPENDING_THRESHOLD: return

  def _buying_actions(self):
    '''Tries to go below spending threshold.'''
    # demortgage first
    for property in filter(Property.is_mortgaged, self.owned_properties()):
      property.demortgage()
      if self.balance() < const.UPPER_SPENDING_THRESHOLD: return
    
    # if still can buy, buy until you cant
    for color in filter(self.owns_color, reversed(const.COLORS)):
      color = self.board().color(color)

      for property in aitools.buying_order(color):
        property.build()
        if self.balance() < const.LOWER_SPENDING_THRESHOLD: return

  def post_turn_actions(self):
    if self.balance() < const.LOWER_SPENDING_THRESHOLD:
      self._selling_actions()

    if self.balance() >= const.UPPER_SPENDING_THRESHOLD:
      self._buying_actions()

  def is_in_prison(self) -> bool: return self._in_prison

  def imprison(self) -> None: 
    '''Sends player to jail. Does not apply GO bonus.'''
    self.set_position(self._board.jail_position(), go_bonus = False)
    self._in_prison = True
    raise const.EndTurn

  def eliminate(self, creditor: Player) -> None:
    '''Eliminates self from play.'''
    # for now this goes to the bank and not to the player that is lost to
    for property in self.owned_properties(): property.reset()
    for attr in self._streets, self._stations, self._utilities: attr.clear()
    raise const.EndTurn

def build_player(board: Board, data: dict[str, Any], index: int) -> Player:
  """Build a Player from JSON-like dict with 'name', 'piece', and 'color' keys."""
  return Player(board, data["name"], data["piece"], data["color"], index)