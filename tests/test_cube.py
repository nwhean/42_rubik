"""Unittest for Node class."""
from dataclasses import replace
import unittest

from rubik.cube import (
    pack_8_colours,
    unpack_8_colours,
    rotate_left,
    rotate_right,
    Colour,
    TRANSITION_TABLE,
    Cube,
    SOLVED,
)


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


class TestRotate(unittest.TestCase):
    """Test rotate functions."""
    def test_rotate_left(self):
        """Test rotating left."""
        value = 0x123456789ABCDEF0
        self.assertEqual(rotate_left(value, 4), 0x23456789ABCDEF01)
        self.assertEqual(rotate_left(value, 8), 0x3456789ABCDEF012)
        self.assertEqual(rotate_left(value, 4, 16), 0xEF0D)

    def test_rotate_right(self):
        """Test rotating right."""
        value = 0x123456789ABCDEF0
        self.assertEqual(rotate_right(value, 4), 0x0123456789ABCDEF)
        self.assertEqual(rotate_right(value, 8), 0xF0123456789ABCDE)
        self.assertEqual(rotate_right(value, 4, 16), 0X0DEF)


class TestCube(unittest.TestCase):
    """Test Cube class."""

    def test_cube_str(self):
        """Test string representation of Cube."""
        solved = replace(SOLVED)
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

    def test_cube_hash(self):
        """Test that the hash of the cube is consistent."""
        cube_0 = replace(SOLVED)
        cube_1 = replace(SOLVED)
        self.assertEqual(hash(cube_0), hash(cube_1))

        # Turn a face of the cube and check that the hash changes
        cube_1._turn_clockwise('R')
        self.assertNotEqual(hash(cube_0), hash(cube_1))

    def test_turn_clockwise_R(self):
        """Test turning a face of the cube clockwise."""
        cube = replace(SOLVED)
        cube._turn_clockwise('R')
        expected_str = (
            "Y         Y         O \n"
            "    O     O     W     \n"
            "  G   O   O   W   B   \n"
            "    G   O O W   B     \n"
            "      G W W R B       \n"
            "Y G G G W W R B B B O \n"
            "      G W W R B       \n"
            "    G   R R Y   B     \n"
            "  G   R   R   Y   B   \n"
            "    R     R     Y     \n"
            "Y         Y         O \n"
        )
        self.assertEqual(str(cube), expected_str)

    def test_turn_clockwise_U(self):
        """Test turning a face of the cube clockwise."""
        cube = replace(SOLVED)
        cube._turn_clockwise('U')
        expected_str = (
            "Y         Y         Y \n"
            "    O     O     O     \n"
            "  G   O   O   O   B   \n"
            "    G   G G G   B     \n"
            "      R W W W O       \n"
            "Y G G R W W W O B B Y \n"
            "      R W W W O       \n"
            "    G   B B B   B     \n"
            "  G   R   R   R   B   \n"
            "    R     R     R     \n"
            "Y         Y         Y \n"
        )
        self.assertEqual(expected_str, str(cube))

    def test_turn_clockwise_F(self):
        """Test turning a face of the cube clockwise."""
        cube = replace(SOLVED)
        cube._turn_clockwise('F')
        expected_str = (
            "Y         Y         Y \n"
            "    O     O     O     \n"
            "  G   O   O   O   B   \n"
            "    G   O O O   B     \n"
            "      G W W W B       \n"
            "Y G G G W W W B B B Y \n"
            "      Y G G G W       \n"
            "    Y   R R R   W     \n"
            "  Y   R   R   R   W   \n"
            "    R     R     R     \n"
            "B         B         B \n"
        )
        self.assertEqual(expected_str, str(cube))

    def test_turn_clockwise_L(self):
        """Test turning a face of the cube clockwise."""
        cube = replace(SOLVED)
        cube._turn_clockwise('L')
        expected_str = (
            "R         Y         Y \n"
            "    Y     O     O     \n"
            "  G   Y   O   O   B   \n"
            "    G   Y O O   B     \n"
            "      G O W W B       \n"
            "R G G G O W W B B B Y \n"
            "      G O W W B       \n"
            "    G   W R R   B     \n"
            "  G   W   R   R   B   \n"
            "    W     R     R     \n"
            "R         Y         Y \n"
        )
        self.assertEqual(expected_str, str(cube))

    def test_turn_clockwise_D(self):
        """Test turning a face of the cube clockwise."""
        cube = replace(SOLVED)
        cube._turn_clockwise('D')
        expected_str = (
            "Y         Y         Y \n"
            "    B     B     B     \n"
            "  O   O   O   O   R   \n"
            "    G   O O O   B     \n"
            "      G W W W B       \n"
            "Y O G G W W W B B R Y \n"
            "      G W W W B       \n"
            "    G   R R R   B     \n"
            "  O   R   R   R   R   \n"
            "    G     G     G     \n"
            "Y         Y         Y \n"
        )
        self.assertEqual(expected_str, str(cube))

    def test_turn_clockwise_B(self):
        """Test turning a face of the cube clockwise."""
        cube = replace(SOLVED)
        cube._turn_clockwise('B')
        expected_str = (
            "G         G         G \n"
            "    O     O     O     \n"
            "  W   O   O   O   Y   \n"
            "    W   O O O   Y     \n"
            "      W B B B Y       \n"
            "Y G G G W W W B B B Y \n"
            "      G W W W B       \n"
            "    G   R R R   B     \n"
            "  G   R   R   R   B   \n"
            "    R     R     R     \n"
            "Y         Y         Y \n"
        )
        self.assertEqual(expected_str, str(cube))

    def test_turn_invalid_face(self):
        """Test turning a face of the cube with an invalid face."""
        cube = replace(SOLVED)
        with self.assertRaises(ValueError):
            cube._turn_clockwise('X')

    def test_turn_clockwise_RU(self):
        """Test turning a face of the cube clockwise."""
        cube = replace(SOLVED)
        cube._turn_clockwise('R')
        cube._turn_clockwise('U')
        expected_str = (
            "Y         Y         O \n"
            "    O     O     W     \n"
            "  G   O   O   W   B   \n"
            "    G   G G G   B     \n"
            "      R W W W O       \n"
            "Y G G R W W W O B B O \n"
            "      Y R R R W       \n"
            "    G   B B B   B     \n"
            "  G   R   R   Y   B   \n"
            "    R     R     Y     \n"
            "Y         Y         O \n"
        )
        self.assertEqual(str(cube), expected_str)

    def test_turn_clockwise_UF(self):
        """Test turning a face of the cube clockwise."""
        cube = replace(SOLVED)
        cube._turn_clockwise('U')
        cube._turn_clockwise('F')
        expected_str = (
            "Y         Y         Y \n"
            "    O     O     O     \n"
            "  G   O   O   O   B   \n"
            "    G   G G G   B     \n"
            "      R W W W O       \n"
            "Y G G R W W W O B B Y \n"
            "      Y G G R W       \n"
            "    Y   R R B   W     \n"
            "  Y   R   R   B   W   \n"
            "    R     R     B     \n"
            "B         B         O \n"
        )
        self.assertEqual(expected_str, str(cube))

    def test_turn_clockwise_FL(self):
        """Test turning a face of the cube clockwise."""
        cube = replace(SOLVED)
        cube._turn_clockwise('F')
        cube._turn_clockwise('L')
        expected_str = (
            "R         Y         Y \n"
            "    B     O     O     \n"
            "  Y   Y   O   O   B   \n"
            "    G   Y O O   B     \n"
            "      G O W W B       \n"
            "R Y G G O W W B B B Y \n"
            "      G O G G W       \n"
            "    G   W R R   W     \n"
            "  Y   W   R   R   W   \n"
            "    G     R     R     \n"
            "R         B         B \n"
        )
        self.assertEqual(expected_str, str(cube))

    def test_turn_clockwise_LD(self):
        """Test turning a face of the cube clockwise."""
        cube = replace(SOLVED)
        cube._turn_clockwise('L')
        cube._turn_clockwise('D')
        expected_str = (
            "Y         Y         Y \n"
            "    B     B     B     \n"
            "  O   Y   O   O   R   \n"
            "    G   Y O O   B     \n"
            "      G O W W B       \n"
            "Y O G G O W W B B R Y \n"
            "      G O W W B       \n"
            "    G   W R R   B     \n"
            "  Y   W   R   R   W   \n"
            "    G     G     G     \n"
            "R         R         R \n"
        )
        self.assertEqual(expected_str, str(cube))

    def test_turn_clockwise_DB(self):
        """Test turning a face of the cube clockwise."""
        cube = replace(SOLVED)
        cube._turn_clockwise('D')
        cube._turn_clockwise('B')
        expected_str = (
            "G         G         O \n"
            "    O     O     B     \n"
            "  W   O   O   B   Y   \n"
            "    W   O O B   Y     \n"
            "      W B B R Y       \n"
            "Y O G G W W W B B R Y \n"
            "      G W W W B       \n"
            "    G   R R R   B     \n"
            "  O   R   R   R   R   \n"
            "    G     G     G     \n"
            "Y         Y         Y \n"
        )
        self.assertEqual(expected_str, str(cube))

    def test_turn_clockwise_BR(self):
        """Test turning a face of the cube clockwise."""
        cube = replace(SOLVED)
        cube._turn_clockwise('B')
        cube._turn_clockwise('R')
        expected_str = (
            "G         G         O \n"
            "    O     O     B     \n"
            "  W   O   O   W   Y   \n"
            "    W   O O W   B     \n"
            "      W B B R B       \n"
            "Y G G G W W R B B Y O \n"
            "      G W W R B       \n"
            "    G   R R Y   B     \n"
            "  G   R   R   Y   Y   \n"
            "    R     R     G     \n"
            "Y         Y         O \n"
        )
        self.assertEqual(expected_str, str(cube))

    def test_turn_counterclockwise(self):
        """Test turning a face of the cube counterclockwise."""
        faces = ["R", "L", "U", "D", "F", "B"]
        for face in faces:
            cube_0 = replace(SOLVED)
            cube_1 = replace(SOLVED)
            cube_0._turn_clockwise(face)
            cube_0._turn_clockwise(face)
            cube_0._turn_clockwise(face)
            cube_1._turn_counterclockwise(face)
            self.assertEqual(str(cube_0), str(cube_1))

    def test_turn_counterclockwise_two_faces(self):
        """Test turning a face of the cube counterclockwise."""
        faces = ["R", "L", "U", "D", "F", "B"]
        for face_0 in faces:
            for face_1 in faces:
                cube_0 = replace(SOLVED)
                cube_1 = replace(SOLVED)
                # turn one face first
                cube_0._turn_clockwise(face_0)
                cube_1._turn_clockwise(face_0)

                # test counterclockwise turn == 3 x clockwise turns
                cube_0._turn_clockwise(face_1)
                cube_0._turn_clockwise(face_1)
                cube_0._turn_clockwise(face_1)
                cube_1._turn_counterclockwise(face_1)
                self.assertEqual(str(cube_0), str(cube_1))

    def test_turn_double(self):
        """Test turning a face of the cube twice."""
        faces = ["R", "L", "U", "D", "F", "B"]
        for face in faces:
            cube_0 = replace(SOLVED)
            cube_1 = replace(SOLVED)
            cube_0._turn_clockwise(face)
            cube_0._turn_clockwise(face)
            cube_1._turn_double(face)
            self.assertEqual(str(cube_0), str(cube_1))

    def test_turn_double_two_faces(self):
        """Test turning a face of the cube twice."""
        faces = ["R", "L", "U", "D", "F", "B"]
        for face_0 in faces:
            for face_1 in faces:
                cube_0 = replace(SOLVED)
                cube_1 = replace(SOLVED)
                # turn one face first
                cube_0._turn_clockwise(face_0)
                cube_1._turn_clockwise(face_0)

                # test double turn == 2 x clockwise turns
                cube_0._turn_clockwise(face_1)
                cube_0._turn_clockwise(face_1)
                cube_1._turn_double(face_1)
                self.assertEqual(str(cube_0), str(cube_1))

    def test_turn(self):
        """Test public method of turning a face of the cube."""
        faces = ["R", "L", "U", "D", "F", "B"]
        modifiers = ["", "'", "2"]
        for face in faces:
            for modifier in modifiers:
                cube_0 = replace(SOLVED)
                cube_1 = replace(SOLVED)
                cube_0.turn(face + modifier)
                match modifier:
                    case "":
                        cube_1._turn_clockwise(face)
                    case "'":
                        cube_1._turn_counterclockwise(face)
                    case "2":
                        cube_1._turn_double(face)
                self.assertEqual(str(cube_0), str(cube_1))

    def test_turn_invalid(self):
        """Test turning a face of the cube with invalid command."""
        faces = ["R", "L", "U", "D", "F", "B", "X"]
        modifiers = ['"', "3"]
        for face in faces:
            for modifier in modifiers:
                cube = replace(SOLVED)
                with self.assertRaises(ValueError):
                    cube.turn(face + modifier)

    def test_transition_table(self):
        """Test that the transition table is correct."""
        exclude = {
            "L": "R",   # R cannot succeed L
            "D": "U",   # U cannot succeed D
            "B": "F",   # F cannot succeed B
        }
        for face, successors in TRANSITION_TABLE.items():
            self.assertEqual(
                set(successors),
                set(["R", "L", "U", "D", "F", "B"])
                - {face}    # a face cannot succeed by the same face
                - {exclude.get(face, None)}
            )

    def test_successors(self):
        """Test that successors are generated according to transition table."""
        faces = [None, "R", "L", "U", "D", "F", "B"]
        for face in faces:
            cube = replace(SOLVED)
            if face:
                cube.turn(face)

            successors = cube.successors()
            self.assertEqual(len(successors), len(TRANSITION_TABLE[face]) * 3)

            # ensure that the successors' last move are allowed
            allowed_faces = set(TRANSITION_TABLE[face])
            for succ in successors:
                self.assertIn(succ._last_move[0], allowed_faces)
