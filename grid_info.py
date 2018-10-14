images_names = [
    "grid_empty",

    "grid_painted",
    "grid_marked",

    "grid_triangle_dotted",
    "grid_triangle_filled",
    "grid_triangle_hole",
    "grid_triangle_hole_filled",

    "grid_square_dotted",
    "grid_square_filled",
    "grid_square_hole",
    "grid_square_hole_filled",

    "grid_circle_dotted",
    "grid_circle_filled",
    "grid_circle_hole",
    "grid_circle_hole_filled",

    "grid_winning_square",
    "grid_wall",
]


LEVEL_MAX_SIZE = 21
IMAGE_SIZE = 20

EMPTY = 0

PAINTED = 1 << 0
MARKER = 1 << 1

SHAPE_TRIANGLE = 0b01 << 2
SHAPE_SQUARE = 0b10 << 2
SHAPE_CIRCLE = 0b11 << 2

FILLED = 1 << 4
HOLE = 1 << 5

WINNING_SQUARE = 1 << 6
WALL = 1 << 7
NUMBER = 1 << 8

grid_types = [
    EMPTY,

    PAINTED,
    MARKER,

    SHAPE_TRIANGLE,
    SHAPE_TRIANGLE | FILLED,
    SHAPE_TRIANGLE | HOLE,
    SHAPE_TRIANGLE | HOLE | FILLED,

    SHAPE_SQUARE,
    SHAPE_SQUARE | FILLED,
    SHAPE_SQUARE | HOLE,
    SHAPE_SQUARE | HOLE | FILLED,

    SHAPE_CIRCLE,
    SHAPE_CIRCLE | FILLED,
    SHAPE_CIRCLE | HOLE,
    SHAPE_CIRCLE | HOLE | FILLED,

    WINNING_SQUARE,
    WALL,

    NUMBER,  # number data goes on left bits
]

reversed_names = {type: name for type, name in zip(grid_types, images_names)}

def square_number_set(number):
    return NUMBER | (number << 9)

def square_number_get(square_type):
    return (square_type & ~NUMBER) >> 9

def get_image_from_type(square_type):
    return reversed_names[square_type]
