"""Implement the hamming distance heuristics."""
import math

from .common import EDGES, CORNERS, get_colour
from ..cube import Cube

def _different_bytes(a: int, b: int) -> int:
    """Return the number of bytes which are different in values `a` and `b`."""
    xor: int = a ^ b
    result: int = 0
    while xor:
        if xor & 0xFF:
            result += 1
        xor >>= 8
    return result

def hamming_tile_distance(start: Cube, goal: Cube) -> float:
    """Calculate the admissible tile Hamming distance heuristic for IDA*."""
    result: int = 0
    for face in ("R", "L", "U", "D", "F", "B"):
        result += _different_bytes(getattr(start, face), getattr(goal, face))
    return float(math.ceil(result / 20.0))    # single turn changes 20 tiles

def hamming_piece_distance(start: Cube, goal: Cube) -> float:
    """Calculate the admissible piece Hamming distance heuristic for IDA*."""
    bad_corners: int = 0
    for corner in CORNERS:
        for tile in corner:
            if (get_colour(start, *tile) != get_colour(goal, *tile)):
                bad_corners += 1
                break

    bad_edges: int = 0
    for edge in EDGES:
        for tile in edge:
            if (get_colour(start, *tile) != get_colour(goal, *tile)):
                bad_edges += 1
                break

    corner_h: int = math.ceil(bad_corners / 4.0)    # each turn moves 4 corner
    edge_h: int = math.ceil(bad_edges / 4.0)        # each turn moves 4 edges
    return float(max(corner_h, edge_h))
