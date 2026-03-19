from board import DebugBoard
import aitools

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
  regent, oxford, tmp, bond = board.tiles()[31:35]

  board.run(1) # the board wont be drawn properly if we dont roll jordi's dice first
  jordi.entrust(100000) # ensure the ai can build all it wants
  for property in board.color_set('green'): jordi.buy(property)
  regent.build(); oxford.build()

  board.run(1) # jordi rolled doubles so he plays again
  # at the end of this turn, the ai will buy until it cant anymore
  # (i.e. until there is an hotel on every green tile)
  assert all(property.has_hotel() for property in board.color_set('green'))

  return board

def test_ai_sells_properly_from_full_set() -> DebugBoard:
  '''Tests that the player AI knows how to empty a color set from hotels to
  mortgaged properties.
  
  Return value:
  Returns board with all players at GO, all greens mortgaged & under Jordi's
  property and Mireia's turn. Pending rolls are (1, 0), (-1, 1), (-1, 1),
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

def test_pays_mortgage_if_able() -> None:
  '''Tests that a player.'''
  raise NotImplementedError

# def makes right choices when recieving properties
# def gets out of jail