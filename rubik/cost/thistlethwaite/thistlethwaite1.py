"""Calculations related to the Thistlethwaite G1 algorithm."""
from functools import partial
import math

from .common import (
    CORNER_TYPE,
    G1_FILE,
    EDGES,
    EDGE_PIECES,
    CORNERS,
    generate_database,
    save_database as _save_database,
    load_database,
)
from ..common import get_colour
from ...cube import Cube, Colour, SOLVED


G1_MAX_STATE = 1_082_565
G1_DIST: list[int] | None = None

LR_COLOURS = {Colour.B.value, Colour.G.value}   # R face is blue, L is green
M_PIECES: set[frozenset[int]] = set(EDGE_PIECES[4:8])

G1_MOVES = [
    'L', 'R', 'F', 'B',
    "L'", "R'", "F'", "B'",
    'U2', 'D2', 'L2', 'R2', 'F2', 'B2'
]


def corner_orientation(
        cube: Cube,
        corner: CORNER_TYPE
        ) -> int:
    """Return the orientation of a corner."""
    colour = [get_colour(cube, *tile) for tile in corner]

    for (i, col) in enumerate(colour):
        if col in LR_COLOURS:
            return i
    else:
        raise ValueError("Corner piece is missing L or R colour tile.")

def cube_corner_orientation(cube: Cube) -> list[int]:
    """Return a list containing the orientation of each corner."""
    return [corner_orientation(cube, corner) for corner in CORNERS]

def cube_M_indices(cube: Cube) -> list[int]:
    """Return the sorted indices of the M slice pieces."""
    result = []
    for i, edge in enumerate(EDGES):
        colour = frozenset(get_colour(cube, *tile) for tile in edge)
        if colour in M_PIECES:
            result.append(i)
    return result

def cube_g1_index(cube: Cube) -> int:
    """Return a unique index between 0 to 1,082,564 for G1 state

    Combine corner orientations (0-2186) and E-slice combinations (0-494).
    """
    index_corner = cube_corner_orientation(cube)
    index_M = cube_M_indices(cube)
    result = 0
    for i, val in enumerate(index_corner[:-1]):
        result += val * 3**i
    combo = 0
    for i, val in enumerate(index_M, start=1):
        combo += math.comb(val, i)
    return result * 495 + combo

generate_g1_database = partial(
    generate_database, cube_g1_index, G1_MAX_STATE, G1_MOVES)

save_database = partial(_save_database, G1_FILE)

def read_database_1() -> None:
    """Read the Thistlethwaite G1 distance database from file."""
    global G1_DIST
    G1_DIST = load_database(G1_FILE, generate_g1_database)


if __name__ == "__main__":
    print("Generating G1 database...")
    g1_dist = generate_g1_database()
    save_database(g1_dist)
    print("Reached states:", len([i for i in g1_dist if i > -1]))
    print("Max moves:", max(g1_dist))
