"""Codes used by Thistlethwaite files"""
from collections import deque
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
import pickle
import sys

from ...cube import Colour, SOLVED


Tile = tuple[str, int]

BASE_DIR = Path(__file__).parent / "thistlethwaite_database"
G0_FILE = BASE_DIR / "G0_distance.pickle"
G1_FILE = BASE_DIR / "G1_distance.pickle"
G2_FILE = BASE_DIR / "G2_distance.pickle"
G3_FILE = BASE_DIR / "G3_distance.pickle"

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

def print_progress_bar(iteration, total, bar_length=50):
    """Print a progress bar."""
    percent = int(100 * (iteration / total))

    # skip the I/O if percent hasn't changed
    last_percent = getattr(print_progress_bar, 'last_percent', None)
    if last_percent == percent and iteration != 0 and iteration != total:
        return

    # store the last percent
    print_progress_bar.last_percent = percent

    filled_length = int(bar_length * iteration // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    # \r moves the cursor back to the start of the line
    sys.stdout.write(f'\rProgress: |{bar}| {percent}% Complete')
    sys.stdout.flush()

    if iteration == total:
        sys.stdout.write('\n')

def generate_database(
        index_func: Callable[[Cube], int],
        max_state: int,
        allowed_moves: list[str]
    ) -> list[int]:
    """Use Breadth First Search algorithm to compute distance database."""
    result = [-1] * max_state
    solved: Cube = replace(SOLVED)
    queue = deque([(replace(SOLVED), 0)])
    index = index_func(solved)
    result[index] = 0
    iteration = 1

    while queue:
        cube: Cube
        count: int
        cube, count = queue.popleft()

        for move in allowed_moves:
            cube_next = replace(cube)
            cube_next.turn(move)
            index = index_func(cube_next)

            if result[index] == -1:
                iteration += 1
                print_progress_bar(iteration, max_state)
                result[index] = count + 1
                queue.append((cube_next, count + 1))

    return result

def save_database(filepath: Path, dist: list[int]) -> None:
    """Save a distance database list to file."""
    # Create the directory if it doesn't exist
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "wb") as f:
        pickle.dump(dist, f)
