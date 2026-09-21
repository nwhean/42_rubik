"""Calculations related to the Thistlethwaite G2 algorithm."""
from functools import partial
import math

from .common import (
    EDGE_TYPE,
    EDGES,
    EDGE_PIECES,
    CORNERS,
    CORNER_PIECES,
    G2_FILE,
    generate_database,
    save_database as _save_database,
    load_database,
)
from ..common import get_colour
from ...cube import Cube, Colour


G2_MAX_STATE = 29_400
G2_DIST: list[int] | None = None

CORNER_INDICES: dict[frozenset[int], int] = {
    colours: i for i, colours in enumerate(CORNER_PIECES)
}

# a tetrad is a set of 4 adjacent corners on the Rubik's Cube
# these are the set of positions where one cubie can reach using
# U2, D2, L2, R2, F2, B2 moves only
TETRAD_0: set[frozenset[int]] = set(CORNER_PIECES[:4])

NON_M_EDGES: list[EDGE_TYPE] = EDGES[0:4] + EDGES[8:]

# We are tracking E_PIECES to isolate them in Phase 2
E_PIECES: set[frozenset[int]] = set(EDGE_PIECES[8:])

G2_MOVES = [
    'L', 'R',
    "L'", "R'",
    'U2', 'D2', 'L2', 'R2', 'F2', 'B2'
    ]


def tetrad_0_indices(cube: Cube) -> list[int]:
    """Return an ordered list containing the indices of tetrad_0 corners."""
    result = []
    for i, corner in enumerate(CORNERS):
        colour = frozenset(get_colour(cube, *tile) for tile in corner)
        if colour in TETRAD_0:
            result.append(i)
    return result

def tetrad_parity(cube: Cube) -> int:
    """Return the 0..5 tetrad/parity coordinate for G2."""
    piece_at_position = corner_indices(cube)

    # Build the tetrad representation.
    # For tetrad 0: store the piece numbers in positional order
    # i.e. corner[rank] = piece
    #
    # For tetrad 1, store:
    # i.e. corner[piece] = rank
    corner = [0] * 8
    tetrad_0_rank = 0
    tetrad_1_rank = 0

    for piece in piece_at_position:
        if piece < 4:
            corner[tetrad_0_rank] = piece
            tetrad_0_rank += 1
        else:
            corner[piece] = tetrad_1_rank
            tetrad_1_rank += 1

    # Determine the relative tetrad permutation.
    # Creates a 4-element array pair that maps each Tetrad 0 piece to
    # the positional rank of its corresponding Tetrad 1 counterpart piece.
    pair = [corner[4 + corner[i]] for i in range(4)]

    # Make the first element the reference point, i.e. pair[0] == 0
    base = pair[0]
    pair = [value ^ base for value in pair]

    # Encode the 3 tetrad states × 2 parity states.
    # pair as one of the following
    # [0, 1, 2, 3] -> 0 or [0, 1, 3, 2] -> 1
    # [0, 2, 1, 3] -> 2 or [0, 2, 3, 1] -> 3
    # [0, 3, 1, 2] -> 4 or [0, 3, 2, 1] -> 5
    result = pair[1] * 2 - 2
    if pair[3] < pair[2]:
        result += 1

    return result

def cube_E_indices(cube: Cube) -> list[int]:
    """Return the sorted indices of the E slice pieces."""
    result: list[int] = []
    for i, edge in enumerate(NON_M_EDGES):
        colour = frozenset(get_colour(cube, *tile) for tile in edge)
        if colour in E_PIECES:
            result.append(i)
    return result

def corner_indices(cube: Cube) -> list[int]:
    """Return a list containing the indices of the corners."""
    result: list[int] = []
    for i, corner in enumerate(CORNERS):
        colours = frozenset(get_colour(cube, *tile) for tile in corner)
        result.append(CORNER_INDICES[colours])
    return result

def rank_combination(combination: list[int]) -> int:
    """
    Finds the lexicographical rank of a 0-indexed k-combination.

    Reference: https://math.stackexchange.com/questions/1227409/indexing-all-combinations-without-making-list

    Parameter:
    combination - list of integers sorted in ascending order.
    """
    rank: int = 0
    for i, c in enumerate(combination, start=1):
        rank += math.comb(c, i)
    return rank

def cube_g2_index(cube: Cube) -> int:
    """Return a unique index between 0 to 29,399 for G2 state

    Combine the following:
    - tetrad_0 indices C(8, 4) = 70
    - E-slice indices C(8, 4) = 70
    - corner parity = 2
    - tetrad parity = 3
    for a total of 70 x 70 x 2 x 3 = 29,400 states.
    """
    t_indices = tetrad_0_indices(cube)
    e_indices = cube_E_indices(cube)
    tetrad_coord = tetrad_parity(cube)

    return (
        (rank_combination(t_indices)
         * 70 + rank_combination(e_indices))
        * 6 + tetrad_coord
        )

generate_g2_database = partial(
    generate_database, cube_g2_index, G2_MAX_STATE, G2_MOVES)

save_database = partial(_save_database, G2_FILE)

def read_database_2() -> None:
    """Read the Thistlethwaite G2 distance database from file."""
    global G2_DIST
    G2_DIST = load_database(G2_FILE, generate_g2_database)


if __name__ == "__main__":
    print("Generating G2 database...")
    g2_dist = generate_g2_database()
    save_database(g2_dist)
    print("Reached states:", len([i for i in g2_dist if i > -1]))
    print("Max moves:", max(g2_dist))
