import unittest

from rubik.cost.common import get_colour
from rubik.cube import Colour, Cube, pack_8_colours, SOLVED


class TestGetColour(unittest.TestCase):
    """Test suite for get_colour helper function."""

    def test_solved_cube_colours(self):
        """
        Test that get_colour extracts expected values for every tile on
        a solved cube.
        """
        expected_faces = {
            "R": Colour.B.value,
            "L": Colour.G.value,
            "U": Colour.W.value,
            "D": Colour.Y.value,
            "F": Colour.R.value,
            "B": Colour.O.value,
        }
        for face, expected_val in expected_faces.items():
            for index in range(8):
                with self.subTest(face=face, index=index):
                    self.assertEqual(get_colour(SOLVED, face, index), expected_val)

    def test_mixed_face_tile_indices(self):
        """
        Test reading individual tile positions from a face containing
        multiple distinct colours.
        """
        mixed_colours = [
            Colour.B,
            Colour.G,
            Colour.W,
            Colour.Y,
            Colour.R,
            Colour.O,
            Colour.B,
            Colour.G,
        ]
        test_cube = Cube(
            R=pack_8_colours(mixed_colours),
            L=pack_8_colours([Colour.G] * 8),
            U=pack_8_colours([Colour.W] * 8),
            D=pack_8_colours([Colour.Y] * 8),
            F=pack_8_colours([Colour.R] * 8),
            B=pack_8_colours([Colour.O] * 8),
        )

        for index, colour_enum in enumerate(mixed_colours):
            with self.subTest(index=index):
                self.assertEqual(
                    get_colour(test_cube, "R", index),
                    colour_enum.value
                )
