"""Implement the Thistlethwaite algorithm."""
from dataclasses import replace
from typing import Callable

from ..cost.thistlethwaite import PHASE_MOVES, INDICE_FUNC, PHASE_DIST
from ..cube import Cube


def thistlethwaite(
        start: Cube,
        _goal: Cube,
        _h_cost: Callable[[Cube, Cube], float],
        _weight: float
    ) -> tuple[list[Cube], int]:
    """Run the Thistlethwaite solver to find a path to the solved state."""
    path = [start]
    current_cube = start

    for moves, func, dist in zip(PHASE_MOVES, INDICE_FUNC, PHASE_DIST):
        while True:
            idx = func(current_cube)
            current_d = dist[idx]

            # Phase is solved, move to the next phase
            if current_d == 0:
                break

            target_d = current_d - 1

            # Pick the first optimal move and apply it
            for move in moves:
                next_cube = replace(current_cube)
                next_cube.turn(move)
                if dist[func(next_cube)] == target_d:
                    current_cube = next_cube
                    path.append(current_cube)
                    break

    return path, len(path) - 1
