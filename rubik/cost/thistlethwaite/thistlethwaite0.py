"""Calculations related to the Thistlethwaite G0 algorithm."""
from functools import partial
import pickle

from .common import Tile, BASE_DIR, FB_COLOURS, EDGES, generate_database
from ..common import get_colour
from ...cube import Cube, Colour, SOLVED


G0_MAX_STATE = 2_048
G0_FILE = BASE_DIR / "G0_distance.pickle"
G0_DIST: list[int] | None = None

UD_COLOURS = {Colour.W.value, Colour.Y.value}
FB_FACES = {'F', 'B'}
UD_FACES = {'U', 'D'}

G0_MOVES = [
    'U', 'D', 'L', 'R', 'F', 'B',
    "U'", "D'", "L'", "R'", "F'", "B'",
    'U2', 'D2', 'L2', 'R2', 'F2', 'B2'
    ]

def read_database() -> None:
    """Read the Thistlethwaite G0 distance database from file."""
    global G0_DIST
    try:
        with open(G0_FILE, "rb") as f:
            G0_DIST = pickle.load(f)

    except FileNotFoundError:
        G0_DIST = generate_g0_database()
        save_database(G0_DIST)

def save_database(g0_dist: list[int]) -> None:
    """Save the G0 distance database to files."""
    # Create the directory if it doesn't exist
    G0_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(G0_FILE, "wb") as f:
        pickle.dump(g0_dist, f)

def edge_orientation(
        cube: Cube,
        edge: tuple[Tile, Tile]
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


if __name__ == "__main__":
    print("Generating G0 database...")
    g0_dist = generate_g0_database()
    save_database(g0_dist)
    print("Reached states:", len([i for i in g0_dist if i > -1]))
    print("Max moves:", max(g0_dist))
