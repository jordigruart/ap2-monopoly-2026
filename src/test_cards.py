import pytest
from typing import TYPE_CHECKING

from board import DebugBoard
if TYPE_CHECKING: from tile import Street, Station, Utility
import const

def test_advance_to_go():
  '''Tests card Advance to Go.
  
  Card ID: 1 / Card description:
  Advance to Go (Collect £200)'''
  board = DebugBoard(
    die_inputs = [(4, 3)],
    cards = [1]
  )
  jordi = board.players()[0]
  board.play() # jordi lands on chance and draws Advance to Go
  assert jordi.position() == 0
  assert jordi.balance() == const.START_MONEY + const.GO_SALARY

def test_advance_to_trafalgar():
  '''Tests that card Advance to Trafalgar runs the landing logic.
  
  Card ID: 2 / Card description:
  Advance to Trafalgar Square. If you pass Go, collect £200'''
  board = DebugBoard(
    die_inputs = [(4, 3)],
    cards = [2]
  )
  jordi = board.players()[0]
  trafalgar: Street = board.tiles()[24]
  board.play() # jordi lands on chance and draws Advance to Trafalgar Square
  assert jordi.current_tile() == trafalgar
  assert jordi.owns(trafalgar) # he shouldve bought it bc he has the money; this
  # demonstrates the landing logic was run

def test_advance_to_nearest_station_1():
  '''Tests that nearest station logic is run properly when landing on chance 7.
  Card ID: 4 / Card description:
  Advance to nearest Station. If unowned, you may buy it from the Bank. If
  owned, pay owner twice the rental to which they are otherwise entitled)'''
  board = DebugBoard(
    die_inputs = [(4, 3)],
    cards = [4]
  )
  jordi = board.players()[0]
  maryleborn_station: Station = board.tiles()[15]
  board.play() # jordi lands on chance and draws Advance to Nearest Station
  # which is maryleborn (see board for reference)

  assert jordi.current_tile() == maryleborn_station
  assert jordi.owns(maryleborn_station)

def test_advance_to_nearest_station_2():
  '''Tests that nearest station logic is run properly when landing on chance 22.
  
  Card ID: 4 / Card description:
  Advance to nearest Station. If unowned, you may buy it from the Bank. If
  owned, pay owner twice the rental to which they are otherwise entitled)'''
  board = DebugBoard(
    die_inputs = [(22, 0)],
    cards = [4]
  )
  jordi = board.players()[0]
  fenchurch_st: Station = board.tiles()[25]
  board.play() # jordi lands on chance and draws Advance to Nearest Station
  # which is fenchurch st (see board for reference)

  assert jordi.current_tile() == fenchurch_st
  assert jordi.owns(fenchurch_st)

def test_advance_to_nearest_station_3():
  '''Tests that nearest station logic is run properly when landing on chance 36.
  Card ID: 4 / Card description:
  Advance to nearest Station. If unowned, you may buy it from the Bank. If
  owned, pay owner twice the rental to which they are otherwise entitled'''
  board = DebugBoard(
    die_inputs = [(36, 0)],
    cards = [4]
  )
  jordi = board.players()[0]
  kings_cross: Station = board.tiles()[5]
  board.play() # jordi lands on chance and draws Advance to Nearest Station
  # which is kings cross (see board for reference)

  assert jordi.current_tile() == kings_cross
  assert jordi.balance() > const.START_MONEY - kings_cross.price() # he shouldve collected go bonus

def test_advance_to_nearest_utility():
  '''Tests that nearest utility logic is run properly when landing on chance 7.

  Card ID: 5 / Card description:
  Advance to nearest Utility. If unowned, you may buy it from the Bank. If
  owned, throw dice and pay owner ten times the rental to which they are
  otherwise entitled'''
  board = DebugBoard(
    die_inputs = [(4, 3)],
    cards = [6]
  )
  jordi = board.players()[0]
  electric: Utility = board.tiles()[12]
  board.play() # jordi lands on chance and draws Advance to Nearest Utility
  # which is electric company (see board for reference)

  assert jordi.current_tile() == electric
  assert jordi.owns(electric)

def test_advance_to_nearest_station_rent():
  '''Tests that, for Advance to Nearest Station, rent is charged when
  the station is landed on and the rent multiplier is applied properly.
  
  Card ID: 5 / Card description:
  Advance to nearest Station. If unowned, you may buy it from the Bank. If
  owned, pay owner twice the rental to which they are otherwise entitled)'''
  board = DebugBoard(
    die_inputs = [(15, 0), (4, 3)],
    cards = [5]
  )
  mireia = board.players()[1]
  maryleborn_station: Station = board.tiles()[15]

  board.play() # jordi lands on and buys maryleborn
               # mireia lands on chance and draws Advance to Nearest Station
  assert mireia.balance() == ( # rent should be twice the normal amount
    const.START_MONEY - 2 * maryleborn_station.__getattribute__('_rents')[1])

def test_advance_to_nearest_utility_rent():
  '''Tests that, for card Advance to Nearest Utility, rent is charged when
  the tile is landed on and the rent multiplier is applied properly.
  
  Card ID: 6 / Card description:
  Advance to nearest Utility. If unowned, you may buy it from the Bank. If
  owned, throw dice and pay owner a total ten times the rental to which they
  are otherwise entitled.'''
  board = DebugBoard(
    die_inputs = [(12, 0), (4, 3), (1, 2)],
    cards = [6]
  )
  mireia = board.players()[1]
  electric: Station = board.tiles()[12]

  board.play() # jordi lands on and buys electric company
               # mireia lands on chance and draws Advance to Nearest Utility
  assert mireia.balance() == ( # rent should be 10 times the normal ammount
    const.START_MONEY - (10 * (1 + 2) * getattr(electric, '_default_multiplier')))

def test_move_back_spaces():
  '''Tests that tile landing logic is run when player moves back a number of
  spaces due to a card.
  
  Card ID: 9 / Card description: Go back 3 spaces.'''
  board = DebugBoard(
    die_inputs = [(7, 0)],
    cards = [9]
  )
  jordi = board.players()[0]
  income_tax = board.tiles()[4]
  board.play() # jordi lands on chance and draws Go Back 3 Spaces
  # which is income tax
  assert jordi.balance() < const.START_MONEY # this demonstrates the logic was run

def test_go_to_jail_card():
  '''Tests that the following card sends the player to prison:
  Card ID: 10 / Card description: Go to Jail.'''
  board = DebugBoard(
    die_inputs = [(7, 0)],
    cards = [10]
  )
  jordi = board.players()[0]
  board.play()
  assert jordi.is_in_prison()

def test_general_repairs():
  '''Tests that the following card charges the right amount:
  Card ID: 11 / Card description:
  Make general repairs on all your property. For each house pay £25.
  For each hotel pay £100.'''
  board = DebugBoard(
    die_inputs = [(0, 0), (0, 0), (7, 0)],
    cards = [11]
  )
  jordi = board.players()[0]
  board.run(1) # the board wont be drawn properly if we dont roll jordi's dice first
  jordi.entrust(100000) # ensure the ai can build all it wants
  for property in board.color_set('green'): jordi.buy(property)
  board.run(1) # jordi rolls again and lands on go
  # at the end of this turn he builds on every green tile up to hotels
  jordi.__setattr__('_money', 1000)
  board.run(1) # he plays again and lands on chance, where he draws General Repairs
  # he has 4*3 = 12 houses and 3 hotels
  assert jordi.balance() == 1000 - 25 * 12 - 3 * 100

def test_collect_money():
  '''Tests that the following card gives player the right amount:
  Card ID: 7 / Card description:
  Bank pays you a dividend of $50'''
  board = DebugBoard(
    die_inputs = [(7, 0)],
    cards = [7]
  )
  jordi = board.players()[0]
  board.play()
  assert jordi.balance() == const.START_MONEY + 50

def test_pay_money():
  '''Tests that the following card charges the right amount:
  Card ID: 12 / Card description:
  Speeding Fine. Pay $15'''
  board = DebugBoard(
    die_inputs = [(7, 0)],
    cards = [12]
  )
  jordi = board.players()[0]
  board.play()
  assert jordi.balance() == const.START_MONEY - 15

def test_pay_each_player():
  '''Tests that the following card charges and gives everybody the right amount:
  Chairman of the Board (chance ID 15)
  You have been elected Chairman of the Board. Pay each player £50
  '''
  board = DebugBoard(
    die_inputs = [(7, 0)],
    cards = [15]
  )
  jordi = board.players()[0]
  board.play()
  assert jordi.balance() == const.START_MONEY - 3 * 50
  assert all(player.balance() == const.START_MONEY + 50 for player in board.players()[1:])

def test_collect_from_players():
  '''Tests that the following card makes the right transactions:
  Grand Opera Night (community chest ID 7)
  Collect £50 from every player for opening night seats'''
  board = DebugBoard(
    die_inputs = [(2, 0)],
    cards = [7]
  )
  jordi = board.players()[0]
  board.play() #jordi lands on community chest and draws Grand Opera Night
  assert jordi.balance() == const.START_MONEY + 3 * 50
  assert all(player.balance() == const.START_MONEY - 50 for player in board.players()[1:])