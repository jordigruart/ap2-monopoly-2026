import pytest
from typing import TYPE_CHECKING
if TYPE_CHECKING: from player import Player
from tile import *

from board import DebugBoard
import const, aitools

# testing movement
def test_doubles():
  board = DebugBoard(
    [(1, 1), (1, 2)]
  )
  jordi, mireia = board.players()[:2]

  assert board.current_player() == jordi

  board.run(1)
  assert board.current_player() == jordi

  board.run(1)
  assert board.current_player() == mireia

def test_three_doubles():
  board = DebugBoard(
    die_inputs = [(1, 1), (1, 1), (1, 1)]
  )
  jordi, mireia = board.players()[:2]

  board.play()
  assert jordi.is_in_prison()
  assert board.current_player() == mireia

def test_go_bonus_land_on_go():
  '''Tests that the go bonus is applied when a player lands on the GO square.'''
  board = DebugBoard(
    die_inputs = [(40, 0)]
  )
  jordi = board.players()[0]

  board.play()
  assert jordi.balance() == const.START_MONEY + const.GO_SALARY

# testing landing on tiles
def test_tax():
  '''Tests that landing on a tax tile charges the player the corresponding amount.'''
  board = DebugBoard(
    die_inputs = [(4, 0)]
  )
  jordi = board.players()[0]
  tax = board.tiles()[4]

  board.play()
  assert jordi.balance() == const.START_MONEY - getattr(tax, '_amount')

def test_buy_property() -> DebugBoard:
  board = DebugBoard(
    die_inputs = [(3, 0), (3, 0), (3, 0)]
  )
  jordi = board.players()[0]
  whitechapel_road = board.tiles()[3]

  board.run(1)
  assert whitechapel_road in jordi.owned_properties()
  assert isinstance(whitechapel_road, Street) # for type checking
  assert jordi.balance() == const.START_MONEY - whitechapel_road.price()

  return board

def test_rent_street_default():
  '''Tests that default rent (no color set or buildings) is charged properly
  on a street.'''
  board = test_buy_property()
  jordi, mireia = board.players()[:2]
  whitechapel_road = board.tiles()[3]
  assert isinstance(whitechapel_road, Street) # for type checking

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

def test_rent_street_mortgage() -> DebugBoard:
  '''Tests that rent is not charged on a mortgaged property.'''
  board = test_buy_property()
  mireia = board.players()[1]
  whitechapel = board.tiles()[3]
  assert isinstance(whitechapel, Street)

  whitechapel.mortgage()
  board.run(1) # mireia lands on whitehchapel; should not have been charged any rent because it is mortgaged
  assert mireia.balance() == const.START_MONEY

  return board

def test_rent_street_demortgage():
  '''Tests that rent is charged on a previously mortgaged property after being demortgaged.'''
  board = test_rent_street_mortgage()
  arnau = board.players()[2]
  whitechapel = board.tiles()[3]
  assert isinstance(whitechapel, Street)

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
  old_kent, tmp, whitechapel = board.tiles()[1:4]
  assert isinstance(old_kent, Street) # for type checking
  assert isinstance(whitechapel, Street)

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

def test_rent_street_color_set_with_mortgage():
  '''Tests that color set rent is also applied even when a property in the set
  is mortgaged.'''
  board = test_rent_street_color_set() # jordi owns the brown color set and it is arnau's turn
  arnau = board.players()[2]
  old_kent, tmp, whitechapel = board.tiles()[1:4]
  assert isinstance(old_kent, Street) # for type checking
  assert isinstance(whitechapel, Street)

  old_kent.mortgage()
  board.run(1) # arnau lands on whitechapel

  assert old_kent.is_mortgaged()
  assert arnau.balance() == (
    const.START_MONEY - getattr(whitechapel, '_color_set_rents')[0]
  )

def test_rent_street_houses():
  '''Tests that rent is charged properly on a street when there are houses
  built on it, for one to four houses.'''
  for i in range(1, 5):
    board = DebugBoard(
      die_inputs = [(-1, 1), (2, 1)]
    )
    jordi = board.players()[0]
    mireia = board.players()[1]
    old_kent, tmp, whitechapel = board.tiles()[1:4]
    assert isinstance(old_kent, Street) # for type checking
    assert isinstance(whitechapel, Street) # for type checking

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
  jordi = board.players()[0]
  mireia = board.players()[1]
  old_kent, tmp, whitechapel = board.tiles()[1:4]
  assert isinstance(old_kent, Street) # for type checking
  assert isinstance(whitechapel, Street)

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

def test_rent_utilities_two_utilities():
  '''Tests that rent is charged properly when a player lands on a'''
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

def test_doubles_in_utilities_rent_do_not_make_you_play_again():
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

def test_doubles_in_utilities_rent_do_not_count_towards_straight_double_count():
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

# testing buying and selling
def test_building_orderly() -> DebugBoard:
  '''Test whether building in order works.'''
  board = DebugBoard(
    die_inputs = [(-1, 1)]
  )
  jordi = board.players()[0]
  regent, oxford, tmp, bond = board.tiles()[31:35]
  assert isinstance(regent, Street) # ty
  assert isinstance(oxford, Street) # pe
  assert isinstance(bond, Street) # checking

  board.play()
  # end play before we give jordi anything lest the ai build inadvertedly

  jordi.entrust(19000)
  for property in board.color_set('green'): jordi.buy(property)

  regent.build(); bond.build(); oxford.build(); oxford.build()
  bond.build(); regent.build(); bond.build(); oxford.build()

  return board

def test_selling_orderly():
  '''Tests that selling in order works.'''
  board = test_building_orderly()
  regent, oxford, tmp, bond = board.tiles()[31:35]
  assert isinstance(regent, Street) # ty
  assert isinstance(oxford, Street) # pe
  assert isinstance(bond, Street) # checking

  oxford.sell(); bond.sell(); regent.sell(); bond.sell()
  oxford.sell(); oxford.sell(); bond.sell(); regent.sell()

def test_building_unorderly():
  '''Tests that building on the same tile twice in a row does not work.'''
  with pytest.raises(AssertionError):
    board = DebugBoard(
      die_inputs = [(-1, 1)]
    )
    jordi = board.players()[0]
    regent = board.tiles()[31]

    board.play()

    jordi.entrust(19000)
    for property in board.color_set('green'): jordi.buy(property)

    assert isinstance(regent, Street)
    for _ in range(2): regent.build()

def test_ai_builds_properly_from_zero():
  '''Tests that the player AI knows how to build from 0 houses on a set to
  three hotels granted unlimited funds.'''
  board = DebugBoard(
    die_inputs = [(5, 5), (-1, 1)]
  )
  jordi = board.players()[0]

  board.run(1) # jordi lands on just visiting
  # end jordi's turn before we give him anything lest the ai build inadvertedly

  jordi.entrust(100000)
  for property in board.color_set('green'): jordi.buy(property)

  board.play() # the ai will now buy until there is an hotel on every tile
  assert all(property.has_hotel() for property in board.color_set('green'))

def test_ai_builds_properly_from_a_start() -> DebugBoard:
  '''Tests that the player AI knows how to build from an already present amount
  of houses on a set to three hotels granted unlimited funds.'''
  board = DebugBoard(
    die_inputs = [(5, 5), (-1, 1)]
  )
  jordi = board.players()[0]
  regent, oxford, tmp, bond = board.tiles()[31:35]
  assert isinstance(regent, Street)
  assert isinstance(oxford, Street)
  assert isinstance(bond, Street)

  board.run(1) # the board wont be drawn properly if we dont roll jordi's dice first

  jordi.entrust(100000)
  for property in board.color_set('green'): jordi.buy(property)

  regent.build(); oxford.build()

  board.play() # the ai will now buy until it cant anymore
  # (i.e. until there is an hotel on every green tile)
  assert all(property.has_hotel() for property in board.color_set('green'))

  return board

def test_ai_sells_properly_from_all():
  '''Tests that the player AI knows how to empty a color set; from hotels, to mortgaged
  properties.'''
  board = test_ai_builds_properly_from_a_start()
  jordi = board.players()[0]

  jordi.__setattr__('_money', -10000)
  aitools._run_selling_actions(jordi) # ai will now attempt to go over 0
  assert all(property.is_mortgaged() for property in board.color_set('green'))

# testing prison
def test_three_turns_in_prison():
  '''Tests that spending three turns in prison takes you out of jail.'''
  board = DebugBoard(
    die_inputs = [
      (0, 30), (-1, 1), (-1, 1), (-1, 1), # (0, 30) places Jordi at Go to Jail
      (-1, 1), (-1, 1), (-1, 1), (-1, 1),
      (-1, 1), (-1, 1), (-1, 1), (-1, 1),
      (-1, 1)]
  )
  jordi = board.players()[0]

  board.run(1)
  assert jordi.is_in_prison()

  board.run(3)
  # it is about to be jordi's turn again, but he has still not spent any turns in prison
  assert jordi.turns_in_prison() == 0
  board.run(1)
  # when this turn finishes, he has spent a turn in prison
  assert jordi.turns_in_prison() == 1

  board.run(4)
  assert jordi.turns_in_prison() == 2

  board.run(3)
  assert jordi.turns_in_prison() == 2
  # jordi's turn starts next
  board.run(1)
  # when it ends, he has spent 3 turns in prison, so he should now be free
  assert not jordi.is_in_prison()
  assert jordi.turns_in_prison() == 0

  assert board.current_player() is not jordi # next player after he is freed should be mireia

def test_get_out_of_jail_free():
  ...

def test_roll_doubles_to_get_out_of_jail():
  '''Tests that getting out of jail with doubles works properly.'''
  board = DebugBoard(
  die_inputs =[
    (0, 30), (-1, 1), (-1, 1), (-1, 1),
    (2, 2)]
  )

  jordi = board.players()[0]

  board.run(1) # lands on go to jail
  assert jordi.is_in_prison()

  board.run(4) # all players have a go and then jordi rolls doubles; he gets out of prison and continues his turn normally
  assert not jordi.is_in_prison()
  assert jordi.position() == board.jail_position() + 4 # result for doubles is then used for player's next move according to official rules
  assert board.current_player() == jordi # jordi should play another turn´


'''TODO
- station rent
- building not in order
- cards
- goojfc
- elimination
'''