"""Unit tests for the Manhattan distance heuristic and database functions."""
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rubik.cost.common import SOLVED
from rubik.cost.manhattan import (
    generate_manhattan_distance,
    manhattan_distance,
    read_database,
    save_database,
)


class TestManhattanDistance(unittest.TestCase):
    """Test suite for Manhattan distance calculation and persistence."""

    def test_identical_cubes(self):
        """Test that identical cubes return a distance of 0.0."""
        self.assertEqual(manhattan_distance(SOLVED, SOLVED), 0.0)

    def test_single_turn_distance(self):
        """Test distance on a single face turn is admissible (<= 1.0)."""
        scrambled = replace(SOLVED)
        scrambled.turn("R")
        h = manhattan_distance(scrambled, SOLVED)
        self.assertGreater(h, 0.0)
        self.assertLessEqual(h, 1.0)

    def test_multi_turn_admissibility(self):
        """Test that the heuristic value never exceeds actual move depth."""
        scrambled = replace(SOLVED)
        moves = ["R", "U", "F", "D'", "L2", "B"]

        for depth, move in enumerate(moves, start=1):
            scrambled.turn(move)
            h = manhattan_distance(scrambled, SOLVED)
            self.assertLessEqual(h, depth)

    def test_database_generation(self):
        """Test that generate_manhattan_distance produces non-empty lookup tables."""
        edge_dist, corner_dist = generate_manhattan_distance()

        self.assertGreater(len(edge_dist), 0)
        self.assertGreater(len(corner_dist), 0)

        # Verify 3D structure of the distance tables
        self.assertEqual(len(edge_dist), 12)
        self.assertEqual(len(edge_dist[0]), 12)
        self.assertEqual(len(edge_dist[0][0]), 2)

        # Verify 3D structure of the corner distance tables
        self.assertEqual(len(corner_dist), 8)
        self.assertEqual(len(corner_dist[0]), 8)
        self.assertEqual(len(corner_dist[0][0]), 3)

    def test_save_and_read_database(self):
        """Test saving and reading database files from disk using a temporary directory."""
        edge_dist, corner_dist = generate_manhattan_distance()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            edge_file = tmp_path / "edge_distance.pickle"
            corner_file = tmp_path / "corner_distance.pickle"

            with patch("rubik.cost.manhattan.EDGE_FILE", edge_file), \
                 patch("rubik.cost.manhattan.CORNER_FILE", corner_file), \
                 patch("rubik.cost.manhattan.BASE_DIR", tmp_path):

                save_database(edge_dist, corner_dist)

                self.assertTrue(edge_file.exists())
                self.assertTrue(corner_file.exists())

                # Reset cached module globals and test loading
                with patch("rubik.cost.manhattan.EDGE_DIST", None), \
                     patch("rubik.cost.manhattan.CORNER_DIST", None):
                    read_database()
                    import rubik.cost.manhattan as m
                    self.assertIsNotNone(m.EDGE_DIST)
                    self.assertIsNotNone(m.CORNER_DIST)

    def test_edge_distances(self):
        """Test that edge distances are consistent with the database."""
        edge_dist, _ = generate_manhattan_distance()

        # pre-calculate the expected distances for specific edge configurations
        # source index = 0
        # destination indices = 0-11, orientation = 0 or 1
        targets = [
            (0, 3),
            (1, 2),
            (1, 2),
            (1, 3),
            (2, 2),
            (2, 2),
            (2, 3),
            (2, 2),
            (2, 2),
            (1, 3),
            (1, 2),
            (1, 2),
        ]

        for target_id, vals in enumerate(targets):
            for i, val in enumerate(vals):
                self.assertEqual(edge_dist[0][target_id][i], val)

    def test_corner_distances(self):
        """Test that corner distances are consistent with the database."""
        _, corner_dist = generate_manhattan_distance()

        # pre-calculate the expected distances for specific corner configurations
        # source index = 0
        # destination indices = 0-7, orientation = 0, 1, or 2
        targets = [
            (0, 2, 2),
            (1, 1, 2),
            (1, 2, 2),
            (2, 1, 1),
            (2, 2, 2),
            (1, 2, 2),
            (1, 2, 1),
            (1, 2, 2),
        ]

        for target_id, vals in enumerate(targets):
            for i, val in enumerate(vals):
                self.assertEqual(corner_dist[0][target_id][i], val)
