from __future__ import annotations

from typing import TYPE_CHECKING
import json
from card import Card, build_card
if TYPE_CHECKING: from board import Board

class Deck:
  _cards: set[Card]

  def __init__(self, board: Board, path: str) -> None:
    with open(path) as file:
      data = json.load(file)
    self._cards = [build_card(board, card_data) for card_data in data]
  
  def pop(self): return self._cards.pop()
  def __len__(self): return len(self._cards)