
from src.environment.board import (
    EMPTY,
    GREEN_APPLE,
    RED_APPLE,
)


WALL = "W"
HEAD = "H"
BODY = "S"
GREEN = "G"
RED = "R"
EMPTY_CELL = "0"

DISTANCE_LEVELS = 5


def get_cell_value(game, position):

    if not game.board.is_inside(position):
        return WALL

    if position == game.snake.head:
        return HEAD

    if position in game.snake.body[1:]:
        return BODY

    x, y = position
    value = game.board.grid[y][x]

    if value == GREEN_APPLE:
        return GREEN

    if value == RED_APPLE:
        return RED

    if value == EMPTY:
        return EMPTY_CELL

    return EMPTY_CELL


def get_ray(game, direction):

    x, y = game.snake.head

    movements = {
        "UP": (0, -1),
        "DOWN": (0, 1),
        "LEFT": (-1, 0),
        "RIGHT": (1, 0),
    }

    if direction not in movements:
        raise ValueError("Invalid direction.")

    dx, dy = movements[direction]

    vision = []

    x += dx
    y += dy

    while game.board.is_inside((x, y)):

        vision.append(
            get_cell_value(game, (x, y))
        )

        x += dx
        y += dy

    vision.append(WALL)

    return vision


def get_vision(game):

    directions = (
        "UP",
        "DOWN",
        "LEFT",
        "RIGHT",
    )

    return {
        direction: get_ray(game, direction)
        for direction in directions
    }


def get_distance_bucket(distance, ray_length):

    if ray_length <= 0:
        return 0

    bucket = (
        (distance - 1) * DISTANCE_LEVELS
    ) // ray_length

    return min(
        DISTANCE_LEVELS - 1,
        bucket
    )


def encode_ray(ray):

    cells = ray[:-1]

    # Distance jusqu'au mur, plafonnée à 5.
    wall_distance = min(
        len(ray),
        DISTANCE_LEVELS
    )

    nearest = {
        BODY: None,
        GREEN: None,
        RED: None,
    }

    for distance, cell in enumerate(cells, start=1):

        if cell in nearest and nearest[cell] is None:

            nearest[cell] = get_distance_bucket(
                distance,
                len(cells)
            )

    encoded = [
        f"W{wall_distance}",
    ]

    for symbol in (BODY, GREEN, RED):

        distance = nearest[symbol]

        if distance is None:
            encoded.append(f"{symbol}-")
        else:
            encoded.append(
                f"{symbol}{distance}"
            )

    return "".join(encoded)


def encode_state(vision, direction):

    if direction not in (
        "UP",
        "DOWN",
        "LEFT",
        "RIGHT",
    ):
        raise ValueError("Invalid direction.")

    state = "DIR:" + direction + "|"

    for current_direction in (
        "UP",
        "DOWN",
        "LEFT",
        "RIGHT",
    ):

        state += current_direction + ":"

        state += encode_ray(
            vision[current_direction]
        )

        state += "|"

    return state
