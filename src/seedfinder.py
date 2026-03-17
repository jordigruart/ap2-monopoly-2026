from __future__ import annotations

from board import Board
import random, sys

i = int(sys.argv[1])
while True:
  print('Trying seed', i)
  random.seed(i)
  if Board(image_path = 'debug/imgs/').play():
    print(
    f'''
    =========================
    SEED FOUND: {i} ends the game in less than 400 turns!
    ========================='''
    )
    if input('Press enter to find more seeds or type q to quit') == 'q': break

  else:
    print('Unsuccessful.')

  i += 1