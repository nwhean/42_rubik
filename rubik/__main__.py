from dataclasses import replace
from typing import Callable

from rubik.algorithm import (
    ida_star,
    thistlethwaite,
)
from rubik.cost import (
    hamming_tile_distance,
    hamming_piece_distance,
    manhattan_distance,
)
from rubik.cube import Colour, Cube, SOLVED


ALGORITHMS: dict[str, Callable] = {
    "ida": ida_star,
    "thistlethwaite": thistlethwaite,
}

COSTS: dict[str, Callable] = {
    "hamming_tile": hamming_tile_distance,
    "hamming_piece": hamming_piece_distance,
    "manhattan": manhattan_distance,
}


def solve(
        node: Cube,
        algo: str,
        cost: str,
        weight: float,
    ) -> tuple[list[Cube], int]:
    """Solve a Rubik's Cube state and return the path and final cost bound."""
    if algo not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm: {algo}")
    if cost not in COSTS:
        raise ValueError(f"Unknown cost heuristic: {cost}")

    func = ALGORITHMS[algo]
    return func(node, SOLVED, COSTS[cost], weight)


if __name__ == "__main__":
    import argparse
    import random
    import sys
    import time

    parser = argparse.ArgumentParser(description="Rubik's Cube Solver")

    parser.add_argument(
        "moves",
        nargs="?",
        default="",
        help="Space-separated scramble moves (e.g. \"R U R' F2\")"
    )

    parser.add_argument(
        "-s", "--scramble", type=int,
        help="Scramble the cube with a specified number of random moves"
    )

    parser.add_argument(
        "-p", "--performance", action="store_true",
        help="Print the solution time and move count"
    )

    parser.add_argument(
        "-a", "--algo", type=str, default="thistlethwaite",
        choices=list(ALGORITHMS.keys()),
        help="search algorithm to be used"
    )

    parser.add_argument(
        "-c", "--cost", type=str, default="manhattan",
        choices=list(COSTS.keys()),
        help="heuristic cost function to be used by solver. "\
            "Default = 'manhattan'"
    )

    parser.add_argument(
        "-w", "--weight", type=float, default=2.5,
        help="weight factor to multiply heuristic cost value. Default = 2.5"
    )

    args = parser.parse_args()

    # Determine the moves to apply
    scramble_moves = []
    if args.scramble:
        faces = ["R", "L", "U", "D", "F", "B"]
        modifiers = ["", "'", "2"]
        last_face = None

        for _ in range(args.scramble):
            # prevent turning the same face twice in a row
            available_faces = [f for f in faces if f != last_face]
            face = random.choice(available_faces)
            modifier = random.choice(modifiers)
            scramble_moves.append(face + modifier)
            last_face = face

        print(f"Generated Scramble: {' '.join(scramble_moves)}")
    else:
        scramble_moves = args.moves.split()

    # scramble the cube
    cube = replace(SOLVED)
    for move in scramble_moves:
        try:
            cube.turn(move)
        except ValueError as err:
            print(f"Invalid scramble move '{move}'", file=sys.stderr)
            sys.exit(1)

    # reset last move so transition table isn't constrained by scramble
    cube._last_move = None

    start_time = time.perf_counter()
    try:
        path, bound = solve(cube, args.algo, args.cost, args.weight)
    except RuntimeError as err:
        print(f"Solver error: {err}", file=sys.stderr)
        sys.exit(1)
    elapsed = time.perf_counter() - start_time

    solution_moves = [state._last_move for state in path[1:]]
    move_count = len(solution_moves)

    if args.performance:
        print(f"Solved in {elapsed:.3f}s ({move_count} moves):")
    print(" ".join(solution_moves))

    # verify that the generated solution actually solves the cube
    verification_cube = replace(cube)
    for move in solution_moves:
        verification_cube.turn(move)

    if verification_cube != SOLVED:
        raise RuntimeError("Verification: FAILED (Cube is NOT solved)")
