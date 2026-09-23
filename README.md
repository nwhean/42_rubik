# 42_rubik

A Rubik's Cube Solver and Interactive Animator built in Python.

This project implements various search algorithms and heuristics to solve a Rubik's Cube and includes a Pygame-based interactive visualization tool that allows you to play with the cube or watch the solution unfold.

## Requirements

*   **Python >= 3.10**
*   `pygame` (for the interactive animator)

## Installation

1.  **Clone the repository** to your local machine:
    ```bash
    git clone https://github.com/nwhean/42_rubik.git
    cd 42_rubik
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies**:
    ```bash
    pip install pygame
    ```

## Usage

### The Solver (`__main__.py`)

The main entry point for solving the cube is `__main__.py` inside the `rubik` module. You can run it as a module using the `-m` flag.

**Basic Usage:**
You can provide a specific sequence of scramble moves, or let the program generate a random scramble.

```bash
# Provide a specific scramble sequence
python -m rubik "R U R' F2 L D"

# Generate a random scramble of 15 moves
python -m rubik -s 15
```

**Advanced Options:**
The solver supports several flags to change algorithms, heuristics, and output.

*   `-a`, `--algo`: Search algorithm to use (e.g., `thistlethwaite`, `ida`). Default is `thistlethwaite`.
*   `-c`, `--cost`: Heuristic cost function (e.g., `manhattan`, `hamming_tile`, `hamming_piece`). Default is `manhattan`.
*   `-w`, `--weight`: Weight factor to multiply the heuristic cost (for A* variants). Default is `2.5`.
*   `-p`, `--performance`: Print the solution time and move count.
*   `-g`, `--graphics`: Launch the Pygame visualization to watch the scramble and solution.

**Examples:**
```bash
# Solve a specific scramble using IDA* and Manhattan distance, and print performance stats
python -m rubik "R U R' F2" -a ida -c manhattan -p

# Generate a 20-move scramble, solve it, and animate the whole process
python -m rubik -s 20 -g
```

### The Interactive Animator (`animate_cube.py`)

You can also run the animator directly if you just want to play with the cube manually or test specific move sequences without running the solver.

```bash
# Launch the animator with a solved cube
python -m rubik.animate_cube

# Launch the animator with an initial sequence applied
python -m rubik.animate_cube "L R U D F B L2 R2 U2 D2 F2 B2"
```

**Controls (Inside the Pygame Window):**

*   `W` = turn UP face clockwise (U)
*   `S` = turn DOWN face clockwise (D)
*   `A` = turn LEFT face clockwise (L)
*   `D` = turn RIGHT face clockwise (R)
*   `E` = turn FRONT face clockwise (F)
*   `Q` = turn BACK face clockwise (B)
*   **Hold `Shift`** with any of the above keys to turn the face **anti-clockwise** (e.g., `Shift + W` = U').
*   `Esc` = Quit the application.