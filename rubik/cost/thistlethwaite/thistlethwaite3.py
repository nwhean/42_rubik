"""Calculations related to the Thistlethwaite G3 algorithm."""
from functools import partial
import math

from .common import (
    EdgeType,
    CornerType,
    EDGES,
    EDGE_PIECES,
    CORNERS,
    CORNER_PIECES,
    G3_FILE,
    generate_database,
    save_database as _save_database,
    load_database,
)
from ..common import get_colour
from ...cube import Cube


G3_MAX_STATE = 663_552
G3_DIST: list[int] | None = None

SliceType = list[EdgeType]
TetradType = list[CornerType]

SLICES: list[SliceType] = [
    EDGES[:4],
    EDGES[4:8],
    EDGES[8:]
]

S_PIECES: list[frozenset[int]] = EDGE_PIECES[:4]
M_PIECES: list[frozenset[int]] = EDGE_PIECES[4:8]
E_PIECES: list[frozenset[int]] = EDGE_PIECES[8:]

EDGE_INDICES: list[dict[frozenset[int], int]] = [
    {colours: i for i, colours in enumerate(S_PIECES)},
    {colours: i for i, colours in enumerate(M_PIECES)},
    {colours: i for i, colours in enumerate(E_PIECES)},
]

TETRADS: list[TetradType] = [
    CORNERS[:4],
    CORNERS[4:]
]

TETRAD_0: list[frozenset[int]] = CORNER_PIECES[:4]
TETRAD_1: list[frozenset[int]] = CORNER_PIECES[4:]

CORNER_INDICES: list[dict[frozenset[int], int]] = [
    {colours: i for i, colours in enumerate(TETRAD_0)},
    {colours: i for i, colours in enumerate(TETRAD_1)},
]

G3_MOVES = ['U2', 'D2', 'L2', 'R2', 'F2', 'B2']


def edge_indices(cube: Cube, group_idx: int) -> list[int]:
    """Return a list containing the indices of S, M or E edges."""
    result = []
    for edge in SLICES[group_idx]:
        colour = frozenset(get_colour(cube, *tile) for tile in edge)
        result.append(EDGE_INDICES[group_idx][colour])
    return result

def corner_indices(cube: Cube, group_idx: int) -> list[int]:
    """Return a list containing the indices of tetrad_0 or tetrad_1 corners."""
    result = []
    for corner in TETRADS[group_idx]:
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

save_database = partial(_save_database, G3_FILE)

def read_database_3() -> None:
    """Read the Thistlethwaite G3 distance database from file."""
    global G3_DIST
    G3_DIST = load_database(G3_FILE, generate_g3_database)


if __name__ == "__main__":
    print("Generating G3 database...")
    g3_dist = generate_g3_database()
    save_database(g3_dist)
    print("Reached states:", len([i for i in g3_dist if i > -1]))
    print("Max moves:", max(g3_dist))
