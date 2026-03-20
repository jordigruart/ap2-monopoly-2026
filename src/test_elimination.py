import pytest
from board import DebugBoard
import const

def test_elimination_tax() -> DebugBoard:
  '''Tests that a player can be eliminated when landing on a tax tile.
  
  Return value: Jordi eliminated, Mireia's turn. Pending rice rolls: 
  (-1, 1), (-1, 1), (-1, 1), (4, 0)'''
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
  board = test_elimination_tax() #see doc string for details
  mireia = board.players()[1]
  board.run(3) # mireia, arnau and marta have a go
  board.play() # mireia -- and not jordi -- shouldve landed on tax
  assert mireia.position() == 4
  # tile logic shouldve been run on mireia and not jordi
  assert mireia.balance() == const.START_MONEY - 200

def test_properties_reset():
  '''Tests that unmortgaged properties are reset when a player is eliminated.'''
  from test_building_and_selling import test_building_orderly

  # jordi's turn
  # he owns green and there are some houses on every green street
  board = test_building_orderly() #see doc string for details
  jordi = board.players()[0]
  jordi.__setattr__('_money', 100)
  board.play() # all players stall until jordi lands on income tax and is eliminated

  # properties shouldve been properly reset
  assert all(not property.owner and property.houses() == 0         
    for property in board.color_set('green')) 

def test_mortgages_given_to_creditor():
  '''Tests that mortgaged properties are given to the player who eliminates
  an eliminated player.'''
  from test_player_ai import test_ai_sells_properly_from_full_set
  board = test_ai_sells_properly_from_full_set()
  # all players at GO
  # all greens are mortgaged and under jordi's property
  # mireia's turn
  jordi, mireia = board.players()[:2]

  jordi.__setattr__('_money', 1)

  board.play() # mireia lands on old kent and buys it, arnau and marta stall,
  # jordi lands on old kent and is eliminated
  # mireia should be the owner of every previously mortgaged property of jordi's
  # which are the greens
  assert all(property.owner == mireia for property in board.color_set('green'))

def test_bankruptcy_when_keeping_mortgage():
  '''Tests that it is possible for a player to go bankrupt when deciding to
  keep mortgaged properties.'''
  # behaviour similar to last test (test_mortgages_given_to_creditor)
  from test_player_ai import test_ai_sells_properly_from_full_set
  board = test_ai_sells_properly_from_full_set()
  # all players at GO
  # all greens mortgaged and under jordi's property
  # mireia's turn
  jordi, mireia = board.players()[:2]

  jordi.__setattr__('_money', 1)
  board.run(1) # mireia lands on old kent and buys it
  mireia.__setattr__('_money', 1)

  board.run(3) # arnau and marta stall,
  # jordi lands on old kent and is eliminated
  # mireia has to either keep the mortgage on the properties for a fee or pay it
  # so se should be eliminated as well
  assert mireia.is_eliminated()

  board.run(1)
  assert board.current_player() != mireia
  assert jordi.is_eliminated() # he also shouldve been eliminated

def test_bankruptcy_pay_bank_card():
  '''Tests that it is possible for a player to go bankrupt when drawing a
  \"Pay the bank\" card.'''
  board = DebugBoard(
    die_inputs = [(7, 0)],
    cards = [12]
  )
  jordi = board.players()[0]
  jordi.__setattr__('_money', 10)
  board.play()
  assert jordi.is_eliminated()

def test_bankruptcy_pay_each_player_card():
  '''Tests that it is possible for a player to go bankrupt when drawing a
  \"Pay each player\" card.
  Chairman of the Board (chance ID 15)
  You have been elected Chairman of the Board. Pay each player £50
  '''
  board = DebugBoard(
    die_inputs = [(7, 0)],
    cards = [15]
  )
  jordi = board.players()[0]
  jordi.__setattr__('_money', 50)
  board.play() # jordi lands on chance and draws Chairman of the board
  assert jordi.is_eliminated()
  
  assert all(player.balance() == const.START_MONEY + 50 for player in board.players()[1:])
  # everybody else still shouldve gotten paid

def test_bankruptcy_recieve_from_each_player_card():
  '''Tests that it is possible for a player to go bankrupt when somebody draws a
  \"Collect from player\" card.
  
  Grand Opera Night (community chest ID 7)
  Collect £50 from every player for opening night seats'''
  board = DebugBoard(
    die_inputs = [(2, 0)],
    cards = [7]
  )
  jordi, mireia = board.players()[:2]
  mireia.__setattr__('_money', 10)
  board.play() #jordi lands on community chest and draws Grand Opera Night
  assert mireia.is_eliminated()
  assert jordi.balance() == const.START_MONEY + 3 * 50 # jordi still should have gotten paid completely
  assert board.current_player() != mireia # arnau should be playing

def test_bankruptcy_pay_per_property_card():
  '''Tests that it is possible for a player to go bankrupt when drawing a
  \"Pay per property\" card.
  Card ID: 11 / Card description:
  Make general repairs on all your properties. For each house pay £25.
  For each hotel pay £100.'''
  board = DebugBoard(
    die_inputs = [
      (1, 0), (-1, 1), (-1, 1), (-1, 1),
      (1, 1), (2, 2)],
    cards = [11]
  )
  jordi = board.players()[0]
  board.run(5) #jordi buys first brown; rest of plays stall; jordi buys second brown and builds
  jordi.__setattr__('_money', 10)
  board.run(1) # jordi rolls again, lands on chance and draws Pay per property
  assert jordi.is_eliminated()