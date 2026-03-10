from board import Board
import random

def main() -> None:
  random.seed(-1)
  Board().play()

if __name__ == "__main__":
  main()

'''TODO: imprison method does not work
TODO: doubles dont work because EndTurn always _makes_way_for_next_player.'''