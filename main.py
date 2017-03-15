import math
import numpy
import numpy.linalg

from common import Edge, adapt
from settings import ADAPTIVE, XMIN, XMAX, YMIN, YMAX


class V2:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def marching_cubes_2d_single_cell(f, x, y):
    """Returns a list of edges that approximate f's boundary for a single cell"""

    # Evaluate
    x0y0 = f(x + 0.0, y + 0.0)
    x0y1 = f(x + 0.0, y + 1.0)
    x1y0 = f(x + 1.0, y + 0.0)
    x1y1 = f(x + 1.0, y + 1.0)

    # There are 16 different cases that these points can be inside or outside
    # It's even more in the 3d case!
    case = ((1 if x0y0 > 0 else 0) +
            (2 if x0y1 > 0 else 0) +
            (4 if x1y0 > 0 else 0) +
            (8 if x1y1 > 0 else 0))

    # Several of the cases are inverses of each other where solid is non solid and visa versa
    # They have the same boundary, which cuts down the cases a bit.
    # But we swap the direction of the boundary, so that edges are always winding clockwise around the solid.

    if case is 0 or case is 15:
        # All outside / inside
        return []
    if case is 1 or case is 14:
        # Single corner
        return [Edge(V2(x+0+adapt(x0y0, x1y0), y), V2(x+0, y+adapt(x0y0, x0y1))).swap(case is 14)]
    if case is 2 or case is 13:
        # Single corner
        return [Edge(V2(x + 0, y + adapt(x0y0, x0y1)), V2(x + adapt(x0y1, x1y1), y + 1)).swap(case is 11)]
    if case is 4 or case is 11:
        # Single corner
        return [Edge(V2(x + 1, y + adapt(x1y0, x1y1)), V2(x + adapt(x0y0, x1y0), y + 0)).swap(case is 13)]
    if case is 8 or case is 7:
        # Single corner
        return [Edge(V2(x+adapt(x0y1, x1y1), y+1), V2(x+1, y+adapt(x1y0, x1y1))).swap(case is 7)]
    if case is 3 or case is 12:
        # Vertical split
        return [Edge(V2(x+adapt(x0y0, x1y0), y+0), V2(x+adapt(x0y1, x1y1), y+1)).swap(case is 10)]
    if case is 5 or case is 10:
        # Horizontal split
        return [Edge(V2(x+0, y+adapt(x0y0, x0y1)), V2(x+1, y+adapt(x1y0, x1y1))).swap(case is 5)]
    if case is 9:
        # Two opposite corners, copy cases 1 and 8
        return [Edge(V2(x + 0 + adapt(x0y0, x1y0), y), V2(x + 0, y + adapt(x0y0, x0y1))),
                Edge(V2(x + adapt(x0y1, x1y1), y + 1), V2(x + 1, y + adapt(x1y0, x1y1)))]
    if case is 6:
        # Two opposite corners, copy cases 2 and 4
        return [Edge(V2(x+1, y+adapt(x1y0, x1y1)), V2(x+adapt(x0y0, x1y0), y+0)),
                Edge(V2(x+0, y+adapt(x0y0, x0y1)), V2(x+adapt(x0y1, x1y1), y+1))]

    assert False, "All cases exhausted"


def marching_cubes_2d(f, xmin=XMIN, xmax=XMAX, ymin=YMIN, ymax=YMAX):
    # For each cube, evaluate independently.
    # If this wasn't demonstration code, you might actually evaluate them together for efficiency
    edges = []
    for x in range(xmin, xmax):
        for y in range(ymin, ymax):
            edges.extend(marching_cubes_2d_single_cell(f, x, y))
    return edges


def dual_cont_2d_find_best_vertex(f, f_normal, x, y):
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
        changes.append(V2(x + 0, y + adapt(x0y0, x0y1)))
    if (x1y0 > 0) != (x1y1 > 0):
        changes.append(V2(x + 1, y + adapt(x1y0, x1y1)))
    if (x0y0 > 0) != (x1y0 > 0):
        changes.append(V2(x + adapt(x0y0, x1y0), y + 0))
    if (x0y1 > 0) != (x1y1 > 0):
        changes.append(V2(x + adapt(x0y1, x1y1), y + 1))

    if len(changes) <= 1:
        return None

    # For each sign change location v[i], we find the normal n[i].
    # The error term we are trying to minimize is sum( dot(x-v[i], n[i]) ^ 2)

    # In other words, minimize || A * x - b || ^2 where A and b are a matrix and vector
    # derived from v and n

    normals = []
    for v in changes:
        n = f_normal(v.x, v.y)
        normals.append([n.x, n.y])

    A = numpy.array(normals)
    b = [v.x*n[0]+v.y*n[1] for v, n in zip(changes, normals)]
    result, residual, rank, s = numpy.linalg.lstsq(A, b)
    return V2(result[0], result[1])


def dual_cont_2d(f, f_normal, xmin=XMIN, xmax=XMAX, ymin=YMIN, ymax=YMAX):
    # For each cell, find the the best vertex for fitting f
    verts = {}
    for x in range(xmin, xmax):
        for y in range(ymin, ymax):
            verts[(x,y)] = dual_cont_2d_find_best_vertex(f, f_normal, x, y)
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


def element(e, **kwargs):
    s = "<" + e
    for key, value in kwargs.items():
        s += " {}='{}'".format(key, value)
    s += "/>\n"
    return s


def make_svg(file):
    f = circle_function
    f_norm = circle_normal
    #f = square_function
    #f_norm = square_normal
    #f = t_shape_function
    #f_norm = None
    scale = 50
    file.write("<svg viewBox='{} {} {} {}'>\n".format(
        XMIN*scale, YMIN*scale, (XMAX-XMIN)*scale, (YMAX-YMIN)*scale))

    # Draw grid
    for x in range(XMIN, XMAX):
        for y in range(YMIN, YMAX):
            file.write(element("rect", x=x*scale, y=y*scale, width=scale, height=scale,
                               style="stroke: grey; stoke-width: 1; fill: none"))

    # Draw filled / unfilled circles
    for x in range(XMIN, XMAX+1):
        for y in range(YMIN, YMAX+1):
            is_solid = f(x, y) > 0
            fill_color = ("black" if is_solid else "white")
            file.write(element("circle", cx=x*scale, cy=y*scale, r=0.05*scale,
                               style="stroke: black; stoke-width: 1; fill: " + fill_color))
    # Draw edges
    edges = marching_cubes_2d(f)
    #edges = dual_cont_2d(f, f_norm)
    for edge in edges:
        file.write(element("line", x1=edge.v1.x*scale, y1=edge.v1.y*scale, x2=edge.v2.x*scale, y2=edge.v2.y*scale,
                           style='stroke:rgb(255,0,0);stroke-width:2'))

    # Draw vertices
    r = 0.05
    for v in [v for edge in edges for v in (edge.v1, edge.v2) ]:
        file.write(element("rect", x=(v.x-r)*scale, y=(v.y-r)*scale, width=2*r*scale, height=2*r*scale,
                           style='fill: red'))

    file.write("</svg>\n")


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


def t_shape_function(x, y):
    if (x, y) in ((0, 0), (0, 1), (0, -1), (1, 0)):
        return 1
    return -1

with open("example.svg", "w") as file:
    make_svg(file)

