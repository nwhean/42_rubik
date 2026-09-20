"""Calculations related to the Thistlethwaite G0 algorithm."""
from functools import partial

from .common import (
    Tile,
    EDGE_TYPE,
    BASE_DIR,
    G0_FILE,
    FB_COLOURS,
    EDGES,
    generate_database,
    save_database as _save_database,
    load_database,
)
from ..common import get_colour
from ...cube import Cube, Colour, SOLVED


G0_MAX_STATE = 2_048
G0_DIST: list[int] | None = None

UD_COLOURS = {Colour.W.value, Colour.Y.value}
FB_FACES = {'F', 'B'}
UD_FACES = {'U', 'D'}

G0_MOVES = [
    'U', 'D', 'L', 'R', 'F', 'B',
    "U'", "D'", "L'", "R'", "F'", "B'",
    'U2', 'D2', 'L2', 'R2', 'F2', 'B2'
    ]


def edge_orientation(
        cube: Cube,
        edge: EDGE_TYPE
        ) -> int:
    """Return the orientation of an edge."""
    colour = [get_colour(cube, *tile) for tile in edge]

    # whether the piece contains F or B colours
    is_fb_piece = colour[0] in FB_COLOURS or colour[1] in FB_COLOURS

    # Rule 1: F/B pieces must have F/B sticker facing F or B face
    if is_fb_piece:
        if colour[0] in FB_COLOURS:
            return 0
        return 1

    # Rule 2: U/D pieces must face U/D face AND occupy one of (UR, UL, DR, DL)
    else:
        if colour[0] in UD_COLOURS:
            return 0
        return 1

def cube_edge_orientation(cube: Cube) -> list[int]:
    """Return a list containing the orientation of each edge."""
    return [edge_orientation(cube, edge) for edge in EDGES]

def cube_g0_index(cube: Cube) -> int:
    """Convert edge orientations into an 11-bit index.

    The last orientation is disregarded, as 1 edge cannot be flipped
    independently without affecting the parity of the cube.
    """
    result = 0
    for val in cube_edge_orientation(cube)[:-1]:
        result = (result << 1) | val
    return result

generate_g0_database = partial(
    generate_database,cube_g0_index, G0_MAX_STATE, G0_MOVES)

save_database = partial(_save_database, G0_FILE)

def read_database_0() -> None:
    """Read the Thistlethwaite G0 distance database from file."""
    global G0_DIST
    G0_DIST = load_database(G0_FILE, generate_g0_database)


if __name__ == "__main__":
    print("Generating G0 database...")
    g0_dist = generate_g0_database()
    save_database(g0_dist)
    print("Reached states:", len([i for i in g0_dist if i > -1]))
    print("Max moves:", max(g0_dist))
