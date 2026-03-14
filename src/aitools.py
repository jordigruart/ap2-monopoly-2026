from tile import Street, Property
from typing import Iterator
from player import Player
import const

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

def buying_order(color: set[Street]) -> Iterator[Street]:
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
  properties = filter(Property.is_mortgaged, player.owned_properties())
  
  property = next(properties, None)
  while player.balance() >= const.SPENDING_THRESHOLD and property:
    if player.balance() >= property.demortgage_fee(): property.demortgage()
    property = next(properties, None)

  #do this better
  colors = filter(player.owns_color, const.COLORS)
  color_sets = (player.board().color_set(color) for color in colors)

  for color_set in color_sets:
    order = buying_order(color_set)

    property = next(order)
    while player.balance() >= const.SPENDING_THRESHOLD and property:
      if player.balance() >= property.building_cost(): property.build()
      property = next(order)