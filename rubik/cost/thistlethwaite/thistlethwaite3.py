"""Calculations related to the Thistlethwaite G3 algorithm."""
from functools import partial
import math
import pickle

from .common import Tile, BASE_DIR, generate_database
from ..common import get_colour
from ...cube import Cube, Colour


G3_MAX_STATE = 663_552
G3_FILE = BASE_DIR / "G3_distance.pickle"
G3_DIST: list[int] | None = None

EDGE_TYPE = tuple[Tile, Tile]
CORNER_TYPE = tuple[Tile, Tile, Tile]
SLICE_TYPE = list[EDGE_TYPE]
TETRAD_TYPE = list[CORNER_TYPE]

EDGES: list[SLICE_TYPE] = [
    [
        (("U", 3), ("R", 7)),   # UR
        (("D", 5), ("R", 3)),   # DR
        (("D", 1), ("L", 5)),   # DL
        (("U", 7), ("L", 1)),   # UL
    ],
    [
        (("F", 1), ("U", 5)),   # FU
        (("B", 7), ("U", 1)),   # BU
        (("B", 3), ("D", 7)),   # BD
        (("F", 5), ("D", 3)),   # FD
    ],
    [
        (("F", 3), ("R", 5)),   # FR
        (("F", 7), ("L", 3)),   # FL
        (("B", 1), ("L", 7)),   # BL
        (("B", 5), ("R", 1)),   # BR
    ],
]

S_PIECES: list[frozenset[int]] = [
    frozenset({Colour.W.value, Colour.B.value}),    # UR
    frozenset({Colour.Y.value, Colour.B.value}),    # DR
    frozenset({Colour.Y.value, Colour.G.value}),    # DL
    frozenset({Colour.W.value, Colour.G.value}),    # UL
]

M_PIECES: list[frozenset[int]] = [
    frozenset({Colour.R.value, Colour.W.value}),    # FU
    frozenset({Colour.O.value, Colour.W.value}),    # BU
    frozenset({Colour.O.value, Colour.Y.value}),    # BD
    frozenset({Colour.R.value, Colour.Y.value}),    # FD
]

E_PIECES: list[frozenset[int]] = [
    frozenset({Colour.R.value, Colour.B.value}),    # FR
    frozenset({Colour.R.value, Colour.G.value}),    # FL
    frozenset({Colour.O.value, Colour.G.value}),    # BL
    frozenset({Colour.O.value, Colour.B.value}),    # BR
]

EDGE_INDICES = [
    {frozenset(colours): i for i, colours in enumerate(S_PIECES)},
    {frozenset(colours): i for i, colours in enumerate(M_PIECES)},
    {frozenset(colours): i for i, colours in enumerate(E_PIECES)},
]

CORNERS: list[TETRAD_TYPE] = [
    [
        (("F", 4), ("R", 4), ("D", 4)),     # FRD
        (("F", 0), ("L", 2), ("U", 6)),     # FLU
        (("B", 2), ("L", 6), ("D", 0)),     # BLD
        (("B", 6), ("R", 0), ("U", 2)),     # BRU
    ],
    [
        (("F", 2), ("U", 4), ("R", 6)),     # FUR
        (("F", 6), ("D", 2), ("L", 4)),     # FDL
        (("B", 0), ("U", 0), ("L", 0)),     # BUL
        (("B", 4), ("D", 6), ("R", 2)),     # BDR
    ],
]

TETRAD_0: list[frozenset[int]] = [
    frozenset({Colour.R.value, Colour.B.value, Colour.Y.value}),   # FRD
    frozenset({Colour.R.value, Colour.G.value, Colour.W.value}),   # FLU
    frozenset({Colour.O.value, Colour.G.value, Colour.Y.value}),   # BLD
    frozenset({Colour.O.value, Colour.B.value, Colour.W.value}),   # BRU
]

TETRAD_1: list[frozenset[int]] = [
    frozenset({Colour.R.value, Colour.B.value, Colour.W.value}),   # FRU
    frozenset({Colour.R.value, Colour.G.value, Colour.Y.value}),   # FLD
    frozenset({Colour.O.value, Colour.G.value, Colour.W.value}),   # BLU
    frozenset({Colour.O.value, Colour.B.value, Colour.Y.value}),   # BRD
]

CORNER_INDICES: list[dict[frozenset[int], int]] = [
    {frozenset(colours): i for i, colours in enumerate(TETRAD_0)},
    {frozenset(colours): i for i, colours in enumerate(TETRAD_1)},
]

G3_MOVES = ['U2', 'D2', 'L2', 'R2', 'F2', 'B2']

def read_database() -> None:
    """Read the Thistlethwaite G3 distance database from file."""
    global G3_DIST
    try:
        with open(G3_FILE, "rb") as f:
            G3_DIST = pickle.load(f)

    except FileNotFoundError:
        G3_DIST = generate_g3_database()
        save_database(G3_DIST)

def save_database(g3_dist: list[int]) -> None:
    """Save the G3 distance database to files."""
    # Create the directory if it doesn't exist
    G3_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(G3_FILE, "wb") as f:
        pickle.dump(g3_dist, f)

def edge_indices(cube: Cube, group_idx: int) -> list[int]:
    """Return a list containing the indices of S, M or E edges."""
    result = []
    for i, edge in enumerate(EDGES[group_idx]):
        colour = frozenset(get_colour(cube, *tile) for tile in edge)
        result.append(EDGE_INDICES[group_idx][colour])
    return result

def corner_indices(cube: Cube, group_idx: int) -> list[int]:
    """Return a list containing the indices of tetrad_0 or tetrad_1 corners."""
    result = []
    for i, corner in enumerate(CORNERS[group_idx]):
        colour = frozenset(get_colour(cube, *tile) for tile in corner)
        result.append(CORNER_INDICES[group_idx][colour])
    return result

def rank_permutation(perm: list[int]) -> int:
    """Return the rank of a 0-indexed list of indices."""
    n: int = len(perm)
    rank: int = 0

    for i, val in enumerate(perm, start=1):
        smaller_count = len([j for j in perm[i:] if j < val])
        rank += smaller_count * math.factorial(n - i)

    return rank

def cube_g3_index(cube: Cube) -> int:
    """Return a unique index between 0 to 663_551 for G3 state

    Combine the following:
    - tetrad_0 permutations = 4! = 24
    - reduced tetrad_1 permutations = 4
    - S edges permutations = 4! = 24
    - M edges permutations = 4! = 24
    - reduces M edges permutations = 12
    for a total of 24 x 4 x 24 x 24 x 12 = 663,552 states.
    """
    tetrad_0_indices = corner_indices(cube, 0)
    tetrad_1_indices = corner_indices(cube, 1)
    edge_s_indices = edge_indices(cube, 0)
    edge_m_indices = edge_indices(cube, 1)
    edge_e_indices = edge_indices(cube, 2)

    tetrad_0_rank = rank_permutation(tetrad_0_indices)
    tetrad_1_rank = rank_permutation(tetrad_1_indices)
    edge_s_rank = rank_permutation(edge_s_indices)
    edge_m_rank = rank_permutation(edge_m_indices)
    edge_e_rank = rank_permutation(edge_e_indices)

    result = ((((tetrad_0_rank * 4 + tetrad_1_rank // 6)
                * 24 + edge_s_rank)
               * 24 + edge_m_rank)
              * 12 + edge_e_rank // 2)
    if result >= 663_552:
        raise ValueError()
    return result

generate_g3_database = partial(
    generate_database, cube_g3_index, G3_MAX_STATE, G3_MOVES)


if __name__ == "__main__":
    print("Generating G3 database...")
    g3_dist = generate_g3_database()
    save_database(g3_dist)
    print("Reached states:", len([i for i in g3_dist if i > -1]))
    print("Max moves:", max(g3_dist))
