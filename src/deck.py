from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Any
import random, json

from card import Card, build_card
if TYPE_CHECKING: from board import Board

class Deck:
  _cards: dict[int, Card]

  def __init__(self, board: Board, path: str) -> None:
    '''Builds a deck of cards from a JSON-like dictionary.'''
    with open(path) as file:
      data = json.load(file)
    self._cards = {card['id']: build_card(board, **card) for card in data}
  
  def extract(self):
    '''Returns a random card from the deck'''
    id = random.randint(1, len(self._cards))
    return self._cards[id]

class DebugDeck(Deck):
  _card_ids: Iterator[int]
  def __init__(self, card_ids: Iterator[int], **kwargs: Any):
    super().__init__(**kwargs)
    self._card_ids = card_ids
  
  def extract(self):
    '''Returns the next card according to the card iterator.'''
    id = next(self._card_ids)
    return self._cards[id]