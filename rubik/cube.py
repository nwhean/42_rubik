"""Represent the state of a Rubik's Cube."""
from dataclasses import dataclass
from enum import Enum

class Colour(Enum):
    """Represent the colours of the faces of a Rubik's Cube"""
    B = 0   # Right
    G = 1   # Left
    W = 2   # Up
    Y = 3   # Down
    R = 4   # Front
    O = 5   # Back


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


@dataclass(slots=True)
class Cube:
    """Represent the state of a Rubik's cube."""
    R: int
    L: int
    U: int
    D: int
    F: int
    B: int

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
