"""Calculations related to the Thistlethwaite G2 algorithm."""
from collections import deque
from dataclasses import replace
import math
import pickle

from .common import Tile, BASE_DIR
from ..common import get_colour
from ...cube import Cube, Colour, SOLVED

G2_FILE = BASE_DIR / "G2_distance.pickle"
G2_DIST: list[int] | None = None

CORNERS = [
    (("F", 4), ("R", 4), ("D", 4)),     # FRD
    (("F", 0), ("L", 2), ("U", 6)),     # FLU
    (("B", 2), ("L", 6), ("D", 0)),     # BLD
    (("B", 6), ("R", 0), ("U", 2)),     # BRU
    (("F", 2), ("U", 4), ("R", 6)),     # FUR
    (("F", 6), ("D", 2), ("L", 4)),     # FDL
    (("B", 0), ("U", 0), ("L", 0)),     # BUL
    (("B", 4), ("D", 6), ("R", 2)),     # BDR
]

CORNER_COLOURS: list[set[int]] = [
    {Colour.R.value, Colour.B.value, Colour.Y.value},   # FRD
    {Colour.R.value, Colour.G.value, Colour.W.value},   # FLU
    {Colour.O.value, Colour.G.value, Colour.Y.value},   # BLD
    {Colour.O.value, Colour.B.value, Colour.W.value},   # BRU
    {Colour.R.value, Colour.W.value, Colour.B.value},   # FUR
    {Colour.R.value, Colour.Y.value, Colour.G.value},   # FDL
    {Colour.O.value, Colour.W.value, Colour.G.value},   # BUL
    {Colour.O.value, Colour.Y.value, Colour.B.value},   # BDR
]

CORNER_INDICES: dict[frozenset[int], int] = {
    frozenset(colours): i for i, colours in enumerate(CORNER_COLOURS)
}

# a tetrad is a set of 4 adjacent corners on the Rubik's Cube
# these are the set of positions where one cubie can reach using
# U2, D2, L2, R2, F2, B2 moves only
TETRAD_0: set[frozenset[int]] = {
    frozenset({Colour.R.value, Colour.B.value, Colour.Y.value}),   # FRD
    frozenset({Colour.R.value, Colour.G.value, Colour.W.value}),   # FLU
    frozenset({Colour.O.value, Colour.G.value, Colour.Y.value}),   # BLD
    frozenset({Colour.O.value, Colour.B.value, Colour.W.value}),   # BRU
}

NON_M_EDGES: list[tuple[Tile, Tile]] = [
    (("U", 3), ("R", 7)),   # UR - 0
    (("F", 3), ("R", 5)),   # FR - 1
    (("U", 7), ("L", 1)),   # UL - 2
    (("F", 7), ("L", 3)),   # FL - 3
    (("D", 1), ("L", 5)),   # DL - 4
    (("B", 1), ("L", 7)),   # BL - 5
    (("D", 5), ("R", 3)),   # DR - 6
    (("B", 5), ("R", 1)),   # BR - 7
]

# We are tracking E_PIECES to isolate them in Phase 2
E_PIECES: set[frozenset[int]] = {
    frozenset({Colour.R.value, Colour.B.value}),    # FR
    frozenset({Colour.R.value, Colour.G.value}),    # FL
    frozenset({Colour.O.value, Colour.G.value}),    # BL
    frozenset({Colour.O.value, Colour.B.value}),    # BR
}

G2_MOVES = [
    'L', 'R',
    "L'", "R'",
    'U2', 'D2', 'L2', 'R2', 'F2', 'B2'
    ]

def read_database() -> None:
    """Read the Thistlethwaite G2 distance database from file."""
    global G2_DIST
    try:
        with open(G2_FILE, "rb") as f:
            G2_DIST = pickle.load(f)

    except FileNotFoundError:
        G2_DIST = generate_g2_database()
        save_database(G2_DIST)

def save_database(g2_dist: list[int]) -> None:
    """Save the G2 distance database to files."""
    # Create the directory if it doesn't exist
    G2_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(G2_FILE, "wb") as f:
        pickle.dump(g2_dist, f)

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

def generate_g2_database() -> list[int]:
    """Use Breadth First Search algorithm to compute distance to G3 state."""
    MAX_STATE = 29_400
    result = [-1] * MAX_STATE
    solved: Cube = replace(SOLVED)
    queue = deque([(replace(SOLVED), 0)])
    index = cube_g2_index(solved)
    visited = {index}
    result[index] = 0

    while queue and len(visited) < MAX_STATE:
        cube: Cube
        count: int
        cube, count = queue.popleft()

        for move in G2_MOVES:
            cube_next = replace(cube)
            cube_next.turn(move)
            index = cube_g2_index(cube_next)

            if index not in visited:
                visited.add(index)
                result[index] = count + 1
                queue.append((cube_next, count + 1))

    return result


if __name__ == "__main__":
    print("Generating G2 database...")
    g2_dist = generate_g2_database()
    save_database(g2_dist)
    print("Reached states:", len([i for i in g2_dist if i > -1]))
    print("Max moves:", max(g2_dist))
