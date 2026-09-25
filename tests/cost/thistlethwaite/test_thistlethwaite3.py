from dataclasses import replace
import unittest
from unittest.mock import MagicMock, mock_open, patch

from rubik.cost.thistlethwaite.thistlethwaite3 import (
    G3_MAX_STATE,
    corner_indices,
    cube_g3_index,
    edge_indices,
    rank_permutation,
    save_database,
)
from rubik.cost.thistlethwaite.thistlethwaite2 import cube_g2_index
import rubik.cost.thistlethwaite.thistlethwaite3 as t3
from rubik.cube import SOLVED


class TestThistlethwaite3(unittest.TestCase):
    """Unit tests for Phase 3 (G3 -> G4) Thistlethwaite calculations."""

    def test_previous_index(self) -> None:
        """Taking any allowed moves in current phase preserves prior index."""
        solved = replace(SOLVED)
        for move in t3.G3_MOVES:
            cube_0 = replace(solved)
            cube_0.turn(move)
            self.assertEqual(cube_g2_index(solved), cube_g2_index(cube_0))
            for move in t3.G3_MOVES:
                cube_1 = replace(cube_0)
                cube_1.turn(move)
                self.assertEqual(cube_g2_index(solved), cube_g2_index(cube_1))

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
        """Applying valid G3 moves must produce indices within [0, G3_MAX_STATE - 1]."""
        cube = replace(SOLVED)
        for move in t3.G3_MOVES:
            test_cube = replace(cube)
            test_cube.turn(move)
            idx = cube_g3_index(test_cube)
            self.assertTrue(0 <= idx < G3_MAX_STATE)

    @patch("pathlib.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.dump")
    def test_save_database(
            self,
            mock_dump: MagicMock,
            mock_file: MagicMock,
            mock_mkdir: MagicMock
        ) -> None:
        """save_database should ensure directory exists and pickle dataset."""
        dummy_dist = [0] * G3_MAX_STATE
        save_database(dummy_dist)

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file.assert_called_once_with(t3.G3_FILE, "wb")
        mock_dump.assert_called_once_with(dummy_dist, mock_file())
