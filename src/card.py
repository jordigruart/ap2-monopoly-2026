from typing import Any

class Card:
	def __init__(
		self,
		id: int,
		title: str,
		description: str,
		action: str,
	) -> None: ...

def build_card(data: dict[str, Any]) -> Card: ...