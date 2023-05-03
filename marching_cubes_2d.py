"""Provides a function for performing 2D Marching Cubes"""

import math

from common import Edge, adapt, frange
from settings import XMIN, XMAX, YMIN, YMAX, CELL_SIZE
from utils_2d import V2, make_svg


def marching_cubes_2d_single_cell(f, x, y):
    """Returns a list of edges that approximate f's boundary for a single cell"""

    # Evaluate
    x0y0 = f(x            , y )
    x0y1 = f(x            , y + CELL_SIZE)
    x1y0 = f(x + CELL_SIZE, y)
    x1y1 = f(x + CELL_SIZE, y + CELL_SIZE)

    # There are 16 different cases that these points can be inside or outside.
    # We use binary counting to map the 4 truth values to a number between 0 and 15 inclusive.
    # It's even more in the 3d case!
    case = ((1 if x0y0 > 0 else 0) +
            (2 if x0y1 > 0 else 0) +
            (4 if x1y0 > 0 else 0) +
            (8 if x1y1 > 0 else 0))

    # Several of the cases are inverses of each other where solid is non solid and visa versa
    # They have the same boundary, which cuts down the cases a bit.
    # But we swap the direction of the boundary, so that edges are always winding clockwise around the solid.
    # Getting those swaps correct isn't needed for our simple visualizations, but is important in other uses cases
    # particularly in 3d.

    if case == 0 or case == 15:
        # All outside / inside
        return []
    if case == 1 or case == 14:
        # Single corner
        return [Edge(V2(x + 0 + adapt(x0y0, x1y0), y), V2(x + 0, y + adapt(x0y0, x0y1))).swap(case == 14)]
    if case == 2 or case == 13:
        # Single corner
        return [Edge(V2(x + 0, y + adapt(x0y0, x0y1)), V2(x + adapt(x0y1, x1y1), y + CELL_SIZE)).swap(case == 13)]
    if case == 4 or case == 11:
        # Single corner
        return [Edge(V2(x + CELL_SIZE, y + adapt(x1y0, x1y1)), V2(x + adapt(x0y0, x1y0), y + 0)).swap(case == 11)]
    if case == 8 or case == 7:
        # Single corner
        return [Edge(V2(x + adapt(x0y1, x1y1), y + CELL_SIZE), V2(x + CELL_SIZE, y + adapt(x1y0, x1y1))).swap(case == 7)]
    if case == 3 or case == 12:
        # Vertical split
        return [Edge(V2(x + adapt(x0y0, x1y0), y + 0), V2(x + adapt(x0y1, x1y1), y + CELL_SIZE)).swap(case == 12)]
    if case == 5 or case == 10:
        # Horizontal split
        return [Edge(V2(x + 0, y + adapt(x0y0, x0y1)), V2(x + CELL_SIZE, y + adapt(x1y0, x1y1))).swap(case == 5)]
    if case == 9:
        # Two opposite corners, copy cases 1 and 8
        return [Edge(V2(x + 0 + adapt(x0y0, x1y0), y), V2(x + 0, y + adapt(x0y0, x0y1))),
                Edge(V2(x + adapt(x0y1, x1y1), y + 1), V2(x + CELL_SIZE, y + adapt(x1y0, x1y1)))]
    if case == 6:
        # Two opposite corners, copy cases 2 and 4
        return [Edge(V2(x + CELL_SIZE, y+adapt(x1y0, x1y1)), V2(x+adapt(x0y0, x1y0), y + 0)),
                Edge(V2(x + 0, y+adapt(x0y0, x0y1)), V2(x + adapt(x0y1, x1y1), y + CELL_SIZE))]

    assert False, "All cases exhausted"


def marching_cubes_2d(f, xmin=XMIN, xmax=XMAX, ymin=YMIN, ymax=YMAX):
    # For each cube, evaluate independently.
    # If this wasn't demonstration code, you might actually evaluate them together for efficiency
    edges = []
    for x in frange(xmin, xmax, CELL_SIZE):
        for y in frange(ymin, ymax, CELL_SIZE):
            edges.extend(marching_cubes_2d_single_cell(f, x, y))
    return edges


def circle_function(x, y):
    return 2.5 - math.sqrt(x*x + y*y)


def square_function(x, y):
    return 2.5 - max(abs(x), abs(y))


def t_shape_function(x, y):
    if (x, y) in ((0, 0), (0, 1), (0, -1), (1, 0)):
        return 1
    return -1

__all__ = ["marching_cubes_2d"]

if __name__ == "__main__":
    edges = marching_cubes_2d(circle_function)
    with open("example.svg", "w") as file:
        make_svg(file, edges, circle_function)

