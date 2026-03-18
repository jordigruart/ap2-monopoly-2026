import pytest
from typing import TYPE_CHECKING

from board import DebugBoard
if TYPE_CHECKING: from tile import Street, Station
import const

def test_advance_to_go():
  board = DebugBoard(
    die_inputs = [(4, 3)],
    cards = [1]
  )
  jordi = board.players()[0]
  board.play() # jordi lands on chance and draws Advance to Go
  assert jordi.position() == 0
  assert jordi.balance() == const.START_MONEY + const.GO_SALARY

def test_advance_to_trafalgar():
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
  '''Tests that nearest station logic is run properly when landing on chance 7.'''
  board = DebugBoard(
    die_inputs = [(4, 3)],
    cards = [4]
  )
  jordi = board.players()[0]
  maryleborn_station: Station = board.tiles()[15]
  board.play() # jordi lands on chance and draws Advance to Nearest Station
  # which is maryleborn

  assert jordi.current_tile() == maryleborn_station
  assert jordi.owns(maryleborn_station)

def test_advance_to_nearest_station_2():
  '''Tests that nearest station logic is run properly when landing on chance 22.'''
  board = DebugBoard(
    die_inputs = [(22, 0)],
    cards = [4]
  )
  jordi = board.players()[0]
  fenchurch_st: Station = board.tiles()[25]
  board.play() # jordi lands on chance and draws Advance to Nearest Station
  # which is maryleborn

  assert jordi.current_tile() == fenchurch_st
  assert jordi.owns(fenchurch_st)

def test_advance_to_nearest_station_3():
  '''Tests that nearest station logic is run properly when landing on chance 36.'''
  board = DebugBoard(
    die_inputs = [(36, 0)],
    cards = [4]
  )
  jordi = board.players()[0]
  kings_cross: Station = board.tiles()[5]
  board.play() # jordi lands on chance and draws Advance to Nearest Station
  # which is kings cross

  assert jordi.current_tile() == kings_cross
  assert jordi.balance() > const.START_MONEY - kings_cross.price() # he shouldve collected go bonus

def test_advance_to_nearest_utility():
  '''Tests that nearest station logic is run properly when landing on chance 36.'''
  raise NotImplementedError

def test_advance_to_nearest_rent():
  '''Tests that, for card Advance to Nearest Station, rent is charged when
  the station is landed on and the rent multiplier is applied properly.
  
  (Card description:
  Advance to nearest Station. If unowned, you may buy it from the Bank. If
  owned, pay owner twice the rental to which they are otherwise entitled)'''
  board = DebugBoard(
    die_inputs = [(15, 0), (4, 3)],
    cards = [4]
  )
  mireia = board.players()[2]
  maryleborn_station: Station = board.tiles()[15]

  board.play() # jordi lands on and buys maryleborn
               # mireia lands on chance and draws Advance to Nearest Station
  assert mireia.balance() == ( # rent should be twice the normal amount
   const.START_MONEY - 2 * maryleborn_station.__getattribute__('_rents')[1])

def advance_to_nearest_utility_rent():
  raise NotImplementedError

def test_move_back_spaces():
  '''Tests that tile landing logic is run when player moves back a number of
  spaces due to a card.'''
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
  board = DebugBoard(
    die_inputs = [(7, 0)],
    cards = [10]
  )
  jordi = board.players()[0]
  board.play()
  assert jordi.is_in_prison()

def test_general_repairs():
  '''Tests that the following card charges the right amount:
  General Repairs: Make general repairs on all your property. For
  each house pay £25. For each hotel pay £100.'''
  raise NotImplementedError

def test_collect_money():
  raise NotImplementedError

def test_pay_each_player():
  ''''''
  raise NotImplementedError

def test_collect_from_players():
  '''Tests that the following card makes the right transactions:
  General Repairs: Make general repairs on all your property. For
  each house pay £25. For each hotel pay £100.'''