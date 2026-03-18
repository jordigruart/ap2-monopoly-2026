import pytest

import const
from board import DebugBoard

def test_doubles():
  board = DebugBoard(
    [(2, 2), (1, 3)]
  )
  jordi, mireia = board.players()[:2]
  assert board.current_player() == jordi
  board.run(1)
  assert board.current_player() == jordi
  board.run(1)
  assert board.current_player() == mireia

def test_three_doubles_jail():
  '''Tests that a player goes to jail after rolling three doubles.'''
  board = DebugBoard(
    die_inputs = [(2, 2), (1, 1), (1, 1)]
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
  assert jordi.position() == 0
  assert jordi.balance() == const.START_MONEY + const.GO_SALARY

def test_go_bonus_pass_go():
  '''Tests that the go bonus is applied when a player passes the GO square.
  ''' # Realistically, a player will move no more than 40 tiles.
  board = DebugBoard( # Making more than one lap is not implemented
    die_inputs = [(50, 0)]
  )
  jordi = board.players()[0]

  board.play()
  assert jordi.balance() == const.START_MONEY + const.GO_SALARY