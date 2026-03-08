import pytest

from player import Player
from tile import *

from board import DebugBoard
import const

def test_tax():
  board = DebugBoard(
    die_inputs = [(4, 0)]
  )

  board.play()

  jordi = board.players()[0]
  tax = board.tiles()[4]

  assert jordi.balance() == const.START_MONEY - getattr(tax, '_amount')

def test_buy():
  board = DebugBoard(
    die_inputs = [(3, 0)],
  )
  
  board.play()

  jordi = board.players()[0]
  whitechapel_road = board.tiles()[3]

  assert whitechapel_road in jordi.owned_properties()
  
  assert isinstance(whitechapel_road, Street) # for type checking
  assert jordi.balance() == const.START_MONEY - whitechapel_road.price()

def test_rent_charged():
  board = DebugBoard(
    die_inputs = [(3, 0), (3, 0)]
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
    die_inputs = [(-1, 1), (2, 1)]
  )

  board.run(1)

  jordi = board.players()[0]
  old_kent, tmp, whitechapel = board.tiles()[1:4]
  
  for property in old_kent, whitechapel: jordi.buy(property)
  
  assert isinstance(old_kent, Street) # for type checking
  assert isinstance(whitechapel, Street)

  mireia = board.players()[1]
  assert jordi.owns_color('brown')

  board.run(1)

  assert jordi.balance() == (
    const.START_MONEY
    - getattr(old_kent, '_price')
    - getattr(whitechapel, '_price')
    + getattr(whitechapel, '_rent_with_color_set')
  )
  assert mireia.balance() == (
    const.START_MONEY - getattr(whitechapel, '_rent_with_color_set')
  )

def test_station_rent():
  board = DebugBoard(
    die_inputs = [(5, 0), (5, 0), (-1, 1), (-1, 1),
    (10, 0), (1, 0), (5, 0), (-1, 1)]
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
    const.START_MONEY - kings_cross_station.price()
    + getattr(kings_cross_station, '_starting_rent')
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

def test_doubles():
  board = DebugBoard(
    [(1, 1), (1, 2)]
  )

  board.play()

  jordi = board.players()[0]
  mireia = board.players()[1]

  assert jordi.position() == 5
  assert board.current_player() == mireia

def test_three_doubles():
  board = DebugBoard(
    die_inputs = [(1, 1), (1, 1), (1, 1)]
  )

  board.play()

  jordi = board.players()[0]
  assert jordi.is_in_prison()

def test_go_bonus():
  board = DebugBoard(
    die_inputs = [(40, 0)]
  )

  board.play()

  jordi = board.players()[0]
  assert jordi.balance() == const.START_MONEY + const.GO_SALARY

def test_buying_orderly():
  board = DebugBoard(
    die_inputs = [(-1, 1)]
  )

  board.play()

  jordi = board.players()[0]
  for property in board.color('green'): jordi.buy(property)

  regent, oxford, tmp, bond = board.tiles()[31:35]
  assert isinstance(regent, Street)
  assert isinstance(oxford, Street)
  assert isinstance(bond, Street)

  regent.build(); bond.build(); oxford.build(); oxford.build()
  bond.build(); regent.build(); bond.build(); oxford.build()

def test_building_twice_in_a_row():
  with pytest.raises(AssertionError):
    board = DebugBoard(
      die_inputs = [(-1, 1)]
    )

    board.play()

    jordi = board.players()[0]
    for property in board.color('green'): property.set_owner(jordi)

    regent = board.tiles()[31]
    assert isinstance(regent, Street)

    for _ in range(2): regent.build()

def test_ai_builds_properly_from_zero():
  '''Tests whether the player AI knows how to build from 0 houses on a set to
  three hotels granted unlimited funds.'''
  board = DebugBoard(
    die_inputs = [(-1, 1)]
  )

  jordi = board.players()[0]
  for property in board.color('green'): property.set_owner(jordi)

  jordi.entrust(100000)

  board.play()
  assert all(property.has_hotel() for property in board.color('green'))

def test_ai_builds_properly_from_a_start():
  board = DebugBoard(
    die_inputs = [(5, 5), (-1, 1)]
  )
  board.run(1)

  jordi = board.players()[0]
  jordi.entrust(100000)

  for property in board.color('green'): jordi.buy(property)

  regent, oxford, tmp, bond = board.tiles()[31:35]
  assert isinstance(regent, Street)
  assert isinstance(oxford, Street)
  assert isinstance(bond, Street)

  regent.build(); oxford.build()

  board.play()
  assert all(property.has_hotel() for property in board.color('green'))