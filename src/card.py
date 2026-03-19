from __future__ import annotations

from typing import Any, TYPE_CHECKING
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

  def __init__(self, board: Board, id: int, title: str, description: str) -> None:
    '''Initializes constants shared by all cards.
    - board is the board the card belongs to
    - id is a unique identifier for the card
    - title is the card name
    - description is a description of the card's behavior'''
    self._board = board; self._id = id; self._title = title; self._description = description

  @property
  def id(self): return self._id
  @property
  def title(self): return self._title
  @property
  def description(self): return self._description

  def execute(self, player: Player) -> None: 
    '''Executes the action of the card, with player as the benefactor.
    
    Board-drawing: this function draws the board.'''
    raise NotImplementedError

# movement related
class GoToPosition(Card):
  '''Advances to a certain position and lands on tile.
  Collects GO bonus.'''
  _position: int

  def __init__(self, board: Board, id: int, title: str, description: str,
               position: int) -> None:
    '''See Card.__init__ for board, id, title, description, ...
    - position is the position the player must go to when the tile is landed on'''
    super().__init__(board, id, title, description)
    self._position = position

  def execute(self, player: Player) -> None:
    tile = self._board.tiles()[self._position]
    player.set_position(self._position, True)

    tile.land_on(player)
  
class MoveToNearest(Card):
  '''Advances to nearest instance of a certain tile type. The tile is landed on
  normally, but a multiplier (rentMultiplier) is applied to the rent charged.
  Base class for MoveToNearestStation and MoveToNearestUtility.'''
  _rentMultiplier: int

  def __init__(self, board: Board, id: int, title: str, description: str,
               rentMultiplier: int) -> None:
    '''See Card.__init__ for board, id, title, description, ...
    - rentMultiplier is the amount the destination's usual rent is multiplied by.'''
    super().__init__(board, id, title, description)
    self._rentMultiplier = rentMultiplier

  def _nearest_position(self, player: Player) -> int:
    '''Based on the current position of player, determines the position they
    should land on.'''
    raise NotImplementedError
  
  def execute(self, player: Player) -> None:
    position = self._nearest_position(player)
    player.set_position(position, True)

    tile = self._board.tiles()[position]
    assert isinstance(tile, Property)
    tile.land_on(player, self._rentMultiplier)

class MoveToNearestStation(MoveToNearest):
  def _nearest_position(self, player: Player) -> int:
    if 5 <= player.position() < 15: return 15
    elif 15 <= player.position() < 25: return 25
    elif 25 <= player.position() < 35: return 35
    else: return 5

class MoveToNearestUtility(MoveToNearest):
  def _nearest_position(self, player: Player) -> int: return 28 if 12 <= player.position() < 28 else 12

class MoveBackSpaces(Card):
  '''Moves player back the given number of spaces.'''
  _spaces: int
  def __init__(self, board: Board, id: int, title: str, description: str,
               spaces: int) -> None:
    super().__init__(board, id, title, description)
    self._spaces = spaces

  def execute(self, player: Player) -> None:
    player.move_backwards(self._spaces, False)

    tile = self._board.tiles()[player.position()]
    tile.land_on(player)

# jail related
class GoToJail(Card):
  def execute(self, player: Player) -> None:
    player.imprison()

class GetOutOfJailFreeCard(Card):
  def execute(self, player: Player) -> None:
    player.get_out_of_jail_free_cards += 1
    self._board.draw()
  
# money related
class CollectMoney(Card):
  '''Entrusts player a certain amount.'''
  _amount: int
  def __init__(self, board: Board, id: int, title: str, description: str,
               amount: int) -> None:
    '''See Card.__init__ for board, id, title, description
    - amount is the amount of money collected'''
    super().__init__(board, id, title, description)
    self._amount = amount
  
  def execute(self, player: Player) -> None:
    player.entrust(self._amount)
    self._board.draw()

class CollectFromPlayers(Card):
  _amountPerPlayer: int
  def __init__(self, board: Board, id: int, title: str, description: str,
               amountPerPlayer: int) -> None:
    '''See Card.__init__ for board, id, title, description
    - amount is the amount of money collected per player'''
    super().__init__(board, id, title, description)
    self._amountPerPlayer = amountPerPlayer
  
  def execute(self, player: Player) -> None:
    for debtor in self._board.active_players():
      player.entrust(self._amountPerPlayer)
      debtor.deduct(self._amountPerPlayer)

    self._board.draw()
  
class PayMoney(Card):
  _amount: int
  def __init__(self, board: Board, id: int, title: str, description: str,
               amount: int) -> None:
    '''See Card.__init__ for board, id, title, description
    - amount is the amount of money paid.'''
    super().__init__(board, id, title, description)
    self._amount = amount

  def execute(self, player: Player) -> None:
    player.deduct(self._amount)
    self._board.draw()

class PayEachPlayer(Card):
  _amountPerPlayer: int
  def __init__(self, board: Board, id: int, title: str, description: str,
               amountPerPlayer: int, **kwargs: Any) -> None:
    '''See Card.__init__ for board, id, title, description
    - amount is the amount of money paid to each player.'''
    super().__init__(board, id, title, description)
    self._amountPerPlayer = amountPerPlayer
  
  def execute(self, player: Player) -> None:
    for creditor in self._board.active_players(): creditor.entrust(self._amountPerPlayer)
    player.deduct(len(self._board.active_players()) * self._amountPerPlayer)
    # this is done this way so that every player can be paid
    # if a deduction were to be done after each payment, some players could end
    # up not being paid because the player might have gone bankrupt

    # note how player is given the amount in the first line as well
    # but it is then deducted in the second line
    self._board.draw()

class PayPerProperty(Card):
  '''Deducts a sum calculated from the amount of properties owned by a player.'''
  _amount_per_house: int
  _amount_per_hotel: int
  def __init__(self, board: Board, id: int, title: str, description: str,
    amountPerHouse: int, amountPerHotel: int) -> None:
    '''See Card.__init__ for board, id, title, description
    - amountPerHotel, amountPerHouse is the amount paid for each house or hotel.'''
    super().__init__(board, id, title, description)
    self._amount_per_hotel = amountPerHotel
    self._amount_per_house = amountPerHouse
  
  def execute(self, player: Player) -> None:
    house_count = sum(min(4, property.houses()) for property in player.owned_streets())
    # compared with 4 because, internally, properties with hotels have 5 houses
    hotel_count = sum(property.has_hotel() for property in player.owned_streets())
    player.deduct(self._amount_per_house * house_count + self._amount_per_hotel * hotel_count)
    self._board.draw()

CARD_TYPES: dict[str, type[Card]] = {
  'move_to_position': GoToPosition,
  'move_to_nearest_station': MoveToNearestStation,
  'move_to_nearest_utility': MoveToNearestUtility,
  'collect_money': CollectMoney,
  'get_out_of_jail_card': GetOutOfJailFreeCard,
  'move_back_spaces': MoveBackSpaces,
  'go_to_jail': GoToJail,
  'pay_per_property': PayPerProperty,
  'pay_money': PayMoney,
  'pay_each_player': PayEachPlayer,
  'collect_from_players': CollectFromPlayers
}

def build_card(board: Board, action: str, **data: Any) -> Card:
  '''Builds a card from JSON-like dictionary for kwargs (data).'''
  card_type = CARD_TYPES.get(action, Card)
  return card_type(**data, board = board)