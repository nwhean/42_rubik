"""Contains information that is used by multiple cost functions."""
from ..cube import Colour, Cube, SOLVED


# maps colour to face
COLOUR_FACE_MAP: dict[Colour, str] = {
    Colour.B: 'R',
    Colour.G: 'L',
    Colour.W: 'U',
    Colour.Y: 'D',
    Colour.R: 'F',
    Colour.O: 'B'
}

def get_colour(cube: Cube, face: str, index: int) -> int:
    """Extract the tile raw color value (0-5) at a specific face index."""
    tiles: int = getattr(cube, face)
    return (tiles >> (index * 8)) & 0xFF

# The pair of colour appear such that they are oriented similarly
# An edge is oriented correctly if it does not require a F or B,
# or flipped if it requires a F or B turn to be oriented correctly
EDGES: list[tuple[tuple[str, int], tuple[str, int]]] = [
    (("R", 7), ("U", 3)),   # RU - 0
    (("R", 5), ("F", 3)),   # RF - 1
    (("F", 1), ("U", 5)),   # FU - 2
    (("L", 1), ("U", 7)),   # LU - 3
    (("L", 3), ("F", 7)),   # LF - 4
    (("F", 5), ("D", 3)),   # FD - 5
    (("L", 5), ("D", 1)),   # LD - 6
    (("L", 7), ("B", 1)),   # LB - 7
    (("B", 3), ("D", 7)),   # BD - 8
    (("R", 3), ("D", 5)),   # RD - 9
    (("R", 1), ("B", 5)),   # RB - 10
    (("B", 7), ("U", 1)),   # BU - 11
]

# Maps an edge to its (index, orientation)
EDGE_INDICES: dict[tuple[Colour, Colour], tuple[int, int]] = {}
for index, tiles in enumerate(EDGES):
    colours = tuple(get_colour(SOLVED, *tile) for tile in tiles)
    EDGE_INDICES[colours] = (index, 0)
    EDGE_INDICES[(colours[1], colours[0])] = (index, 1)

# Similar to edges, order of priority is LR, then ordered clockwise from face
CORNERS = [
    (("R", 4), ("D", 4), ("F", 4)),     # RDF
    (("R", 6), ("F", 2), ("U", 4)),     # RFU
    (("L", 2), ("U", 6), ("F", 0)),     # LUF
    (("L", 4), ("F", 6), ("D", 2)),     # LFD
    (("L", 0), ("B", 0), ("U", 0)),     # LBU
    (("L", 6), ("D", 0), ("B", 2)),     # LDB
    (("R", 2), ("B", 4), ("D", 6)),     # RBD
    (("R", 0), ("U", 2), ("B", 6)),     # RUB
]

CORNER_INDICES: dict[tuple[Colour, Colour, Colour], tuple[int, int]] = {}
for index, tiles in enumerate(CORNERS):
    colours = tuple(get_colour(SOLVED, *tile) for tile in tiles)
    CORNER_INDICES[colours] = (index, 0)
    CORNER_INDICES[(colours[1], colours[2], colours[0])] = (index, 1)
    CORNER_INDICES[(colours[2], colours[0], colours[1])] = (index, 2)
