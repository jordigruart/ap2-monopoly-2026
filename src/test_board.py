import pytest

from tile import *

from board import DebugBoard
import const

def test_buy():
  board = DebugBoard(
    die_inputs = iter([(3, 0)]),
    cards = []
  )
  
  board.play()

  jordi = board.players()[0]
  whitechapel_road = board.tiles()[3]

  assert whitechapel_road in jordi.owned_properties()
  
  assert isinstance(whitechapel_road, Street) # for type checking
  assert jordi.balance() == const.START_MONEY - whitechapel_road.price()

def test_rent_charged():
  board = DebugBoard(
    die_inputs = [(3, 0), (3, 0)],
  )

  board.play()
  
  jordi = board.players()[0]
  mireia = board.players()[1]
  whitechapel_road = board.tiles()[3]

  assert isinstance(whitechapel_road, Street) # for type checking

  assert whitechapel_road not in mireia.owned_properties()

  assert jordi.balance() == (
    const.START_MONEY - whitechapel_road.price() + getattr(whitechapel_road, '_starting_rent')
  )

  assert mireia.balance() == (
    const.START_MONEY - getattr(whitechapel_road, '_starting_rent')
  )

def test_color_set():
  board = DebugBoard(
    die_inputs = [(1, 0), (-1, 1), (-1, 1), (-1, 1),
    (2, 0), (3, 0)],
  )

  board.play()

  jordi = board.players()[0]
  mireia = board.players()[1]

  old_kent_road = board.tiles()[1]
  whitechapel_road = board.tiles()[3]

  assert isinstance(old_kent_road, Street) # for type checking
  assert isinstance(whitechapel_road, Street)

  assert old_kent_road, whitechapel_road in jordi.owned_properties()
  assert jordi.owns_color('brown')

  assert jordi.balance() == (
    const.START_MONEY
    - old_kent_road.price() - whitechapel_road.price()
    + getattr(whitechapel_road, '_rent_with_color_set')
  )
  assert mireia.balance() == (
    const.START_MONEY - getattr(whitechapel_road, '_rent_with_color_set')
  )

def station_rent():
  board = DebugBoard(
    die_inputs = [(5, 0), (5, 0), (-1, 1), (-1, 1),
    (10, 0), (0, 0), (5, 0), (-1, 1)]
  )
  jordi = board.players()[0]
  mireia = board.players()[1]
  arnau = board.players()[2]
  marta = board.players()[3]

  kings_cross_station = board.tiles()[5]
  marylebone_station = board.tiles()[15]
  fenchurch_st_station = board.tiles()[25]
  liverpool_station = board.tiles()[35]

  # ---------------------------------------------------------
  board.run(4)

  assert isinstance(kings_cross_station, Station) # for type checking

  assert jordi.station_count() == 1
  assert jordi.balance() == (
    const.START_MONEY - kings_cross_station.price() + getattr(kings_cross_station, '_starting_rent')
  )
  assert mireia.balance() == (
    const.START_MONEY - getattr(kings_cross_station, '_starting_rent')
  )

  # ---------------------------------------------------------
  board.run(4)

  assert isinstance(marylebone_station, Station) # for type checking

  assert jordi.station_count() == 2
  assert jordi.balance() == (
    const.START_MONEY
    - kings_cross_station.price() - marylebone_station.price()
    + getattr(kings_cross_station, '_starting_rent')
    + getattr(kings_cross_station, '_rent_with_2_stations')
  )
  assert arnau.balance() == (
    const.START_MONEY - getattr(kings_cross_station, '_rent_with_2_stations')
  )

def test_three_doubles():
  board = DebugBoard(
    die_inputs = [(1, 1), (1, 1), (1, 1)]
  )

  board.play()

  jordi = board.players()[0]
  assert jordi.is_in_prison()