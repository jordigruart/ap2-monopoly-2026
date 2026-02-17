from board import Board
from draw import draw
import random

def main() -> None:
  board = Board(
    tiles_json_path="src/data/tiles.json",
    chance_json_path="src/data/chance.json",
    community_chest_json_path="src/data/community-chest.json",
    players_json_path="src/data/players.json",
  )

  random.seed(25)
  
  board.play()
  draw(board, 'imgs/tauler-0.svg')

if __name__ == "__main__":
  main()