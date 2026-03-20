from board import DebugBoard
from typing import TYPE_CHECKING
import aitools
if TYPE_CHECKING: from tile import Street

def test_ai_builds_properly_from_zero():
  '''Tests that the player AI knows how to build from 0 houses on a set to
  three hotels granted unlimited funds.'''
  board = DebugBoard(
    die_inputs = [(5, 5), (-1, 1)]
  )
  jordi = board.players()[0]

  board.run(1) # jordi lands on just visiting
  # end jordi's turn before we give him anything lest the ai build inadvertedly

  jordi.entrust(100000) # ensure the ai can build all it wants
  for property in board.color_set('green'): jordi.buy(property)

  board.play() # the ai will now buy until there is an hotel on every tile
  assert all(property.has_hotel() for property in board.color_set('green'))

def test_ai_builds_properly_from_a_start() -> DebugBoard:
  '''Tests that the player AI knows how to build from an already present amount
  of houses on a set to three hotels granted unlimited funds.
  
  Return value:
  Returns board with all players at GO, all greens with hotel & under Jordi's
  property and Mireia's turn. Pending rolls are (1, 0), (-1, 1), (-1, 1),
  (1, 0), (-1, 1)'''
  board = DebugBoard(
    die_inputs = [(0, 0), (-1, 1), (1, 0), (-1, 1), (-1, 1), (1, 0), (-1, 1)]
  )
  jordi = board.players()[0]
  regent: Street; oxford: Street
  regent, oxford = board.tiles()[31:33]

  board.run(1) # the board wont be drawn properly if we dont roll jordi's dice first
  jordi.entrust(100000) # ensure the ai can build all it wants
  for property in board.color_set('green'): jordi.buy(property)
  regent.build(); oxford.build()

  board.run(1) # jordi rolled doubles so he plays again
  # at the end of this turn, the ai will buy until it cant anymore
  # (i.e. until there is an hotel on every green tile)
  assert all(property.has_hotel() for property in board.color_set('green'))

  return board

def test_ai_doesnt_buy_under_threshold():
  '''Tests that the AI doesnt buy a property if under $40.'''
  board = DebugBoard(
    die_inputs = [(0, 1)]
  )
  jordi = board.players()[0]
  old_kent: Street = board.tiles()[1]

  jordi.__setattr__('_money', 10)
  board.run(1) # jordi lands on old kent road and decides not to buy

  assert not jordi.owns(old_kent)

def test_ai_doesnt_build_if_not_enough_money():
  '''Tests that the AI doesnt build on a property during post-turn  actions if
  under $40, even if able.'''
  board = DebugBoard(
    die_inputs = [(-1, 1), (-1, 1)]
  )
  jordi = board.players()[0]
  board.run(1) # required in order for the board to be drawn properly

  for property in board.color_set('brown'): jordi.buy(property)
  jordi.__setattr__('_money', 10)
  board.run(1) #jordi should choose not to build when post turn actions come around
  assert all(property.houses() == 0 for property in board.color_set('brown'))

def test_ai_sells_properly_from_full_set() -> DebugBoard:
  '''Tests that the player AI knows how to empty a color set from hotels to
  mortgaged properties.
  
  Return value:
  Returns board with all players at GO, all greens mortgaged & under Jordi's
  property and Mireia's turn. Jordi has a negative amount of money.
  Pending rolls are (1, 0), (-1, 1), (-1, 1),
  (1, 0), (-1, 1)'''
  board = test_ai_builds_properly_from_a_start()
  jordi = board.players()[0]

  jordi.__setattr__('_money', -10000)
  aitools._run_selling_actions(jordi) # ai will now attempt to go over 0
  assert all(property.is_mortgaged() for property in board.color_set('green'))

  return board

def test_get_out_of_jail_free():
  '''Tests that a player uses a GOOJF card if they own one.'''
  board = DebugBoard(
    die_inputs = [
      (1, 1), (14, 14), (1, -1), (1, -1), (1, -1),
      (2, 3)
    ],
    cards = [5]
  )
  jordi = board.players()[0]
  board.play() # jordi lands on community chest and draws GOOJF
  # then lands on go to jail
  # everybody stalls for a turn
  # then its jordis turn. he shouldve used the GOOJF, got out and rolled
  assert not jordi.is_in_prison()