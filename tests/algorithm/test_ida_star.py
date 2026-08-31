"""Unit tests for the IDA* search algorithm."""
import unittest

from rubik.algorithm.ida_star import ida_star
from rubik.state import State


class MockNode:
    """Mock implementation of the State protocol using an explicit graph dictionary."""

    def __init__(self, name: str, graph: dict[str, list[str]] | None = None):
        self.name = name
        self.graph = graph or {}

    def successors(self) -> list[State]:
        return [MockNode(neighbor, self.graph)
                for neighbor in self.graph.get(self.name, [])]

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MockNode):
            return False
        return self.name == other.name

    def __repr__(self) -> str:
        return f"Node({self.name})"


def zero_heuristic(start: State, goal: State) -> float:
    """Admissible zero heuristic (equivalent to IDDFS search)."""
    return 0.0


def numeric_distance_heuristic(start: State, goal: State) -> float:
    """Sample heuristic for integer-named nodes using absolute difference."""
    try:
        return abs(float(getattr(start, "name")) - float(getattr(goal, "name")))
    except ValueError:
        return 0.0


class TestIDAStar(unittest.TestCase):
    """Test suite for ida_star function."""

    def test_start_equals_goal(self):
        """Test search when start state is already the goal."""
        start = MockNode("A")
        goal = MockNode("A")
        path, bound = ida_star(start, goal, zero_heuristic)

        self.assertEqual(path, [start])
        self.assertEqual(bound, 0.0)

    def test_linear_path(self):
        """Test direct path resolution without branching (A -> B -> C)."""
        graph = {"A": ["B"], "B": ["C"], "C": []}
        start = MockNode("A", graph)
        goal = MockNode("C", graph)

        path, bound = ida_star(start, goal, zero_heuristic)

        self.assertEqual([node.name for node in path], ["A", "B", "C"])
        self.assertEqual(bound, 2.0)

    def test_branching_and_backtracking(self):
        """Test that the algorithm prunes dead ends and backtracks correctly."""
        graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["E"],
            "D": [],
            "E": [],
        }
        start = MockNode("A", graph)
        goal = MockNode("E", graph)

        path, bound = ida_star(start, goal, zero_heuristic)

        self.assertEqual([node.name for node in path], ["A", "C", "E"])
        self.assertEqual(bound, 2.0)

    def test_cycle_prevention(self):
        """Test that cyclic graphs (A -> B -> A) do not trigger infinite loops."""
        graph = {
            "A": ["B"],
            "B": ["A", "C"],
            "C": [],
        }
        start = MockNode("A", graph)
        goal = MockNode("C", graph)

        path, bound = ida_star(start, goal, zero_heuristic)

        self.assertEqual([node.name for node in path], ["A", "B", "C"])

    def test_unreachable_goal(self):
        """Test that searching an unreachable graph raises RuntimeError."""
        graph = {"A": ["B"], "B": []}
        start = MockNode("A", graph)
        goal = MockNode("Z", graph)

        with self.assertRaises(RuntimeError):
            ida_star(start, goal, zero_heuristic)

    def test_heuristic_pruning(self):
        """Test search behavior with a non-zero admissible heuristic."""
        graph = {
            "1": ["2", "10"],
            "2": ["3"],
            "3": [],
            "10": [],
        }
        start = MockNode("1", graph)
        goal = MockNode("3", graph)

        path, bound = ida_star(start, goal, numeric_distance_heuristic)

        self.assertEqual([node.name for node in path], ["1", "2", "3"])
