"""Represent the state of a Rubik's Cube."""
from dataclasses import dataclass, field, replace
from enum import Enum

class Colour(Enum):
    """Represent the colours of the faces of a Rubik's Cube"""
    B = 0   # Right
    G = 1   # Left
    W = 2   # Up
    Y = 3   # Down
    R = 4   # Front
    O = 5   # Back


# the allowable transitions between faces when turning a face of the cube
TRANSITION_TABLE = {
    None: ("R", "L", "U", "D", "F", "B"),
    "R": ("L", "U", "D", "F", "B"),
    "L": ("U", "D", "F", "B"),
    "U": ("D", "R", "L", "F", "B"),
    "D": ("R", "L", "F", "B"),
    "F": ("B", "R", "L", "U", "D"),
    "B": ("R", "L", "U", "D")
}


def pack_8_colours(colours: list[Colour]) -> int:
    """Pack 8 colours into a 64-bit integer."""
    packed = 0
    for i, colour in enumerate(colours):
        # Shift each number by 8 bits times its index
        packed |= (colour.value & 0xFF) << (i * 8)
    return packed

def unpack_8_colours(packed: int) -> list[Colour]:
    """Unpack a 64-bit integer into a list of 8 Colours."""
    colours = []
    for _ in range(8):
        colours.append(packed & 0xFF)
        packed >>= 8
    return colours

def rotate_left(value: int, shift: int, max_bits: int = 64) -> int:
    """Rotate a value to the left by a given number of bits."""
    value &= (1 << max_bits) - 1    # only consider the max_bits
    shift %= max_bits
    return ((value << shift) | (value >> (max_bits - shift))) \
            & ((1 << max_bits) - 1)     # fit within max_bits

def rotate_right(value: int, shift: int, max_bits: int = 64) -> int:
    """Rotate a value to the right by a given number of bits."""
    value &= (1 << max_bits) - 1    # only consider the max_bits
    shift %= max_bits
    return ((value >> shift) | (value << (max_bits - shift))) \
            & ((1 << max_bits) - 1)     # fit within max_bits


@dataclass(slots=True)
class Cube:
    """Represent the state of a Rubik's cube."""
    R: int
    L: int
    U: int
    D: int
    F: int
    B: int
    _last_move: str | None = field(default=None, init=False)

    def __str__(self) -> str:
        c = {}
        for face in ["R", "L", "U", "D", "F", "B"]:
            tiles = getattr(self, face)
            c[face] = [Colour(tile).name for tile in unpack_8_colours(tiles)]

        return \
            "{}         {}         {} \n".format(c["D"][0], c["D"][7], c["D"][6]) + \
            "    {}     {}     {}     \n".format(c["B"][2], c["B"][3], c["B"][4]) + \
            "  {}   {}   O   {}   {}   \n".format(c["L"][6], c["B"][1], c["B"][5], c["R"][2]) + \
            "    {}   {} {} {}   {}     \n".format(c["L"][7], c["B"][0], c["B"][7], c["B"][6], c["R"][1]) + \
            "      {} {} {} {} {}       \n".format(c["L"][0], c["U"][0], c["U"][1], c["U"][2], c["R"][0]) + \
            "{} {} G {} {} W {} {} B {} {} \n".format(c["D"][1], c["L"][5], c["L"][1], c["U"][7], c["U"][3], c["R"][7], c["R"][3], c["D"][5]) + \
            "      {} {} {} {} {}       \n".format(c["L"][2], c["U"][6], c["U"][5], c["U"][4], c["R"][6]) + \
            "    {}   {} {} {}   {}     \n".format(c["L"][3], c["F"][0], c["F"][1], c["F"][2], c["R"][5]) + \
            "  {}   {}   R   {}   {}   \n".format(c["L"][4], c["F"][7], c["F"][3], c["R"][4]) + \
            "    {}     {}     {}     \n".format(c["F"][6], c["F"][5], c["F"][4]) + \
            "{}         {}         {} \n".format(c["D"][2], c["D"][3], c["D"][4])

    def __hash__(self) -> int:
        """Return the hash of the cube."""
        faces = ["R", "L", "U", "D", "F", "B"]
        return hash(tuple(getattr(self, face) for face in faces))

    def __eq__(self, other: object) -> bool:
        """Check if two cubes are equal."""
        if self is other:
            return True
        if not isinstance(other, Cube):
            return NotImplemented
        return (self.R, self.L, self.U, self.D, self.F, self.B) == \
                (other.R, other.L, other.U, other.D, other.F, other.B)

    def _turn_clockwise(self, face: str) -> None:
        """Turn a face of the cube clockwise."""
        # Rotate the face itself
        try:
            tiles: int = getattr(self, face)
        except AttributeError:
            raise ValueError(f"Invalid face: {face}")
        tiles = rotate_left(tiles, 16, 64)
        setattr(self, face, tiles)

        # rotate the adjacent faces
        match face:
            case "R":
                self._turn_adj(["U", "F", "D", "B"], [2, 2, 4, 4])
            case "U":
                self._turn_adj(["R", "B", "L", "F"], [6, 6, 0, 0])
            case "F":
                self._turn_adj(["L", "D", "R", "U"], [2, 2, 4, 4])
            case "L":
                self._turn_adj(["F", "U", "B", "D"], [6, 6, 0, 0])
            case "D":
                self._turn_adj(["B", "R", "F", "L"], [2, 2, 4, 4])
            case "B":
                self._turn_adj(["D", "L", "U", "R"], [6, 6, 0, 0])
            case _:
                raise ValueError(f"Invalid face: {face}")

    def _turn_counterclockwise(self, face: str) -> None:
        """Turn a face of the cube counterclockwise."""
        # Rotate the face itself
        try:
            tiles: int = getattr(self, face)
        except AttributeError:
            raise ValueError(f"Invalid face: {face}")
        tiles = rotate_right(tiles, 16, 64)
        setattr(self, face, tiles)

        # rotate the adjacent faces
        match face:
            case "R":
                self._turn_adj(["B", "D", "F", "U"], [4, 4, 2, 2])
            case "U":
                self._turn_adj(["F", "L", "B", "R"], [0, 0, 6, 6])
            case "F":
                self._turn_adj(["U", "R", "D", "L"], [4, 4, 2, 2])
            case "L":
                self._turn_adj(["D", "B", "U", "F"], [0, 0, 6, 6])
            case "D":
                self._turn_adj(["L", "F", "R", "B"], [4, 4, 2, 2])
            case "B":
                self._turn_adj(["R", "U", "L", "D"], [0, 0, 6, 6])
            case _:
                raise ValueError(f"Invalid face: {face}")

    def _turn_double(self, face: str) -> None:
        """Turn a face of the cube twice."""
        # Rotate the face itself
        try:
            tiles: int = getattr(self, face)
        except AttributeError:
            raise ValueError(f"Invalid face: {face}")
        tiles = rotate_left(tiles, 32, 64)
        setattr(self, face, tiles)

        # rotate the adjacent faces
        match face:
            case "R":
                self._turn_adj(["U", "D"], [2, 4])
                self._turn_adj(["F", "B"], [2, 4])
            case "U":
                self._turn_adj(["R", "L"], [6, 0])
                self._turn_adj(["B", "F"], [6, 0])
            case "F":
                self._turn_adj(["L", "R"], [2, 4])
                self._turn_adj(["D", "U"], [2, 4])
            case "L":
                self._turn_adj(["F", "B"], [6, 0])
                self._turn_adj(["U", "D"], [6, 0])
            case "D":
                self._turn_adj(["B", "F"], [2, 4])
                self._turn_adj(["R", "L"], [2, 4])
            case "B":
                self._turn_adj(["D", "U"], [6, 0])
                self._turn_adj(["L", "R"], [6, 0])
            case _:
                raise ValueError(f"Invalid face: {face}")

    def _turn_adj(self, faces: list[str], indices: list[int]) -> None:
        """Rotate the adjacent edges of a cube when turning a face."""
        # get all the tiles as local variables
        tiles: list[int] = [getattr(self, face) for face in faces]

        # align all relevant tiles to the rightmost position
        for i, tile in enumerate(tiles):
            tiles[i] = rotate_right(tile, indices[i] * 8)

        # get the first edge
        temp_edge = tiles[0] & 0xFFFFFF

        for i in range(len(faces) - 1):
            next_edge = tiles[i + 1] & 0xFFFFFF
            tiles[i] &= ~(0xFFFFFF)     # clear the edge
            tiles[i] |= next_edge       # update the edge

        tiles[-1] &= ~(0xFFFFFF)    # clear the last edge
        tiles[-1] |= temp_edge      # update the last edge

        # align all relevant tiles back to their original position
        for i, tile in enumerate(tiles):
            tiles[i] = rotate_left(tile, indices[i] * 8)
            setattr(self, faces[i], tiles[i])

    def turn(self, command: str) -> None:
        """Turn a face of the cube based on a command string."""
        face, modifier = command[0], command[1:]
        match (face, modifier):
            case (_, ""):
                self._turn_clockwise(face)
            case (_, "'"):
                self._turn_counterclockwise(face)
            case (_, "2"):
                self._turn_double(face)
            case _:
                raise ValueError(f"Invalid command: {command}")

        self._last_move = command

    def successors(self) -> list["Cube"]:
        """Return a list of all neighbouring cubes."""
        successors = []
        last_face = self._last_move[0] if self._last_move else None
        for face in TRANSITION_TABLE[last_face]:
            for modifier in ["", "'", "2"]:
                new_cube = replace(self)
                new_cube.turn(face + modifier)
                successors.append(new_cube)
        return successors
