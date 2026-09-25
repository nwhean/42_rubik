from dataclasses import replace
import unittest
from unittest.mock import MagicMock, mock_open, patch

from rubik.cost.thistlethwaite.thistlethwaite1 import (
    G1_MAX_STATE,
    cube_corner_orientation,
    cube_m_indices,
    cube_g1_index,
    save_database,
)
from rubik.cost.thistlethwaite.thistlethwaite0 import cube_g0_index
import rubik.cost.thistlethwaite.thistlethwaite1 as t1
from rubik.cube import SOLVED


class TestThistlethwaite1(unittest.TestCase):
    """Unit tests for Phase 1 (G1 -> G2) Thistlethwaite calculations."""

    def test_previous_index(self) -> None:
        """Taking any allowed moves in current phase preserves prior index."""
        solved = replace(SOLVED)
        for move in t1.G1_MOVES:
            cube_0 = replace(solved)
            cube_0.turn(move)
            self.assertEqual(cube_g0_index(solved), cube_g0_index(cube_0))
            for move in t1.G1_MOVES:
                cube_1 = replace(cube_0)
                cube_1.turn(move)
                self.assertEqual(cube_g0_index(solved), cube_g0_index(cube_1))

    def test_solved_cube_corner_orientation(self) -> None:
        """A solved cube must have corner orientations all equal to 0."""
        solved_cube = replace(SOLVED)
        orientations = cube_corner_orientation(solved_cube)

        self.assertEqual(len(orientations), 8)
        self.assertEqual(orientations, [1, 1, 1, 1, 2, 2, 2, 2])

    def test_solved_cube_e_slice_indices(self) -> None:
        """Solved cube E-slice pieces must reside at slots [4, 5, 6, 7]."""
        solved_cube = replace(SOLVED)
        m_indices = cube_m_indices(solved_cube)

        self.assertEqual(m_indices, [4, 5, 6, 7])

    def test_solved_cube_index(self) -> None:
        """The solved cube index should equal 1_062_339."""
        solved_cube = replace(SOLVED)
        self.assertEqual(cube_g1_index(solved_cube), 1_062_339)

    def test_g1_moves_preserve_valid_range(self) -> None:
        """Applying valid G1 moves must produce indices within [0, G1_MAX_STATE - 1]."""
        cube = replace(SOLVED)
        for move in t1.G1_MOVES:
            test_cube = replace(cube)
            test_cube.turn(move)
            idx = cube_g1_index(test_cube)
            self.assertTrue(0 <= idx < G1_MAX_STATE)

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
        dummy_dist = [0] * G1_MAX_STATE
        save_database(dummy_dist)

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file.assert_called_once_with(t1.G1_FILE, "wb")
        mock_dump.assert_called_once_with(dummy_dist, mock_file())
