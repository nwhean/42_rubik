from dataclasses import replace
import unittest
from unittest.mock import MagicMock, mock_open, patch

from rubik.cost.thistlethwaite.thistlethwaite1 import (
    corner_orientation,
    cube_corner_orientation,
    cube_M_indices,
    cube_g1_index,
    save_database,
)
import rubik.cost.thistlethwaite.thistlethwaite1 as t1
from rubik.cube import SOLVED, Cube


TOTAL_G1_STATES = 1_082_565

class TestThistlethwaite1(unittest.TestCase):
    """Unit tests for Phase 1 (G1 -> G2) Thistlethwaite calculations."""

    def test_solved_cube_corner_orientation(self) -> None:
        """A solved cube must have corner orientations all equal to 0."""
        solved_cube = replace(SOLVED)
        orientations = cube_corner_orientation(solved_cube)

        self.assertEqual(len(orientations), 8)
        self.assertEqual(orientations, [1, 1, 1, 1, 2, 2, 2, 2])

    def test_solved_cube_e_slice_indices(self) -> None:
        """Solved cube E-slice pieces must reside at slots [4, 5, 6, 7]."""
        solved_cube = replace(SOLVED)
        m_indices = cube_M_indices(solved_cube)

        self.assertEqual(m_indices, [4, 5, 6, 7])

    def test_solved_cube_index(self) -> None:
        """The solved cube index should equal 1_062_339."""
        solved_cube = replace(SOLVED)
        self.assertEqual(cube_g1_index(solved_cube), 1_062_339)

    def test_g1_moves_preserve_valid_range(self) -> None:
        """Applying valid G1 moves must produce indices within [0, TOTAL_G1_STATES - 1]."""
        cube = replace(SOLVED)
        for move in t1.G1_MOVES:
            test_cube = replace(cube)
            test_cube.turn(move)
            idx = cube_g1_index(test_cube)
            self.assertTrue(0 <= idx < TOTAL_G1_STATES)

    @patch("pathlib.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.dump")
    def test_save_database(self, mock_dump: MagicMock, mock_file: MagicMock, mock_mkdir: MagicMock) -> None:
        """save_database should ensure directory exists and pickle dataset."""
        dummy_dist = [0] * TOTAL_G1_STATES
        save_database(dummy_dist)

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file.assert_called_once_with(t1.G1_FILE, "wb")
        mock_dump.assert_called_once_with(dummy_dist, mock_file())
