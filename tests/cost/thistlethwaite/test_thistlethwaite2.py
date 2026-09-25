from dataclasses import replace
import unittest
from unittest.mock import MagicMock, mock_open, patch

from rubik.cost.thistlethwaite.thistlethwaite2 import (
    G2_MAX_STATE,
    cube_e_indices,
    cube_g2_index,
    rank_combination,
    save_database,
    tetrad_0_indices,
)
from rubik.cost.thistlethwaite.thistlethwaite1 import cube_g1_index
import rubik.cost.thistlethwaite.thistlethwaite2 as t2
from rubik.cube import SOLVED


class TestThistlethwaite2(unittest.TestCase):
    """Unit tests for Phase 2 (G2 -> G3) Thistlethwaite calculations."""

    def test_previous_index(self) -> None:
        """Taking any allowed moves in current phase preserves prior index."""
        solved = replace(SOLVED)
        for move in t2.G2_MOVES:
            cube_0 = replace(solved)
            cube_0.turn(move)
            self.assertEqual(cube_g1_index(solved), cube_g1_index(cube_0))
            for move in t2.G2_MOVES:
                cube_1 = replace(cube_0)
                cube_1.turn(move)
                self.assertEqual(cube_g1_index(solved), cube_g1_index(cube_1))

    def test_solved_cube_tetrad_indices(self) -> None:
        """A solved cube must have Tetrad 0 pieces at slots [0, 1, 2, 3]."""
        solved_cube = replace(SOLVED)
        t_indices = tetrad_0_indices(solved_cube)

        self.assertEqual(t_indices, [0, 1, 2, 3])

    def test_solved_cube_e_slice_indices(self) -> None:
        """Solved cube E-slice pieces must reside at non-M slots [1, 3, 5, 7]."""
        solved_cube = replace(SOLVED)
        e_indices = cube_e_indices(solved_cube)

        self.assertEqual(e_indices, [4, 5, 6, 7])

    def test_rank_combination_bounds(self) -> None:
        """Combinadic rank must accurately bound combinations."""
        self.assertEqual(rank_combination([0, 1, 2, 3]), 0)
        self.assertEqual(rank_combination([4, 5, 6, 7]), 69)
        self.assertEqual(rank_combination([1, 3, 5, 7]), 49)

    def test_solved_cube_index(self) -> None:
        """The solved cube index should equal 414."""
        solved_cube = replace(SOLVED)
        self.assertEqual(cube_g2_index(solved_cube), 414)

    def test_g2_moves_preserve_valid_range(self) -> None:
        """Applying valid G2 moves must produce indices within [0, G2_MAX_STATE - 1]."""
        cube = replace(SOLVED)
        for move in t2.G2_MOVES:
            test_cube = replace(cube)
            test_cube.turn(move)
            idx = cube_g2_index(test_cube)
            self.assertTrue(0 <= idx < G2_MAX_STATE)

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
        dummy_dist = [0] * G2_MAX_STATE
        save_database(dummy_dist)

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file.assert_called_once_with(t2.G2_FILE, "wb")
        mock_dump.assert_called_once_with(dummy_dist, mock_file())
