import json
from card import Card, build_card

class Deck:
  _cards: list[Card]

  def __init__(self, path: str) -> None:
    with open(path) as file:
      data = json.load(file)
    self._cards = [build_card(card_data) for card_data in data]