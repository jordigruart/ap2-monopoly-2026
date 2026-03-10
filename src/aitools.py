from tile import Street
from typing import Iterator

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