"""Implement the hamming distance heuristics."""
from ..cube import Cube

def different_bytes(a: int, b: int) -> int:
    """Return the number of bytes which are different in values `a` and `b`."""
    xor: int = a ^ b
    result: int = 0
    while xor:
        if xor & 0xFF:
            result += 1
        xor >>= 8
    return result

def hamming_distance(start: Cube, goal: Cube) -> float:
    """Calculate the admissible tile Hamming distance heuristic for IDA*."""
    result: int = 0
    for face in ("R", "L", "U", "D", "F", "B"):
        result += different_bytes(getattr(start, face), getattr(goal, face))
    return result / 20.0    # single turn changes 20 tiles
