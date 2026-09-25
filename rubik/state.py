"""Define standard protocol that search algorithms can rely on."""

from typing import Protocol


class State(Protocol):
    """Simple protocol for search space state."""

    def successors(self) -> list["State"]:
        """Return a list of successors from the current state.

        The list should exclude the predecessor of the current state.
        """
