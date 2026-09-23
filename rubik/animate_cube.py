import sys
from dataclasses import replace

import pygame

# Import from your existing cube module
from rubik.cube import SOLVED, Colour, Cube, pack_8_colours, unpack_8_colours

# --- Configuration ---
TILE_SIZE = 35
MARGIN = 5
# Frames per quarter-turn (divisible by 3 for perfectly smooth outer rings)
ANIM_FRAMES = 21
ANIM_FPS = 60           # Framerate of the animation
PAUSE_BETWEEN = 150     # Milliseconds to pause between distinct moves
BG_COLOUR = (30, 30, 30)

# RGB mapping for your Colour enum
COLOURS = {
    'B': (0, 81, 186),    # Blue
    'G': (0, 158, 96),    # Green
    'W': (255, 255, 255), # White
    'Y': (255, 213, 0),   # Yellow
    'R': (196, 30, 58),   # Red
    'O': (255, 88, 0)     # Orange
}

# The grid mapping corresponding exactly to your __str__ layout
TILES = [
    (0, 0, 'D', 0), (5, 0, 'D', 7), (10, 0, 'D', 6),

    (2, 1, 'B', 2), (5, 1, 'B', 3), (8, 1, 'B', 4),

    (1, 2, 'L', 6), (3, 2, 'B', 1), (7, 2, 'B', 5), (9, 2, 'R', 2),

    (2, 3, 'L', 7), (4, 3, 'B', 0), (5, 3, 'B', 7), (6, 3, 'B', 6),
    (8, 3, 'R', 1),

    (3, 4, 'L', 0), (4, 4, 'U', 0), (5, 4, 'U', 1), (6, 4, 'U', 2),
    (7, 4, 'R', 0),

    (0, 5, 'D', 1), (1, 5, 'L', 5), (3, 5, 'L', 1), (4, 5, 'U', 7),
    (6, 5, 'U', 3), (7, 5, 'R', 7), (9, 5, 'R', 3), (10, 5, 'D', 5),

    (3, 6, 'L', 2), (4, 6, 'U', 6), (5, 6, 'U', 5), (6, 6, 'U', 4),
    (7, 6, 'R', 6),

    (2, 7, 'L', 3), (4, 7, 'F', 0), (5, 7, 'F', 1), (6, 7, 'F', 2),
    (8, 7, 'R', 5),

    (1, 8, 'L', 4), (3, 8, 'F', 7), (7, 8, 'F', 3), (9, 8, 'R', 4),

    (2, 9, 'F', 6), (5, 9, 'F', 5), (8, 9, 'F', 4),

    (0, 10, 'D', 2), (5, 10, 'D', 3), (10, 10, 'D', 4)
]

# Quick lookup mapping: 'U4' -> (gx, gy)
POS_MAP = {f"{face}{idx}": (gx, gy) for gx, gy, face, idx in TILES}

CENTERS = [
    (5, 2, 'O'), (2, 5, 'G'), (5, 5, 'W'), (8, 5, 'B'), (5, 8, 'R')
]

# Define the exact clockwise perimeter paths for the 2D layout.
VISUAL_RINGS = [

    ['U0', 'U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7'],
    ['B0', 'B7', 'B6', 'R0', 'R7', 'R6', 'F2', 'F1', 'F0', 'L2', 'L1', 'L0'],

    ['F0', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7'],
    ['U6', 'U5', 'U4', 'R6', 'R5', 'R4', 'D4', 'D3', 'D2', 'L4', 'L3', 'L2'],

    ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7'],
    ['U2', 'U3', 'U4', 'F2', 'F3', 'F4', 'D4', 'D5', 'D6', 'B4', 'B5', 'B6'],

    ['B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'],
    ['D0', 'D7', 'D6', 'R2', 'R1', 'R0', 'U2', 'U1', 'U0', 'L0', 'L7', 'L6'],

    ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7'],
    ['U0', 'U7', 'U6', 'F0', 'F7', 'F6', 'D2', 'D1', 'D0', 'B2', 'B1', 'B0'],

    ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7'],
    ['F6', 'F5', 'F4', 'R4', 'R3', 'R2', 'B4', 'B3', 'B2', 'L6', 'L5', 'L4']
]


def get_move_mapping(move: str) -> dict:
    """Returns a dict mapping 'StartPos' -> 'EndPos' for a given move."""
    face_names = ["R", "L", "U", "D", "F", "B"]
    c_args = []

    for i in range(6):
        packed = 0
        for j in range(8):
            packed |= ((i * 8 + j) & 0xFF) << (j * 8)
        c_args.append(packed)

    id_cube = Cube(*c_args)
    id_cube.turn(move)

    mapping = {}
    for face in face_names:
        tiles = unpack_8_colours(getattr(id_cube, face))
        for idx, val in enumerate(tiles):
            orig_face = face_names[val // 8]
            orig_idx = val % 8
            mapping[f"{orig_face}{orig_idx}"] = f"{face}{idx}"

    return mapping


def get_path(start_pos, end_pos):
    """Extract step-by-step intermediate path array from the visual rings."""
    for ring in VISUAL_RINGS:
        if start_pos in ring and end_pos in ring:
            si = ring.index(start_pos)
            ei = ring.index(end_pos)
            length = len(ring)
            diff = (ei - si) % length

            if diff in [2, 3]:
                return [ring[(si + i) % length] for i in range(diff + 1)]
            elif diff in [length - 2, length - 3]:
                diff_back = (length - diff)
                return [ring[(si - i) % length] for i in range(diff_back + 1)]

    return [start_pos, end_pos]


# --- Drawing Helpers ---


def draw_static_centers(surface):
    """Draw the background and the non-moving center circles."""
    surface.fill(BG_COLOUR)
    for grid_x, grid_y, char in CENTERS:
        draw_tile(surface, grid_x, grid_y, char, is_center=True)


def draw_dotted_line(
    surface, p1, p2, color=(100, 100, 100), radius=2, spacing=10
):
    """Draw a dotted line between two pixel coordinates for orbits."""
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    dist = (dx**2 + dy**2)**0.5
    if dist == 0:
        return

    num_dots = int(dist / spacing)
    for i in range(num_dots + 1):
        t = i / max(1, num_dots)
        cx = x1 + dx * t
        cy = y1 + dy * t
        pygame.draw.circle(surface, color, (int(cx), int(cy)), radius)


def draw_all_orbits(surface):
    """Draw all the dotted line orbits for every visual ring on the cube."""
    for ring in VISUAL_RINGS:
        for i in range(len(ring)):
            p1_pos = POS_MAP[ring[i]]
            p2_pos = POS_MAP[ring[(i + 1) % len(ring)]]

            x1 = MARGIN + p1_pos[0] * (TILE_SIZE + MARGIN) + TILE_SIZE / 2
            y1 = MARGIN + p1_pos[1] * (TILE_SIZE + MARGIN) + TILE_SIZE / 2
            x2 = MARGIN + p2_pos[0] * (TILE_SIZE + MARGIN) + TILE_SIZE / 2
            y2 = MARGIN + p2_pos[1] * (TILE_SIZE + MARGIN) + TILE_SIZE / 2

            draw_dotted_line(surface, (x1, y1), (x2, y2))


def draw_tile(
    surface, gx: float, gy: float, color_char: str, is_center: bool = False
):
    """Draw a colored circle at a specific grid coordinate."""
    center_x = MARGIN + gx * (TILE_SIZE + MARGIN) + TILE_SIZE / 2
    center_y = MARGIN + gy * (TILE_SIZE + MARGIN) + TILE_SIZE / 2
    radius = TILE_SIZE // 2

    pygame.draw.circle(
        surface, COLOURS[color_char], (center_x, center_y), radius
    )
    if is_center:
        hole_radius = int(radius * 0.65)
        pygame.draw.circle(
            surface, BG_COLOUR, (center_x, center_y), hole_radius
        )


def draw_static_cube(surface, cube: Cube):
    """Draw the cube instantly without animation."""
    draw_static_centers(surface)
    draw_all_orbits(surface)
    for face in ["R", "L", "U", "D", "F", "B"]:
        tiles = unpack_8_colours(getattr(cube, face))
        for idx, color_int in enumerate(tiles):
            pos_key = f"{face}{idx}"
            gx, gy = POS_MAP[pos_key]
            draw_tile(surface, gx, gy, Colour(color_int).name)
    pygame.display.flip()


# --- Animation Helpers ---


def expand_double_turns(moves: list[str]) -> list[tuple[str, bool]]:
    """Convert half turns into two continuous quarter turns."""
    steps = []
    for m in moves:
        if m.endswith('2'):
            steps.extend([(m[0], False), (m[0], True)])
        else:
            steps.append((m, True))
    return steps


def calculate_trajectories(cube: Cube, move: str) -> tuple[list, list]:
    """Compute visual paths for moving tiles and identify static ones."""
    actual_colors = {}
    for face in ["R", "L", "U", "D", "F", "B"]:
        tiles = unpack_8_colours(getattr(cube, face))
        for idx, color_int in enumerate(tiles):
            actual_colors[f"{face}{idx}"] = Colour(color_int).name

    mapping = get_move_mapping(move)
    stationary = []
    moving = []

    for orig_pos, end_pos in mapping.items():
        if orig_pos == end_pos:
            stationary.append((orig_pos, actual_colors[orig_pos]))
        else:
            path_names = get_path(orig_pos, end_pos)
            moving.append({
                'color': actual_colors[orig_pos],
                'path': [POS_MAP[p] for p in path_names]
            })

    return stationary, moving


def draw_animation_frame(screen, eased_t: float, stationary: list, moving: list):
    """Render a single interpolated frame of the cube's transition."""
    draw_static_centers(screen)
    draw_all_orbits(screen)

    for pos_key, color in stationary:
        gx, gy = POS_MAP[pos_key]
        draw_tile(screen, gx, gy, color)

    for data in moving:
        path = data['path']
        n = len(path)

        segment_t = eased_t * (n - 1)
        idx = int(segment_t)

        # Clamp to prevent index errors at t=1.0
        if idx >= n - 1:
            idx = n - 2
            local_t = 1.0
        else:
            local_t = segment_t - idx

        p0_x, p0_y = path[idx]
        p1_x, p1_y = path[idx + 1]

        curr_x = p0_x + (p1_x - p0_x) * local_t
        curr_y = p0_y + (p1_y - p0_y) * local_t

        draw_tile(screen, curr_x, curr_y, data['color'])

    pygame.display.flip()


def handle_input_events(move_queue: list[tuple[str, bool]]) -> bool:
    """Process Pygame events and update the move queue. Returns False to quit."""
    key_map = {
        pygame.K_a: 'L',
        pygame.K_d: 'R',
        pygame.K_w: 'U',
        pygame.K_s: 'D',
        pygame.K_q: 'B',
        pygame.K_e: 'F'
    }

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key in key_map:
                move = key_map[event.key]
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    move += "'"
                move_queue.append((move, False))

    return True


def animate_single_step(screen, clock, cube: Cube, move: str):
    """Calculate trajectories and render the frame-by-frame animation of a move."""
    stationary_tiles, moving_tiles = calculate_trajectories(cube, move)

    for frame in range(1, ANIM_FRAMES + 1):
        pygame.event.pump()

        t = frame / ANIM_FRAMES
        eased_t = t * t * (3 - 2 * t)

        draw_animation_frame(screen, eased_t, stationary_tiles, moving_tiles)
        clock.tick(ANIM_FPS)

    cube.turn(move)


# --- Main Logic ---


def run_interactive_cube(start_cube: Cube, initial_moves: list[str] = None):
    """Launch the Pygame window, animate initial moves, and wait for user input."""
    pygame.init()

    width = 11 * TILE_SIZE + 12 * MARGIN
    screen = pygame.display.set_mode((width, width))
    pygame.display.set_caption("Rubik's Cube Interactive Animator")

    clock = pygame.time.Clock()
    current_cube = replace(start_cube)

    move_queue = expand_double_turns(initial_moves) if initial_moves else []

    draw_static_cube(screen, current_cube)
    if move_queue:
        pygame.time.wait(1000)

    running = True
    while running:
        # 1. Process OS and Keyboard Events
        running = handle_input_events(move_queue)

        # 2. Process Animations if the queue has moves
        if running and move_queue:
            anim_move, pause_after = move_queue.pop(0)

            animate_single_step(screen, clock, current_cube, anim_move)

            if pause_after and move_queue:
                pygame.time.wait(PAUSE_BETWEEN)

        # 3. Idle State
        elif running:
            clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    scramble_moves = "L R U D F B L2 R2 U2 D2 F2 B2 L' R' U' D' F' B'".split()
    test_cube = replace(SOLVED)

    print(f"Applying test scramble: {' '.join(scramble_moves)}")
    print("Controls: W=U, S=D, A=L, D=R, Q=B, E=F (Hold Shift for Prime moves)")
    run_interactive_cube(test_cube, scramble_moves)
