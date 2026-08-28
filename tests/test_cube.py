"""Unittest for Node class."""
import unittest

from rubik.cube import pack_8_colours, unpack_8_colours, Colour, Cube

class TestPackUnpackColours(unittest.TestCase):
    """Test packing and unpacking of colours."""

    def test_pack(self):
        """Test packing of colours."""
        colours = [Colour.R, Colour.G, Colour.B, Colour.Y, Colour.O, Colour.W, Colour.R, Colour.G]
        packed = pack_8_colours(colours)
        expected_packed = (
            (Colour.R.value & 0xFF) |
            ((Colour.G.value & 0xFF) << 8) |
            ((Colour.B.value & 0xFF) << 16) |
            ((Colour.Y.value & 0xFF) << 24) |
            ((Colour.O.value & 0xFF) << 32) |
            ((Colour.W.value & 0xFF) << 40) |
            ((Colour.R.value & 0xFF) << 48) |
            ((Colour.G.value & 0xFF) << 56)
        )
        self.assertEqual(packed, expected_packed)

    def test_unpack(self):
        """Test unpacking of colours."""
        packed = (
            (Colour.R.value & 0xFF) |
            ((Colour.G.value & 0xFF) << 8) |
            ((Colour.B.value & 0xFF) << 16) |
            ((Colour.Y.value & 0xFF) << 24) |
            ((Colour.O.value & 0xFF) << 32) |
            ((Colour.W.value & 0xFF) << 40) |
            ((Colour.R.value & 0xFF) << 48) |
            ((Colour.G.value & 0xFF) << 56)
        )
        unpacked = unpack_8_colours(packed)
        expected_colours = [Colour.R, Colour.G, Colour.B, Colour.Y, Colour.O, Colour.W, Colour.R, Colour.G]
        for i, j in zip(expected_colours, unpacked):
            self.assertEqual(i.value, j)

    def test_pack_unpack(self):
        """Test packing and unpacking of colours."""
        colours = [Colour.R, Colour.G, Colour.B, Colour.Y, Colour.O, Colour.W, Colour.R, Colour.G]
        packed = pack_8_colours(colours)
        unpacked = unpack_8_colours(packed)
        for i, j in zip(colours, unpacked):
            self.assertEqual(i.value, j)


class TestCube(unittest.TestCase):
    """Test Cube class."""

    def test_cube_str(self):
        """Test string representation of Cube."""
        solved = Cube(
            pack_8_colours([Colour.B] * 8),
            pack_8_colours([Colour.G] * 8),
            pack_8_colours([Colour.W] * 8),
            pack_8_colours([Colour.Y] * 8),
            pack_8_colours([Colour.R] * 8),
            pack_8_colours([Colour.O] * 8),
        )
        expected_str = (
            "Y         Y         Y \n"
            "    O     O     O     \n"
            "  G   O   O   O   B   \n"
            "    G   O O O   B     \n"
            "      G W W W B       \n"
            "Y G G G W W W B B B Y \n"
            "      G W W W B       \n"
            "    G   R R R   B     \n"
            "  G   R   R   R   B   \n"
            "    R     R     R     \n"
            "Y         Y         Y \n"
        )
        self.assertEqual(str(solved), expected_str)
