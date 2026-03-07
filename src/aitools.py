from tile import Street
from typing import Iterator

def selling_order(color: set[Street]) -> Iterator[Street]:
  '''Returns a possible legal order in which buildings must be sold in a color
  set (according to the "sell evenly" rule).'''
  # asymptotically, this be faster using a priority queue but, since color
  # sets are small, it is not terribly inefficient
  while True:
    candidate = max(color, key = lambda property: property.houses())
    if candidate.houses() > 0: yield candidate
    else: return

def buying_order(color: set[Street]) -> Iterator[Street]:
  '''Returns a possible legal order in which to build buildings on a color set
  (according to the "build evenly" rule).'''
  while True:
    candidate = min(color, key = lambda property: property.houses())
    if candidate.houses() < 5: yield candidate
    else: return