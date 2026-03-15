from __future__ import annotations

from typing import Any, TYPE_CHECKING
import const
from tile import Property

if TYPE_CHECKING:
  from player import Player
  from board import Board

class Card:
  '''Base class for all cards.'''
  _id: int
  _title: str
  _description: str
  _board: Board

  def __init__(self, board: Board, **kwargs: Any) -> None:
    self._board = board
    for k in kwargs: self.__setattr__('_'+k, kwargs[k])

  def execute(self, player: Player) -> None: 
    '''Executes the action of the card.'''
    raise NotImplementedError

# movement related
class GoToPosition(Card):
  '''Advances to a certain position. Collects GO bonus.'''
  _position: int
  def __init__(self, board: Board, **kwargs: Any) -> None: super().__init__(board, **kwargs)
  def execute(self, player: Player) -> None: player.set_position(self._position, True)

class MoveToNearest(Card):
  '''Advances to nearest instance of a certain tile type. The tile is landed on
  normally, but a multiplier (rentMultiplier) is applied to the rent charged.
  Base class for MoveToNearestStation and MoveToNearestUtility.'''
  _rentMultiplier: int
  def __init__(self, board: Board, **kwargs: Any) -> None: super().__init__(board, **kwargs)

  def _nearest_position(self, player: Player) -> int:
    '''Based on the current position of player, determines the position they
    should land on. To be implemented in subclass.'''
    raise NotImplementedError
  
  def execute(self, player: Player) -> None:
    position = self._nearest_position(player)
    player.set_position(position, True)

    tile = self._board.tiles()[position]
    assert isinstance(tile, Property)
    tile.land_on(player, self._rentMultiplier)

class MoveToNearestStation(MoveToNearest):
  _rentMultiplier: int
  def __init__(self, board: Board, **kwargs: Any) -> None: super().__init__(board, **kwargs)
  def _nearest_position(self, player: Player) -> int:
    if 5 >= player.position() > 15: return 15
    elif 15 >= player.position() > 25: return 30
    elif 25 >= player.position() > 35: return 35
    else: return 5

class MoveToNearestUtility(MoveToNearest):
  _rentMultiplier: int
  def __init__(self, board: Board, **kwargs: Any) -> None: super().__init__(board, **kwargs)
  def _nearest_position(self, player: Player) -> int: return 28 if 12 >= player.position() > 28 else 12

class MoveBackSpaces(Card):
  '''Moves player back the given number of spaces. spaces is the '''
  _spaces: int
  def __init__(self, board: Board, **kwargs: Any) -> None: super().__init__(board, **kwargs)
  def execute(self, player: Player) -> None: player.move_backwards(self._spaces, False)

# jail related
class GoToJail(Card):
  _position: int
  def __init__(self, board: Board, **kwargs: Any) -> None: super().__init__(board, **kwargs)
  def execute(self, player: Player) -> None:
    player.imprison()

class GetOutOfJailFreeCard(Card):
  _keep_card: bool
  def __init__(self, board: Board, **kwargs: Any) -> None: super().__init__(board, **kwargs)
  def execute(self, player: Player) -> None:
    player.get_out_of_jail_free_cards += 1
  
# money related
class CollectMoney(Card):
  _amount: int
  def __init__(self, board: Board, **kwargs: Any) -> None: super().__init__(board, **kwargs)
  def execute(self, player: Player) -> None:
    player.entrust(self._amount)

class CollectFromPlayers(Card):
  _amountPerPlayer: int
  def __init__(self, board: Board, **kwargs: Any) -> None: super().__init__(board, **kwargs)
  def execute(self, player: Player) -> None:
    for debtor in filter(lambda player: not player.is_bankrupt(), self._board.players()):
      player.entrust(debtor.deduct(self._amountPerPlayer))
      if debtor.is_bankrupt(): debtor.eliminate(player)
  
class PayMoney(Card):
  _amount: int
  def __init__(self, board: Board, **kwargs: Any) -> None: super().__init__(board, **kwargs)
  def execute(self, player: Player) -> None:
    player.deduct(self._amount)

    if player.is_bankrupt(): 
      player.eliminate(None)
      raise const.EndTurn 

class PayEachPlayer(Card):
  _amountPerPlayer: int
  def __init__(self, board: Board, **kwargs: Any) -> None: super().__init__(board, **kwargs)
  def execute(self, player: Player) -> None:
    for creditor in filter(lambda player: not player.is_bankrupt(), self._board.players()):
      creditor.entrust(player.deduct(self._amountPerPlayer))

    if player.is_bankrupt(): 
      player.eliminate(None)
      raise const.EndTurn 

class PayPerProperty(Card):
  _amountPerHouse: int
  _amountPerHotel: int
  def __init__(self, board: Board, **kwargs: Any) -> None: super().__init__(board, **kwargs)
  def execute(self, player: Player) -> None:
    house_count = sum(property.houses() for property in player.owned_streets())
    hotel_count = sum(property.has_hotel() for property in player.owned_streets())
    player.deduct(self._amountPerHouse * house_count)
    player.deduct(self._amountPerHotel * hotel_count)

    if player.is_bankrupt(): 
      player.eliminate(None)
      raise const.EndTurn 

def build_card(board: Board, data: dict[str, Any]) -> Card:
  match data['action']:
    case 'move_to_position': return GoToPosition(board, **data)
    case 'move_to_nearest_station': return MoveToNearestStation(board, **data)
    case 'move_to_nearest_utility': return MoveToNearestUtility(board, **data)
    case 'collect_money': return CollectMoney(board, **data)
    case 'get_out_of_jail_card': return GetOutOfJailFreeCard(board, **data)
    case 'move_back_spaces': return MoveBackSpaces(board, **data)
    case 'go_to_jail': return GoToJail(board, **data)
    case 'pay_per_property': return PayPerProperty(board, **data)
    case 'pay_money': return PayMoney(board, **data)
    case 'pay_each_player': return PayEachPlayer(board, **data)
    case 'collect_from_players': return CollectFromPlayers(board, **data)
    case _: raise KeyError(data['action'])