import numpy as np
import config as c
from TetrisUtility import *

board = np.array([
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                  [1, 0, 0, 1, 0, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 1, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 1, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 1, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 0, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 0, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 0, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 0, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 0, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 1, 1, 0, 0, 1, 1,],
                  [1, 1, 1, 1, 1, 0, 0, 0, 1, 1,],
                  [1, 1, 1, 1, 1, 1, 1, 0, 1, 1,],
                  [1, 1, 1, 1, 0, 1, 1, 1, 1, 1,]
                  ])

placement = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 1, 1, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,]
    ])


print2d(board)
#print2d(placement)
result = board+placement
#print2d(result)
print2d(lineClear(result))
