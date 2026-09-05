from dataclasses import replace
import unittest


from rubik.cost.hamming import (
    _different_bytes,
    hamming_tile_distance,
    hamming_piece_distance,
)
from rubik.cost.common import get_colour
from rubik.cube import SOLVED


class TestDifferentBytes(unittest.TestCase):
    """Test suite for _different_bytes helper function."""

    def test_identical_values(self):
        """Test that identical integers return 0 differences."""
        self.assertEqual(_different_bytes(0x12345678, 0x12345678), 0)
        self.assertEqual(_different_bytes(0, 0), 0)

    def test_single_byte_difference(self):
        """Test when exactly one byte position differs."""
        # Differ in least significant byte
        self.assertEqual(_different_bytes(0x00, 0xFF), 1)
        # Differ in higher byte slot (byte index 2)
        self.assertEqual(_different_bytes(0x00110000, 0x00220000), 1)

    def test_all_bytes_different(self):
        """Test when every byte position differs across a 64-bit integer."""
        a = 0x0000000000000000
        b = 0x0101010101010101
        self.assertEqual(_different_bytes(a, b), 8)

    def test_partial_vs_full_bit_flips(self):
        """Test that any bit flip within a byte counts as 1 byte difference."""
        # Single bit set vs all bits set in the same byte slot
        a = 0x00000001
        b = 0x0000FF
        self.assertEqual(_different_bytes(a, b), 1)

    def test_scattered_byte_differences(self):
        """Test alternating or non-contiguous byte differences."""
        a = 0xAA00BB00CC00DD00
        b = 0x0000000000000000
        self.assertEqual(_different_bytes(a, b), 4)


class TestHammingTileDistance(unittest.TestCase):
    """Test suite for hamming_tile_distance heuristic function."""

    def test_identical_cubes(self):
        """Test that identical cubes return a distance of 0.0."""
        self.assertEqual(hamming_tile_distance(SOLVED, SOLVED), 0.0)

    def test_single_turn_distance(self):
        """Test that a single quarter turn yields a distance of 1.0"""
        scrambled = replace(SOLVED)
        scrambled.turn("R")
        self.assertEqual(hamming_tile_distance(scrambled, SOLVED), 1.0)

    def test_two_independent_turns(self):
        """Test distance for two non-overlapping face turns (R and L)."""
        scrambled = replace(SOLVED)
        scrambled.turn("R")     # R moves 12 tiles
        scrambled.turn("L")     # L moves 12 non-overlapping tiles

        # 24 misplaced tiles, so total = 24 / 20.0 = 1.2, round to 2.0
        self.assertEqual(hamming_tile_distance(scrambled, SOLVED), 2.0)

    def test_symmetry(self):
        """Test that hamming_tile_distance is symmetric."""
        scrambled = replace(SOLVED)
        scrambled.turn("U'")
        self.assertEqual(
            hamming_tile_distance(scrambled, SOLVED),
            hamming_tile_distance(SOLVED, scrambled),
        )

    def test_admissibility(self):
        """Test heuristic cost never exceeds the actual number of moves."""
        scrambled = replace(SOLVED)
        moves = ["F", "U", "R", "D'"]

        for depth, move in enumerate(moves, start=1):
            scrambled.turn(move)
            h = hamming_tile_distance(scrambled, SOLVED)
            self.assertLessEqual(h, depth)


class TestHammingPieceDistance(unittest.TestCase):
    """Test suite for hamming_piece_distance heuristic function."""

    def test_identical_cubes(self):
        """Test that identical cubes return a distance of 0.0."""
        self.assertEqual(hamming_piece_distance(SOLVED, SOLVED), 0.0)

    def test_single_turn_distance(self):
        """Test a single turn alters 4 corners and 4 edges, yielding 1.0."""
        scrambled = replace(SOLVED)
        scrambled.turn("R")
        self.assertEqual(hamming_piece_distance(scrambled, SOLVED), 1.0)

    def test_two_independent_turns(self):
        """Test non-overlapping turns (R and L) alter 8 corners and 8 edges."""
        scrambled = replace(SOLVED)
        scrambled.turn("R")
        scrambled.turn("L")
        self.assertEqual(hamming_piece_distance(scrambled, SOLVED), 2.0)

    def test_symmetry(self):
        """Test that hamming_piece_distance is symmetric."""
        scrambled = replace(SOLVED)
        scrambled.turn("F'")
        self.assertEqual(
            hamming_piece_distance(scrambled, SOLVED),
            hamming_piece_distance(SOLVED, scrambled),
        )

    def test_admissibility(self):
        """Test heuristic cost never exceeds the actual number of moves."""
        scrambled = replace(SOLVED)
        moves = ["R", "U", "F", "D'", "L2"]

        for depth, move in enumerate(moves, start=1):
            scrambled.turn(move)
            h = hamming_piece_distance(scrambled, SOLVED)
            self.assertLessEqual(h, depth)
