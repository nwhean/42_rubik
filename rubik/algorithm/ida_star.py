"""Implementation of the Iterative Deepening A* (IDA) Search Algorithm."""
from math import inf
from typing import Callable

from ..state import State


def ida_star(
        start: State,
        goal: State,
        h_cost: Callable[[State, State], float]
    ) -> tuple[list[State], float]:
    """Returns the path from start to goal using IDA* Search Algorithm.

    Args:
    start  - origin state
    goal   - target destination state.
    h_cost - heuristic function estimating remaining cost from a state to goal.
    """
    bound: float = h_cost(start, goal)
    path: dict[State, None] = {start: None}

    while True:
        val: float = search(goal, path, bound, 0.0, h_cost)
        if val == 0.0:  # the goal is reached
            return list(path.keys()), bound
        if val == inf:  # the goal is not reached
            raise RuntimeError("No solution path found.")
        bound = val

def search(
        goal: State,
        path: dict[State, None],
        bound: float,
        g_cost: float,
        h_cost: Callable[[State, State], float]
    ) -> float:
    """Search function called by IDA* Search Algorithm

    Args:
    goal   - target destination state.
    path   - ordered dictionary acting as current branch stack and visited set.
    g_cost - the cost to reach current state
    bound  - current f-cost threshold for pruning branches.
    h_cost - heuristic function estimating remaining cost from a state to goal.
    """
    current = next(reversed(path))  # get the last inserted state

    # estimated cost of the cheapest path, from start to goal via current
    f_cost = g_cost + h_cost(current, goal)

    # prune branch if cost exceeds current threshold
    if f_cost > bound:
        return f_cost

    # destination reached within current bound
    if current == goal:
        return 0.0

    min_val: float = inf

    for state in current.successors():
        if state not in path:
            path[state] = None
            val = search(goal, path, bound, g_cost + 1.0, h_cost)
            if val == 0.0:
                return 0.0
            if val < min_val:
                min_val = val

            # remove last item from path and cache
            path.popitem()

    return min_val
