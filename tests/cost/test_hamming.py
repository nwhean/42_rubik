from dataclasses import replace
import unittest


from rubik.cost.hamming import different_bytes, hamming_distance
from rubik.cube import Colour, Cube, pack_8_colours


class TestDifferentBytes(unittest.TestCase):
    """Test suite for different_bytes helper function."""

    def test_identical_values(self):
        """Test that identical integers return 0 differences."""
        self.assertEqual(different_bytes(0x12345678, 0x12345678), 0)
        self.assertEqual(different_bytes(0, 0), 0)

    def test_single_byte_difference(self):
        """Test when exactly one byte position differs."""
        # Differ in least significant byte
        self.assertEqual(different_bytes(0x00, 0xFF), 1)
        # Differ in higher byte slot (byte index 2)
        self.assertEqual(different_bytes(0x00110000, 0x00220000), 1)

    def test_all_bytes_different(self):
        """Test when every byte position differs across a 64-bit integer."""
        a = 0x0000000000000000
        b = 0x0101010101010101
        self.assertEqual(different_bytes(a, b), 8)

    def test_partial_vs_full_bit_flips(self):
        """Test that any bit flip within a byte counts as 1 byte difference."""
        # Single bit set vs all bits set in the same byte slot
        a = 0x00000001
        b = 0x0000FF
        self.assertEqual(different_bytes(a, b), 1)

    def test_scattered_byte_differences(self):
        """Test alternating or non-contiguous byte differences."""
        a = 0xAA00BB00CC00DD00
        b = 0x0000000000000000
        self.assertEqual(different_bytes(a, b), 4)


SOLVED = Cube(
    pack_8_colours([Colour.B] * 8),
    pack_8_colours([Colour.G] * 8),
    pack_8_colours([Colour.W] * 8),
    pack_8_colours([Colour.Y] * 8),
    pack_8_colours([Colour.R] * 8),
    pack_8_colours([Colour.O] * 8),
)


class TestHammingDistance(unittest.TestCase):
    """Test suite for hamming_distance heuristic function."""

    def test_identical_cubes(self):
        """Test that identical cubes return a distance of 0.0."""
        self.assertEqual(hamming_distance(SOLVED, SOLVED), 0.0)

    def test_single_turn_distance(self):
        """Test that a single quarter turn yields a distance of 0.6"""
        scrambled = replace(SOLVED)
        scrambled.turn("R")
        self.assertEqual(hamming_distance(scrambled, SOLVED), 0.6)

    def test_two_independent_turns(self):
        """Test distance for two non-overlapping face turns (R and L)."""
        scrambled = replace(SOLVED)
        scrambled.turn("R")     # R moves 12 tiles
        scrambled.turn("L")     # L moves 12 non-overlapping tiles

        # 24 misplaced tiles, so total = 24 / 20.0 = 1.2
        self.assertEqual(hamming_distance(scrambled, SOLVED), 1.2)

    def test_symmetry(self):
        """Test that hamming_distance(a, b) == hamming_distance(b, a)."""
        scrambled = replace(SOLVED)
        scrambled.turn("U'")
        self.assertEqual(
            hamming_distance(scrambled, SOLVED),
            hamming_distance(SOLVED, scrambled),
        )

    def test_admissibility(self):
        """Test heuristic cost never exceeds the actual number of moves."""
        scrambled = replace(SOLVED)
        moves = ["F", "U", "R", "D'"]

        for depth, move in enumerate(moves, start=1):
            scrambled.turn(move)
            h = hamming_distance(scrambled, SOLVED)
            self.assertLessEqual(h, depth)
