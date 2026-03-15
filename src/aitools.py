from __future__ import annotations

from typing import TYPE_CHECKING
from tile import Property
from tile import Street
from typing import Iterator
import const
if TYPE_CHECKING: from player import Player

def selling_order(color: set[Street]) -> Iterator[Street]:
  '''Returns a possible legal order in which buildings must be sold in a color
  set (according to the "sell evenly" rule).'''
  # asymptotically, this (O(n^2) is slower than using a priority queue (O(n log n))
  # color sets, however, are small
  # so this is not terribly inefficient
  while True:
    candidate = max(color, key = lambda property: property.houses())
    if candidate.houses() > 0: yield candidate
    else: return

def building_order(color: set[Street]) -> Iterator[Street]:
  '''Returns a possible legal order in which to build buildings on a color set
  (according to the "build evenly" rule).'''
  while True:
    candidate = min(color, key = lambda property: property.houses())
    if not candidate.has_hotel(): yield candidate
    else: return

def post_turn_actions(player: Player):
  '''Tries to go above lower spending threshold.
  
  Board-drawing: this function draws the board for every change to the board.'''
  if player.balance() < const.SPENDING_THRESHOLD:
    _run_selling_actions(player)
  else: _run_buying_actions(player)

def _run_selling_actions(player: Player):
  '''Tries to go above lower spending threshold.
  
  Board-drawing: this function draws the board for every property mortgaged
  and every building sold.'''
  # sell buildings
  for color in filter(player.owns_color, const.COLORS):
    color = player.board().color_set(color)
    for property in selling_order(color):
      property.sell()
      if player.balance() >= const.SPENDING_THRESHOLD: return
  
  # if still critical, mortgage until not
  for property in player.owned_properties():
    if not property.is_mortgaged(): property.mortgage()
    if player.balance() >= const.SPENDING_THRESHOLD: return

def _run_buying_actions(player: Player):
  '''Tries to go below upper spending threshold.
  
  Board-drawing: this function draws the board for every property demortgaged
  and every building built.'''
  # we shall try demortgaging first
  for property in filter(Property.is_mortgaged, player.owned_properties()):
    if player.balance() >= property.demortgage_fee(): property.demortgage()
    if player.balance() < const.SPENDING_THRESHOLD: return

  # if we can still spend, ai shall try to build
  for color in filter(player.owns_color, const.COLORS):
    color_set = player.board().color_set(color)
    for property in building_order(color_set):
      if player.balance() >= property.building_cost(): property.build()
      if player.balance() < const.SPENDING_THRESHOLD: return

def decide_keep_or_demortgage(player: Player, property: Property):
  '''When a mortgaged property is recieved after elimination, the player must either remove the mortgage or keep it by paying a 10% of the mortgage.
  The AI demortgages the property if the player is above the spending threshold and has the money, and keeps it otherwise.'''
  if player.balance() >= max(property.demortgage_fee(), const.SPENDING_THRESHOLD): # demortgage
    property.demortgage()
  
  else: # keep
    player.deduct(int(.1 * property.mortgage_bonus()))

def prompt_buy(player: Player, property: Property):
  '''Prompts a player to buy a property.'''
  if player.balance() >= max(const.SPENDING_THRESHOLD, property.price()):
    player.buy(property)

def prompt_use_goojfc(player: Player) -> None:
  '''Prompts player to use a get out of jail free card.'''
  if player.get_out_of_jail_free_cards() > 0:
    player.free()
    player._get_out_of_jail_free_cards -= 1