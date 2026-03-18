import pytest
from board import DebugBoard

def test_elimination_tax() -> DebugBoard:
  '''Tests that a player can be eliminated when landing on a tax tile.'''
  board = DebugBoard(
    die_inputs = [(4, 0), (-1, 1), (-1, 1), (-1, 1), (4, 0)]
  )
  jordi = board.players()[0]
  jordi.deduct(1400) # deducted from $1500; balance is now $100
  board.run(1) #jordi lands on income tax which, is $200
  assert jordi.is_bankrupt()
  return board

def test_eliminated_player_doesnt_play():
  '''Tests that players who have been eliminated cannot play at all.'''
  board = test_elimination_tax()
  jordi = board.players()[0]
  board.run(3) # mireia, arnau and marta have a go
  board.run(1) # mireia shouldve landed on tax
  assert board.current_player() != jordi
  # jordi shouldnt have been charged anything; it shouldve been mireia
  assert jordi.balance() == -100 

def test_elimination_ends_turn():
  '''Tests that eliminating a player during their turn ends it immediately.'''

def test_properties_reset():
  '''Tests that unmortgaged properties are reset when a player is eliminated.'''
  from test_building_and_selling import test_building_orderly

  # jordi's turn
  # he owns green and there are some houses on every green street
  board = test_building_orderly()
  jordi = board.players()[0]
  jordi.__setattr__('_money', 100)
  board.play() # all players stall until jordi lands on income tax and is eliminated

  assert all(not property.owner() and property.houses() == 0         
    for property in board.color_set('green')) 

def test_mortgages_given_to_creditor():
  '''Tests that mortgaged properties are given to the player who eliminates
  an eliminated player.'''
  from test_player_ai import test_ai_sells_properly_from_full_set
  board = test_ai_sells_properly_from_full_set()
  jordi, mireia = board.players()[:2]
  # all players at GO
  # all greens mortgaged and under jordi's property
  # mireia's turn

  jordi.__setattr__('_money', 1)

  board.play() # mireia lands on old kent and buys it, arnau and marta stall,
  # jordi lands on old kent and is eliminated
  # mireia should be the owner of every previously mortgaged property of jordi's
  # which are the greens
  assert all(property.owner() == mireia for property in board.color_set('green'))

def test_bankruptcy_when_keeping_mortgage():
  '''Tests that it is possible for a player to go bankrupt when deciding to
  keep mortgaged properties.'''
  # behaviour similar to last test (test_mortgages_given_to_creditor)
  from test_player_ai import test_ai_sells_properly_from_full_set
  board = test_ai_sells_properly_from_full_set()
  jordi, mireia = board.players()[:2]

  jordi.__setattr__('_money', 1)
  board.run(1) # mireia lands on old kent and buys it
  mireia.__setattr__('_money', 1)

  board.run(3) # arnau and marta stall,
  # jordi lands on old kent and is eliminated
  # mireia has to either keep the mortgage on the properties for a fee or pay it
  # so se should be eliminated as well
  assert mireia.is_bankrupt()

  board.run(1)
  assert board.current_player() != mireia

def test_bankruptcy_pay_bank_card():
  '''Tests that it is possible for a player to go bankrupt when drawing a
  \"Pay the bank\" card.'''
  raise NotImplementedError

def test_bankruptcy_pay_each_player_card():
  '''Tests that it is possible for a player to go bankrupt when drawing a
  \"Pay each player\" card.'''
  raise NotImplementedError

def test_bankruptcy_recieve_from_each_player_card():
  '''Tests that it is possible for a player to go bankrupt when some other
  player draws a \"Recieve money from each player\" card.'''
  raise NotImplementedError

def test_bankruptcy_pay_per_property_card():
  '''Tests that it is possible for a player to go bankrupt when drawing a
  \"Pay per property\" card.'''
  raise NotImplementedError