from .thistlethwaite0 import read_database_0, cube_g0_index, G0_MOVES
from .thistlethwaite1 import read_database_1, cube_g1_index, G1_MOVES
from .thistlethwaite2 import read_database_2, cube_g2_index, G2_MOVES
from .thistlethwaite3 import read_database_3, cube_g3_index, G3_MOVES

read_database_0()
read_database_1()
read_database_2()
read_database_3()

from .thistlethwaite0 import G0_DIST
from .thistlethwaite1 import G1_DIST
from .thistlethwaite2 import G2_DIST
from .thistlethwaite3 import G3_DIST

from ...cube import Cube, SOLVED

PHASE_MOVES = [
    G0_MOVES,
    G1_MOVES,
    G2_MOVES,
    G3_MOVES,
]

INDICE_FUNC = [
    cube_g0_index,
    cube_g1_index,
    cube_g2_index,
    cube_g3_index,
]

PHASE_DIST = [
    G0_DIST,
    G1_DIST,
    G2_DIST,
    G3_DIST,
]
