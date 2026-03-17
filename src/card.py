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

  def __init__(self, board: Board, id: int, title: str, description: str, **kwargs: Any) -> None:
    self._board = board; self._id = id; self._title = title; self._description = description
    # ignore kwargs

  @property
  def id(self): return self._id
  @property
  def title(self): return self._title
  @property
  def description(self): return self._description

  def execute(self, player: Player) -> None: 
    '''Executes the action of the card, with player as the benefactor.'''
    raise NotImplementedError

# movement related
class GoToPosition(Card):
  '''Advances to a certain position. Collects GO bonus.'''
  _position: int
  def __init__(self, position: int, **kwargs: Any) -> None:
    super().__init__(**kwargs)
    self._position = position
  def execute(self, player: Player) -> None: player.set_position(self._position, True)

class MoveToNearest(Card):
  '''Advances to nearest instance of a certain tile type. The tile is landed on
  normally, but a multiplier (rentMultiplier) is applied to the rent charged.
  Base class for MoveToNearestStation and MoveToNearestUtility.'''
  _rentMultiplier: int
  def __init__(self, rentMultiplier: int, **kwargs: Any) -> None:
    super().__init__(**kwargs)
    self._rentMultiplier = rentMultiplier

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
  def __init__(self, **kwargs: Any) -> None: super().__init__(**kwargs)
  def _nearest_position(self, player: Player) -> int:
    if 5 <= player.position() < 15: return 15
    elif 15 <= player.position() < 25: return 25
    elif 25 <= player.position() < 35: return 35
    else: return 5

class MoveToNearestUtility(MoveToNearest):
  def __init__(self, **kwargs: Any) -> None: super().__init__(**kwargs)
  def _nearest_position(self, player: Player) -> int: return 28 if 12 <= player.position() < 28 else 12

class MoveBackSpaces(Card):
  '''Moves player back the given number of spaces. spaces is the '''
  _spaces: int
  def __init__(self, spaces: int, **kwargs: Any) -> None:
    super().__init__(**kwargs)
    self._spaces = spaces
  def execute(self, player: Player) -> None: player.move_backwards(self._spaces, False)

# jail related
class GoToJail(Card):
  def __init__(self, **kwargs: Any) -> None: super().__init__(**kwargs)
  def execute(self, player: Player) -> None:
    player.imprison()

class GetOutOfJailFreeCard(Card):
  def __init__(self, **kwargs: Any) -> None: super().__init__(**kwargs)
  def execute(self, player: Player) -> None:
    player.get_out_of_jail_free_cards += 1
  
# money related
class CollectMoney(Card):
  _amount: int
  def __init__(self, amount: int, **kwargs: Any) -> None:
    super().__init__(**kwargs)
    self._amount = amount
  def execute(self, player: Player) -> None:
    player.entrust(self._amount)

class CollectFromPlayers(Card):
  _amountPerPlayer: int
  def __init__(self, amountPerPlayer: int, **kwargs: Any) -> None:
    super().__init__(**kwargs)
    self._amountPerPlayer = amountPerPlayer
  
  def execute(self, player: Player) -> None:
    for debtor in self._board.active_players():
      player.entrust(debtor.deduct(self._amountPerPlayer))
      if debtor.is_bankrupt(): debtor.eliminate(player)
  
class PayMoney(Card):
  _amount: int
  def __init__(self, amount: int, **kwargs: Any) -> None:
    super().__init__(**kwargs)
    self._amount = amount

  def execute(self, player: Player) -> None:
    player.deduct(self._amount)

    if player.is_bankrupt(): 
      player.eliminate(None)
      raise const.EndTurn 

class PayEachPlayer(Card):
  _amountPerPlayer: int
  def __init__(self, amountPerPlayer: int, **kwargs: Any) -> None:
    super().__init__(**kwargs)
    self._amountPerPlayer = amountPerPlayer
  
  def execute(self, player: Player) -> None:
    for creditor in filter(lambda player: not player.is_bankrupt(), self._board.players()):
      creditor.entrust(player.deduct(self._amountPerPlayer))

    if player.is_bankrupt(): 
      player.eliminate(None)
      raise const.EndTurn 

class PayPerProperty(Card):
  _amountPerHouse: int
  _amountPerHotel: int
  def __init__(self, amountPerHouse: int, amountPerHotel: int, **kwargs: Any) -> None:
    super().__init__(**kwargs)
    self._amountPerHotel = amountPerHotel
    self._amountPerHouse = amountPerHouse
  
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
    case 'move_to_position': card_type = GoToPosition
    case 'move_to_nearest_station': card_type = MoveToNearestStation
    case 'move_to_nearest_utility': card_type = MoveToNearestUtility
    case 'collect_money': card_type = CollectMoney
    case 'get_out_of_jail_card': card_type = GetOutOfJailFreeCard
    case 'move_back_spaces': card_type = MoveBackSpaces
    case 'go_to_jail': card_type = GoToJail
    case 'pay_per_property': card_type = PayPerProperty
    case 'pay_money': card_type = PayMoney
    case 'pay_each_player': card_type = PayEachPlayer
    case 'collect_from_players': card_type = CollectFromPlayers
    case _: card_type = Card
  
  return card_type(**data, board = board)