from board import DebugBoard

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