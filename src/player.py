from __future__ import annotations
from typing import TYPE_CHECKING, Any
from tile import Property
import const

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
  
  def imprison(self) -> None: 
    '''Sends player to jail. Does not apply GO bonus.'''
    self.set_position(self._board.jail_position(), False)
  
  def can_play(self) -> bool: return True

def build_player(board: Board, data: dict[str, Any], index: int) -> Player:
  """Build a Player from JSON-like dict with 'name', 'piece', and 'color' keys."""
  return Player(board, data["name"], data["piece"], data["color"], index)