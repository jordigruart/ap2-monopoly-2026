import pytest
from typing import TYPE_CHECKING

from board import DebugBoard
if TYPE_CHECKING: from tile import Street

def test_building_orderly() -> DebugBoard:
  '''Test whether building in order works.
  
  Return value: Green under Jordi's ownership and with some buildings. Mireia's
  turn. Pending rolls: (-1, 1), (-1, 1), (-1, 1), (0, 4)'''
  board = DebugBoard(
    die_inputs = [(-1, 1), (-1, 1), (-1, 1), (-1, 1), (0, 4)]
  )
  jordi = board.players()[0]
  regent: Street; oxford: Street; bond: Street
  regent, oxford, tmp, bond = board.tiles()[31:35] # type: ignore

  board.run(1)
  # end play before we give jordi anything lest the ai build inadvertedly

  jordi.entrust(19000)
  for property in board.color_set('green'): jordi.buy(property)

  regent.build(); bond.build(); oxford.build(); oxford.build()
  bond.build(); regent.build(); bond.build(); oxford.build()

  return board

def test_selling_orderly():
  '''Tests that selling in order works.'''
  board = test_building_orderly() # see doc strings for details
  regent: Street; oxford: Street; bond: Street
  regent, oxford, tmp, bond = board.tiles()[31:35] # type: ignore

  # regent: 2 houses; bond: 3 houses; oxford: 3 houses
  oxford.sell(); bond.sell(); regent.sell(); bond.sell()
  oxford.sell(); oxford.sell(); bond.sell(); regent.sell()

def test_building_unorderly():
  '''Tests that building on the same tile twice in a row does not work.'''
  with pytest.raises(AssertionError):
    board = DebugBoard(
      die_inputs = [(-1, 1)]
    )
    jordi = board.players()[0]
    regent: Street = board.tiles()[31] # type: ignore

    board.play()

    jordi.entrust(19000)
    for property in board.color_set('green'): jordi.buy(property)

    for _ in range(2): regent.build()

def test_selling_unorderly():
  '''Tests that selling on the same tile twice in a row does not work.'''
  with pytest.raises(Exception):
    board = test_building_orderly() #jordi has some greens with houses built on them
    bond: Street = board.tiles()[32] # type: ignore

    bond.sell(); bond.sell()