"""Implements to Manhattan Distance heuristics."""
from collections import deque
from dataclasses import replace
from pathlib import Path
import pickle

from .common import (
    SOLVED,
    EDGES,
    EDGE_INDICES,
    CORNERS,
    CORNER_INDICES,
    get_colour,
)
from ..cube import Cube


BASE_DIR = Path(__file__).parent / "manhattan_database"
EDGE_FILE = BASE_DIR / "edge_distance.pickle"
CORNER_FILE = BASE_DIR / "corner_distance.pickle"
EDGE_DIST: dict[tuple[int, int, int], int] | None = None
CORNER_DIST: dict[tuple[int, int, int], int] | None = None


def read_database() -> None:
    """Read the Manhattan distance database from files."""
    global EDGE_DIST, CORNER_DIST
    try:
        with open(EDGE_FILE, "rb") as f:
            EDGE_DIST = pickle.load(f)

        with open(CORNER_FILE, "rb") as f:
            CORNER_DIST = pickle.load(f)

    except FileNotFoundError:
        EDGE_DIST, CORNER_DIST = generate_manhattan_distance()
        save_database(EDGE_DIST, CORNER_DIST)

def save_database(edge_dist: dict[tuple[int, int, int], int],
                  corner_dist: dict[tuple[int, int, int], int]) -> None:
    """Save the Manhattan distance database to files."""
    # Create the directory if it doesn't exist
    EDGE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(EDGE_FILE, "wb") as f:
        pickle.dump(edge_dist, f)

    with open(CORNER_FILE, "wb") as f:
        pickle.dump(corner_dist, f)

def generate_manhattan_distance():
    """Calculates the Manhattan distance between two edge positions."""
    edge_dist: dict[tuple[int, int, int], int] = {}
    corner_dist: dict[tuple[int, int, int], int] = {}

    solved: Cube = replace(SOLVED)
    queue = deque([(replace(SOLVED), 0)])  # (cube, distance)
    visited = {solved}

    max_edges = len(EDGES) ** 2 * 2
    max_corners = len(CORNERS) ** 2 * 3

    while queue \
            and (len(edge_dist) < max_edges or len(corner_dist) < max_corners):
        cube: Cube
        count: int
        cube, count = queue.popleft()

        # Check all edges in the current cube state
        for dest_edge_id, edge in enumerate(EDGES):
            colours = tuple(get_colour(cube, *tile) for tile in edge)
            src_edge_id, orientation = EDGE_INDICES[colours]
            key = (src_edge_id, dest_edge_id, orientation)
            if key not in edge_dist:
                edge_dist[key] = count

        # check all corners in the current cube state
        for dest_corner_id, corner in enumerate(CORNERS):
            colours = tuple(get_colour(cube, *tile) for tile in corner)
            src_corner_id, orientation = CORNER_INDICES[colours]
            key = (src_corner_id, dest_corner_id, orientation)
            if key not in corner_dist:
                corner_dist[key] = count

        for succ in cube.successors():
            if succ not in visited:
                visited.add(succ)
                queue.append((succ, count + 1))

    return edge_dist, corner_dist

def manhattan_distance(start: Cube, goal: Cube = None) -> float:
    """Calculate the admissible Manhattan distance heuristic for IDA*."""
    # Read the database if it hasn't been read yet
    global EDGE_DIST, CORNER_DIST
    if EDGE_DIST is None or CORNER_DIST is None:
        read_database()

    # sum the total manhattan distances for all edges
    edge_h: int = 0
    for dest_edge_id, edge in enumerate(EDGES):
        # for each of the edge, get the start edge id and orientation
        colours = tuple(get_colour(start, *tile) for tile in edge)
        src_edge_id, orientation = EDGE_INDICES[colours]
        edge_h += EDGE_DIST[(src_edge_id, dest_edge_id, orientation)]

    # sum the total manhattan distances for all corners
    corner_h: int = 0
    for dest_corner_id, corner in enumerate(CORNERS):
        colours = tuple(get_colour(start, *tile) for tile in corner)
        src_corner_id, orientation = CORNER_INDICES[colours]
        corner_h += CORNER_DIST[(src_corner_id, dest_corner_id, orientation)]

    return float(max(edge_h / 4, corner_h / 4))


if __name__ == "__main__":
    print("Generating Manhattan distance database...")
    edge_dist, corner_dist = generate_manhattan_distance()

    print("Saving Manhattan distance database...")
    save_database(edge_dist, corner_dist)
