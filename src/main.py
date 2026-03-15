from __future__ import annotations

from board import Board
import random

def main() -> None:
  random.seed(30)
  Board().play()

if __name__ == "__main__":
  main()