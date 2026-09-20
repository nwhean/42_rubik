from dataclasses import replace
import unittest
from unittest.mock import MagicMock, mock_open, patch

from rubik.cost.thistlethwaite.thistlethwaite3 import (
    corner_indices,
    cube_g3_index,
    edge_indices,
    rank_permutation,
    read_database,
    save_database,
)
import rubik.cost.thistlethwaite.thistlethwaite3 as t3
from rubik.cube import SOLVED


TOTAL_G3_STATES = 663_552

class TestThistlethwaite3(unittest.TestCase):
    """Unit tests for Phase 2 (G3 -> G4) Thistlethwaite calculations."""

    def test_solved_cube_corner_indices(self) -> None:
        """A solved cube must have corner indices equal to [0, 1, 2, 3] for both tetrads."""
        solved_cube = replace(SOLVED)

        self.assertEqual(corner_indices(solved_cube, 0), [0, 1, 2, 3])
        self.assertEqual(corner_indices(solved_cube, 1), [0, 1, 2, 3])

    def test_solved_cube_edge_indices(self) -> None:
        """A solved cube must have edge indices equal to [0, 1, 2, 3] for S, M, and E slices."""
        solved_cube = replace(SOLVED)

        self.assertEqual(edge_indices(solved_cube, 0), [0, 1, 2, 3])  # S-slice
        self.assertEqual(edge_indices(solved_cube, 1), [0, 1, 2, 3])  # M-slice
        self.assertEqual(edge_indices(solved_cube, 2), [0, 1, 2, 3])  # E-slice

    def test_rank_permutation_bounds(self) -> None:
        """Combinadic rank must accurately bound combinations."""
        self.assertEqual(rank_permutation([3, 2, 4, 1]), 15)
        self.assertEqual(rank_permutation([1, 2, 3, 4]), 0)
        self.assertEqual(rank_permutation([4, 3, 2, 1]), 23)

    def test_solved_cube_index(self) -> None:
        """The solved cube index must equal 0."""
        solved_cube = replace(SOLVED)
        self.assertEqual(cube_g3_index(solved_cube), 0)

    def test_g3_moves_preserve_valid_range(self) -> None:
        """Applying valid G3 moves must produce indices within [0, TOTAL_G3_STATES - 1]."""
        cube = replace(SOLVED)
        for move in t3.G3_MOVES:
            test_cube = replace(cube)
            test_cube.turn(move)
            idx = cube_g3_index(test_cube)
            self.assertTrue(0 <= idx < TOTAL_G3_STATES)

    @patch("pathlib.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.dump")
    def test_save_database(self, mock_dump: MagicMock, mock_file: MagicMock, mock_mkdir: MagicMock) -> None:
        """save_database should ensure directory exists and pickle dataset."""
        dummy_dist = [0] * TOTAL_G3_STATES
        save_database(dummy_dist)

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file.assert_called_once_with(t3.G3_FILE, "wb")
        mock_dump.assert_called_once_with(dummy_dist, mock_file())
