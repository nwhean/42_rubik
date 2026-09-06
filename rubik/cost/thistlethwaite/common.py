"""Codes used by Thistlethwaite files"""
from pathlib import Path

from ...cube import Colour


Tile = tuple[str, int]

BASE_DIR = Path(__file__).parent / "thistlethwaite_database"

FB_COLOURS = {Colour.R.value, Colour.O.value}

# The pair of colour appear such that they are oriented similarly
# An edge is oriented correctly if it does not require a U or B turn,
# or flipped if it requires a U or D turn to be oriented correctly
EDGES: list[tuple[Tile, Tile]] = [
    (("U", 3), ("R", 7)),   # UR - 0
    (("F", 3), ("R", 5)),   # FR - 1
    (("F", 1), ("U", 5)),   # FU - 2
    (("U", 7), ("L", 1)),   # UL - 3
    (("F", 7), ("L", 3)),   # FL - 4
    (("F", 5), ("D", 3)),   # FD - 5
    (("D", 1), ("L", 5)),   # DL - 6
    (("B", 1), ("L", 7)),   # BL - 7
    (("B", 3), ("D", 7)),   # BD - 8
    (("D", 5), ("R", 3)),   # DR - 9
    (("B", 5), ("R", 1)),   # BR - 10
    (("B", 7), ("U", 1)),   # BU - 11
]

CORNERS: list[tuple[Tile, Tile, Tile]] = [
    (("F", 4), ("R", 4), ("D", 4)),     # FRD
    (("F", 2), ("U", 4), ("R", 6)),     # FUR
    (("F", 0), ("L", 2), ("U", 6)),     # FLU
    (("F", 6), ("D", 2), ("L", 4)),     # FDL
    (("B", 0), ("U", 0), ("L", 0)),     # BUL
    (("B", 2), ("L", 6), ("D", 0)),     # BLD
    (("B", 4), ("D", 6), ("R", 2)),     # BDR
    (("B", 6), ("R", 0), ("U", 2)),     # BRU
]
