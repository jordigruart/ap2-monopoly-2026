import pytest
from typing import TYPE_CHECKING

if TYPE_CHECKING: from tile import Street, Utility

import const
from board import DebugBoard

def test_tax():
  '''Tests that landing on a tax tile charges the player the corresponding amount.'''
  board = DebugBoard(
    die_inputs = [(4, 0)]
  )
  jordi = board.players()[0]
  tax = board.tiles()[4]

  board.play()
  assert jordi.balance() == const.START_MONEY - getattr(tax, '_amount')

def test_street_buy() -> DebugBoard:
  board = DebugBoard(
    die_inputs = [(3, 0), (3, 0), (3, 0)]
  )
  jordi = board.players()[0]
  whitechapel_road: Street = board.tiles()[3]

  board.run(1)
  assert whitechapel_road in jordi.owned_properties()
  assert jordi.balance() == const.START_MONEY - whitechapel_road.price()

  return board

def test_street_rent_default():
  '''Tests that default rent (no color set or buildings) is charged properly
  on a street.'''
  board = test_street_buy()
  jordi, mireia = board.players()[:2]
  whitechapel_road: Street = board.tiles()[3]

  board.run(1)
  # mireia has landed on whitechapel, but she should not own it, as jordi already does
  assert whitechapel_road not in mireia.owned_properties()
  # aditionally, rent should have been charged and paid to jordi
  assert jordi.balance() == (
    const.START_MONEY - whitechapel_road.price() + getattr(whitechapel_road, '_starting_rent')
  )
  assert mireia.balance() == (
    const.START_MONEY - getattr(whitechapel_road, '_starting_rent')
  )  

def test_street_rent_mortgage() -> DebugBoard:
  '''Tests that rent is not charged on a mortgaged property.'''
  board = test_street_buy()
  mireia = board.players()[1]
  whitechapel: Street = board.tiles()[3]

  whitechapel.mortgage()
  board.run(1) # mireia lands on whitehchapel; should not have been charged any rent because it is mortgaged
  assert mireia.balance() == const.START_MONEY

  return board

def test_street_rent_demortgage():
  '''Tests that rent is charged on a previously mortgaged property after being demortgaged.'''
  board = test_street_rent_mortgage()
  arnau = board.players()[2]
  whitechapel: Street = board.tiles()[3]

  whitechapel.demortgage()
  board.run(1) # arnau lands on whitehchapel; should be charged rent as it has been demortgaged
  assert arnau.balance() == const.START_MONEY - getattr(whitechapel, '_starting_rent')

def test_rent_street_color_set() -> DebugBoard:
  '''Tests that rent is charged properly on a street when its whole color
  set is in one player's posession.'''
  board = DebugBoard(
    die_inputs = [(-1, 1), (2, 1), (2, 1)]
  )
  jordi, mireia = board.players()[:2]
  old_kent: Street; whitechapel: Street
  old_kent, tmp, whitechapel = board.tiles()[1:4]

  board.run(1)
  for property in old_kent, whitechapel: jordi.buy(property)

  assert jordi.owns_color('brown')

  board.run(1)
  # mireia lands on whitechapel
  assert jordi.balance() == (
    const.START_MONEY
    - getattr(old_kent, '_price')
    - getattr(whitechapel, '_price')
    + getattr(whitechapel, '_color_set_rents')[0] # rent charged with color set and 0 houses
  )
  assert mireia.balance() == (
    const.START_MONEY - getattr(whitechapel, '_color_set_rents')[0] # rent charged with color set and 0 houses
  )

  return board

def test_street_rent_color_set_with_mortgage():
  '''Tests that color set rent is also applied even when a property in the set
  is mortgaged.'''
  board = test_rent_street_color_set() # jordi owns the brown color set and it is arnau's turn
  arnau = board.players()[2]
  old_kent: Street; whitechapel: Street
  old_kent, tmp, whitechapel = board.tiles()[1:4]

  old_kent.mortgage()
  board.run(1) # arnau lands on whitechapel

  assert old_kent.is_mortgaged()
  assert arnau.balance() == (
    const.START_MONEY - getattr(whitechapel, '_color_set_rents')[0]
  )

def test_street_rent_houses():
  '''Tests that rent is charged properly on a street when there are houses
  built on it, for one to four houses.'''
  for i in range(1, 5):
    board = DebugBoard(
      die_inputs = [(-1, 1), (2, 1)]
    )
    jordi, mireia = board.players()[:2]
    old_kent: Street; whitechapel: Street
    old_kent, tmp, whitechapel = board.tiles()[1:4]

    board.run(1) # if we gave jordi any properties before he ended his turn, the ai
    # would build stuff on its own, which we dont want

    for property in old_kent, whitechapel: jordi.buy(property)

    jordi.entrust(10000) # we dont want the ai running out of money either
    whitechapel.build()
    for _ in range(i - 1): old_kent.build(); whitechapel.build()
    assert whitechapel.houses() == i

    board.run(1) # mireia lands on whitechapel and pays the corresponding rent
    assert mireia.balance() == (
      const.START_MONEY - getattr(whitechapel, '_color_set_rents')[i]
    )

def test_street_rent_hotel():
  '''Tests that rent is charged properly on a street when there is an hotel
  built on it.'''
  board = DebugBoard(
    die_inputs = [(-1, 1), (2, 1)]
  )
  jordi, mireia = board.players()[:2]
  old_kent: Street; whitechapel: Street
  old_kent, tmp, whitechapel = board.tiles()[1:4]

  board.run(1)
  # end jordi's turn before we give him anything lest the ai build inadvertedly

  for property in old_kent, whitechapel: jordi.buy(property)

  jordi.entrust(9000)
  for _ in range(5): old_kent.build(); whitechapel.build()
  assert old_kent.has_hotel() and whitechapel.has_hotel()

  board.run(1)
  assert mireia.balance() == (
    const.START_MONEY - getattr(whitechapel, '_rent_with_hotel')
  )

def test_station_default_rent():
  raise NotImplementedError

def test_station_rent_2_stations():
  raise NotImplementedError

def test_station_rent_3_stations():
  raise NotImplementedError

def test_station_rent_4_stations():
  raise NotImplementedError

def test_utility_default_rent():
  '''Tests that rent is charged properly when a player lands on an utility
  tile whose owner has only one utility tile in possession'''
  board = DebugBoard(
    die_inputs = [(12, 0), (12, 0), (1, 3)]
  )
  mireia = board.players()[1]
  electric_company: Utility = board.tiles()[12]

  board.play()
  # jordi lands on electric company and buys it
  # mireia lands on electric company and rolls 1, 3 for its rent
  # mireia should have lost 4*default multiplier
  assert mireia.balance() == (
    const.START_MONEY
    - (1 + 3) * getattr(electric_company, '_default_multiplier')
  )

def test_utility_rent_two_utilities():
  '''Tests that rent is charged properly when a player lands on an utility
  tile whose owner has both utility tiles in possession'''
  board = DebugBoard(
    die_inputs = [(6, 6), (16, 0), (12, 0), (1, 2)]
  )

  mireia = board.players()[1]
  electric_company = board.tiles()[12]

  board.play()
  # jordi lands on electric company and buys it
  # jordi plays again because he has rolled doubles; this time, he lands on
  # water works and buys it
  # mireia lands on electric company and rolls 1, 2 for its rent
  # mireia should have lost 3*multiplier with both
  assert mireia.balance() == (
    const.START_MONEY
    - (1 + 2) * getattr(electric_company, '_multiplier_with_both')
  )

def test_utility_doubles_no_turn_repeats():
  '''Tests that the player does not play another turn after rolling doubles for
  to pay rent at a utilities square.'''
  board = DebugBoard(
    die_inputs = [(12, 0), (12, 0), (2, 2)]
  )

  mireia = board.players()[1]
  board.play()
  # jordi lands on electric company and buys it
  # mireia lands on electric company
  # mireia rolls 2, 2 for the electric company rent
  # mireia should not play again because she did not roll doubles in her previous turn
  assert not board.current_player() == mireia

def test_utility_doubles_no_straight_double_count():
  '''Tests that the player does not go to prison after rolling doubles just twice
  when they roll doubles at a utility square.'''
  board = DebugBoard(
    die_inputs = [(12, 0), (6, 6), (2, 2), (3, 3)]
  )

  mireia = board.players()[1]

  board.play()
  # jordi lands on electric company and buys it
  # mireia rolls doubles and lands on electric company
  # mireia rolls 2, 2 for the electric company rent
  # mireia rolls doubles again
  # mireia should not be in prison because she only got two straight doubles
  assert not mireia.is_in_prison()

def test_utility_doesnt_break_doubles_streak():
  '''Tests that, if a player has rolled doubles to land on this tile,
  they get to play again regardless of what they rolled'''

  raise NotImplementedError