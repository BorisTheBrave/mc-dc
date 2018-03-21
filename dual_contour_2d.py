"""Provides a function for performing 2D Dual Contouring"""

import math


from common import Edge, adapt
from settings import ADAPTIVE, XMIN, XMAX, YMIN, YMAX
from utils_2d import V2, make_svg
from qef import solve_qef_2d


def dual_contour_2d_find_best_vertex(f, f_normal, x, y):
    if not ADAPTIVE:
        return V2(x+0.5, y+0.5)

    # Evaluate
    x0y0 = f(x + 0.0, y + 0.0)
    x0y1 = f(x + 0.0, y + 1.0)
    x1y0 = f(x + 1.0, y + 0.0)
    x1y1 = f(x + 1.0, y + 1.0)

    # For each edge, identify where there is a sign change
    changes = []
    if (x0y0 > 0) != (x0y1 > 0):
        changes.append([x + 0, y + adapt(x0y0, x0y1)])
    if (x1y0 > 0) != (x1y1 > 0):
        changes.append([x + 1, y + adapt(x1y0, x1y1)])
    if (x0y0 > 0) != (x1y0 > 0):
        changes.append([x + adapt(x0y0, x1y0), y + 0])
    if (x0y1 > 0) != (x1y1 > 0):
        changes.append([x + adapt(x0y1, x1y1), y + 1])

    if len(changes) <= 1:
        return None

    # For each sign change location v[i], we find the normal n[i].

    normals = []
    for v in changes:
        n = f_normal(v[0], v[1])
        normals.append([n.x, n.y])

    v = solve_qef_2d(x, y, changes, normals)

    return v

def dual_contour_2d(f, f_normal, xmin=XMIN, xmax=XMAX, ymin=YMIN, ymax=YMAX):
    """Iterates over a cells of size one between the specified range, and evaluates f and f_normal to produce
    a boundary by Dual Contouring. Returns an unordered list of Edge objects."""
    # For each cell, find the the best vertex for fitting f
    verts = {}
    for x in range(xmin, xmax):
        for y in range(ymin, ymax):
            verts[(x,y)] = dual_contour_2d_find_best_vertex(f, f_normal, x, y)
    # For each cell edge, emit an edge between the center of the adjacent cells if it is a sign changing edge
    edges = []
    for x in range(xmin+1, xmax):
        for y in range(ymin, ymax):
            y0 = y
            y1 = y+1
            y0_solid = f(x, y0) > 0
            y1_solid = f(x, y1) > 0
            if y0_solid != y1_solid:
                edges.append(Edge(verts[(x-1, y)], verts[x, y]).swap(y0_solid))
    for x in range(xmin, xmax):
        for y in range(ymin+1, ymax):
            x0 = x
            x1 = x+1
            x0_solid = f(x0, y) > 0
            x1_solid = f(x1, y) > 0
            if x0_solid != x1_solid:
                edges.append(Edge(verts[(x, y-1)], verts[x, y]).swap(x0_solid))
    return edges


def circle_function(x, y):
    return 2.5 - math.sqrt(x*x + y*y)


def circle_normal(x, y):
    l = math.sqrt(x*x + y*y)
    return V2(-x / l, -y / l)


def square_function(x, y):
    return 2.5 - max(abs(x), abs(y))


def square_normal(x, y):
    if abs(x) > abs(y):
        return V2(-math.copysign(x, 1), 0)
    else:
        return V2(0, -math.copysign(y, 1))

def normal_from_function(f, d=0.01):
    """Given a sufficiently smooth 2d function, f, returns a function approximating of the gradient of f.
    d controls the scale, smaller values are a more accurate approximation."""
    def norm(x, y):
        return V2(
            (f(x + d, y) - f(x - d, y)) / 2 / d,
            (f(x, y + d) - f(x, y - d)) / 2 / d,
        ).normalize()
    return norm



def t_shape_function(x, y):
    if (x, y) in ((0, 0), (0, 1), (0, -1), (1, 0)):
        return 1
    return -1


def intersect_function(x, y):
    y -= 0.3
    x -= 0.5
    x = abs(x)
    #x += x*x / 1000
    return min(x - y, x + y)


__all__ = ["dual_contour_2d"]

if __name__ == "__main__":
    edges = dual_contour_2d(intersect_function, normal_from_function(intersect_function, 0.001))
    with open("example.svg", "w") as file:
        make_svg(file, edges, intersect_function)

