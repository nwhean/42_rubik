"""Codes used by Thistlethwaite files"""
from collections import deque
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
import pickle
import sys

from ...cube import Cube, Colour, SOLVED


Tile = tuple[str, int]
EDGE_TYPE = tuple[Tile, Tile]
CORNER_TYPE = tuple[Tile, Tile, Tile]

BASE_DIR = Path(__file__).parent / "thistlethwaite_database"
G0_FILE = BASE_DIR / "G0_distance.pickle"
G1_FILE = BASE_DIR / "G1_distance.pickle"
G2_FILE = BASE_DIR / "G2_distance.pickle"
G3_FILE = BASE_DIR / "G3_distance.pickle"

EDGES: list[EDGE_TYPE] = [
    (("U", 3), ("R", 7)),   # UR - S group
    (("D", 5), ("R", 3)),   # DR - S group
    (("D", 1), ("L", 5)),   # DL - S group
    (("U", 7), ("L", 1)),   # UL - S group
    (("F", 1), ("U", 5)),   # FU - M group
    (("B", 7), ("U", 1)),   # BU - M group
    (("B", 3), ("D", 7)),   # BD - M group
    (("F", 5), ("D", 3)),   # FD - M group
    (("F", 3), ("R", 5)),   # FR - E group
    (("F", 7), ("L", 3)),   # FL - E group
    (("B", 1), ("L", 7)),   # BL - E group
    (("B", 5), ("R", 1)),   # BR - E group
]

EDGE_PIECES: list[frozenset[int]] = [
    frozenset({Colour.W.value, Colour.B.value}),    # UR
    frozenset({Colour.Y.value, Colour.B.value}),    # DR
    frozenset({Colour.Y.value, Colour.G.value}),    # DL
    frozenset({Colour.W.value, Colour.G.value}),    # UL
    frozenset({Colour.R.value, Colour.W.value}),    # FU
    frozenset({Colour.O.value, Colour.W.value}),    # BU
    frozenset({Colour.O.value, Colour.Y.value}),    # BD
    frozenset({Colour.R.value, Colour.Y.value}),    # FD
    frozenset({Colour.R.value, Colour.B.value}),    # FR
    frozenset({Colour.R.value, Colour.G.value}),    # FL
    frozenset({Colour.O.value, Colour.G.value}),    # BL
    frozenset({Colour.O.value, Colour.B.value}),    # BR
]

CORNERS: list[CORNER_TYPE] = [
    (("F", 4), ("R", 4), ("D", 4)),     # FRD - tetrad 0
    (("F", 0), ("L", 2), ("U", 6)),     # FLU - tetrad 0
    (("B", 2), ("L", 6), ("D", 0)),     # BLD - tetrad 0
    (("B", 6), ("R", 0), ("U", 2)),     # BRU - tetrad 0
    (("F", 2), ("U", 4), ("R", 6)),     # FUR - tetrad 1
    (("F", 6), ("D", 2), ("L", 4)),     # FDL - tetrad 1
    (("B", 0), ("U", 0), ("L", 0)),     # BUL - tetrad 1
    (("B", 4), ("D", 6), ("R", 2)),     # BDR - tetrad 1
]

CORNER_PIECES: list[frozenset[int]] = [
    frozenset({Colour.R.value, Colour.B.value, Colour.Y.value}),   # FRD
    frozenset({Colour.R.value, Colour.G.value, Colour.W.value}),   # FLU
    frozenset({Colour.O.value, Colour.G.value, Colour.Y.value}),   # BLD
    frozenset({Colour.O.value, Colour.B.value, Colour.W.value}),   # BRU
    frozenset({Colour.R.value, Colour.W.value, Colour.B.value}),   # FUR
    frozenset({Colour.R.value, Colour.Y.value, Colour.G.value}),   # FDL
    frozenset({Colour.O.value, Colour.W.value, Colour.G.value}),   # BUL
    frozenset({Colour.O.value, Colour.Y.value, Colour.B.value}),   # BDR
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

def load_database(
        filepath: Path,
        generate_func: Callable[[], list[int]]
    ) -> list[int]:
    """Read the Thistlethwaite distance database from file."""
    try:
        with open(filepath, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        dist = generate_func()
        save_database(filepath, dist)
        return dist
