from dataclasses import replace
import unittest
from unittest.mock import MagicMock, mock_open, patch

from rubik.cost.thistlethwaite.common import EDGES
from rubik.cost.thistlethwaite.thistlethwaite0 import (
    cube_edge_orientation,
    cube_g0_index,
    edge_orientation,
    generate_g0_database,
    read_database_0,
    save_database,
    G0_MAX_STATE,
)
import rubik.cost.thistlethwaite.thistlethwaite0 as t0
from rubik.cube import SOLVED


class TestThistlethwaite0(unittest.TestCase):
    """Unit tests for Phase 0 (G0 -> G1) Thistlethwaite calculations."""

    def test_solved_cube_orientation(self) -> None:
        """A solved cube must have all edge orientations as 0 and index as 0."""
        solved_cube = replace(SOLVED)
        orientations = cube_edge_orientation(solved_cube)

        self.assertEqual(len(orientations), 12)
        self.assertEqual(orientations, [0] * 12)
        self.assertEqual(cube_g0_index(solved_cube), 0)

    def test_edge_orientation_single_edge(self) -> None:
        """Verify edge_orientation returns 0 for solved edge pieces."""
        solved_cube = replace(SOLVED)
        for edge in EDGES:
            self.assertEqual(edge_orientation(solved_cube, edge), 0)

    def test_orientation_changes_on_moves(self) -> None:
        """
        Applying quarter turns and inverse move should preserve orientations."""
        cube = replace(SOLVED)
        f_index = cube_g0_index(cube)

        # Quarter-turn modifies orientation index
        moves = ['R', 'L', 'U', 'D', 'F', 'B']
        for move in moves:
            cube.turn(move)
            if move in ['U', 'D']:
                self.assertNotEqual(cube_g0_index(cube), f_index)
            else:
                self.assertEqual(cube_g0_index(cube), f_index)
            cube.turn(move + "'")
            # Applying inverse move restores solved orientation index
            self.assertEqual(cube_g0_index(cube), f_index)

    def test_half_turns_preserve_parity(self) -> None:
        """2 quarter turns return index to solved state."""
        cube = replace(SOLVED)
        moves = ['U', 'D']
        for move in moves:
            for _ in range(2):
                cube.turn(move)
        self.assertEqual(cube_g0_index(cube), 0)

    @patch("pathlib.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.dump")
    def test_save_database(
            self,
            mock_dump: MagicMock,
            mock_file: MagicMock,
            mock_mkdir: MagicMock
        ) -> None:
        """save_database should create directories and pickle data."""
        dummy_dist = [0] * G0_MAX_STATE
        save_database(dummy_dist)

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file.assert_called_once_with(t0.G0_FILE, "wb")
        mock_dump.assert_called_once_with(dummy_dist, mock_file())

    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.load")
    def test_read_database_file_exists(
            self,
            mock_load: MagicMock,
            mock_file: MagicMock
        ) -> None:
        """read_database should load data when file exists."""
        fake_db = [0, 1, 2]
        mock_load.return_value = fake_db

        read_database_0()

        mock_file.assert_called_once_with(t0.G0_FILE, "rb")
        self.assertEqual(t0.G0_DIST, fake_db)

    @patch("builtins.open", side_effect=FileNotFoundError)
    @patch("rubik.cost.thistlethwaite.thistlethwaite0.generate_g0_database")
    @patch("rubik.cost.thistlethwaite.common.save_database")
    def test_read_database_file_not_found(
        self,
        mock_save: MagicMock,
        mock_generate: MagicMock,
        mock_open_fn: MagicMock,
    ) -> None:
        """read_database should generate and save DB if file is missing."""
        dummy_generated = [-1] * G0_MAX_STATE
        mock_generate.return_value = dummy_generated

        t0.read_database_0()

        mock_generate.assert_called_once()
        mock_save.assert_called_once_with(t0.G0_FILE, dummy_generated)
        self.assertEqual(t0.G0_DIST, dummy_generated)

    @patch("rubik.cost.thistlethwaite.common.print_progress_bar")
    def test_generate_g0_database(self, mock_progress_bar) -> None:
        """
        Generate_g0_database must produce 2048 reachable states with
        correct distance for solved cube.
        """
        g0_dist = generate_g0_database()

        self.assertEqual(len(g0_dist), G0_MAX_STATE)
        self.assertEqual(g0_dist[0], 0)  # Solved state index distance is 0
        self.assertNotIn(-1, g0_dist)    # All 2048 states must be reachable
