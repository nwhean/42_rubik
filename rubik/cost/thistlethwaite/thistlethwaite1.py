"""Calculations related to the Thistlethwaite G1 algorithm."""
from functools import partial
import math
import pickle

from .common import (
    Tile,
    BASE_DIR,
    FB_COLOURS,
    EDGES,
    CORNERS,
    generate_database,
)
from ..common import get_colour
from ...cube import Cube, Colour, SOLVED


G1_MAX_STATE = 1_082_565
G1_FILE = BASE_DIR / "G1_distance.pickle"
G1_DIST: list[int] | None = None

E_PIECES: set[frozenset[int]] = {
    frozenset({Colour.R.value, Colour.G.value}),   # FL
    frozenset({Colour.G.value, Colour.O.value}),   # BL
    frozenset({Colour.O.value, Colour.B.value}),   # BR
    frozenset({Colour.B.value, Colour.R.value}),   # FR
}

G1_MOVES = [
    'L', 'R', 'F', 'B',
    "L'", "R'", "F'", "B'",
    'U2', 'D2', 'L2', 'R2', 'F2', 'B2'
]

def read_database() -> None:
    """Read the Thistlethwaite G1 distance database from file."""
    global G1_DIST
    try:
        with open(G1_FILE, "rb") as f:
            G1_DIST = pickle.load(f)

    except FileNotFoundError:
        G1_DIST = generate_g1_database()
        save_database(G1_DIST)

def save_database(g1_dist: list[int]) -> None:
    """Save the G1 distance database to files."""
    # Create the directory if it doesn't exist
    G1_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(G1_FILE, "wb") as f:
        pickle.dump(g1_dist, f)

def corner_orientation(
        cube: Cube,
        corner: tuple[Tile, Tile, Tile]
        ) -> int:
    """Return the orientation of a corner."""
    colour = [get_colour(cube, *tile) for tile in corner]

    for (i, col) in enumerate(colour):
        if col in FB_COLOURS:
            return i
    else:
        raise ValueError("Corner piece is missing F or B colour tile.")

def cube_corner_orientation(cube: Cube) -> list[int]:
    """Return a list containing the orientation of each corner."""
    return [corner_orientation(cube, corner) for corner in CORNERS]

def cube_E_indices(cube: Cube) -> list[int]:
    """Return the sorted indices of the E slice pieces."""
    result = []
    for i, edge in enumerate(EDGES):
        colour = frozenset(get_colour(cube, *tile) for tile in edge)
        if colour in E_PIECES:
            result.append(i)
    return result

def cube_g1_index(cube: Cube) -> int:
    """Return a unique index between 0 to 1,082,564 for G1 state

    Combine corner orientations (0-2186) and E-slice combinations (0-494).
    """
    index_corner = cube_corner_orientation(cube)
    index_E = cube_E_indices(cube)
    result = 0
    for i, val in enumerate(index_corner[:-1]):
        result += val * 3**i
    combo = 0
    for i, val in enumerate(index_E, start=1):
        combo += math.comb(val, i)
    return result * 495 + combo

generate_g1_database = partial(
    generate_database, cube_g1_index, G1_MAX_STATE, G1_MOVES)


if __name__ == "__main__":
    print("Generating G1 database...")
    g1_dist = generate_g1_database()
    save_database(g1_dist)
    print("Reached states:", len([i for i in g1_dist if i > -1]))
    print("Max moves:", max(g1_dist))
