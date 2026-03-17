from __future__ import annotations

from board import Board
import const, random, shutil, os

def main() -> None:
  shutil.rmtree('imgs') # remove imgs directory
  os.makedirs('imgs', exist_ok = True) # remake imgs directory

  random.seed(const.SEED)
  Board().play()

if __name__ == "__main__":
  main()