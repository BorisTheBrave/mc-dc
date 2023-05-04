"""Provides a function for performing 3D Dual Countouring"""

from common import adapt, frange
from settings import ADAPTIVE, XMIN, XMAX, YMIN, YMAX, ZMIN, ZMAX, CELL_SIZE
import numpy as np
import math
from utils_3d import V3, Quad, Mesh, make_obj
from qef import solve_qef_3d


def dual_contour_3d_find_best_vertex(f, f_normal, x, y, z):
    if not ADAPTIVE:
        return V3(x+0.5*CELL_SIZE, y+0.5*CELL_SIZE, z+0.5*CELL_SIZE)

    # Evaluate f at each corner
    v = np.empty((2, 2, 2))
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0,1):
                v[dx, dy, dz] = f(x + dx * CELL_SIZE, y + dy * CELL_SIZE, z + dz * CELL_SIZE)

    # For each edge, identify where there is a sign change.
    # There are 4 edges along each of the three axes
    changes = []
    for dx in (0, 1):
        for dy in (0, 1):
            if (v[dx, dy, 0] > 0) != (v[dx, dy, 1] > 0):
                changes.append((x + dx * CELL_SIZE, 
                                y + dy * CELL_SIZE,
                                z + adapt(v[dx, dy, 0],v[dx, dy, 1])))

    for dx in (0, 1):
        for dz in (0, 1):
            if (v[dx, 0, dz] > 0) != (v[dx, 1, dz] > 0):
                changes.append((x + dx * CELL_SIZE,
                                y + adapt(v[dx, 0, dz], v[dx, 1, dz]),
                                z + dz * CELL_SIZE))

    for dy in (0, 1):
        for dz in (0, 1):
            if (v[0, dy, dz] > 0) != (v[1, dy, dz] > 0):
                changes.append((x + adapt(v[0, dy, dz], v[1, dy, dz]),
                                y + dy * CELL_SIZE,
                                z + dz * CELL_SIZE))

    if len(changes) <= 1:
        return None

    # For each sign change location v[i], we find the normal n[i].
    # The error term we are trying to minimize is sum( dot(x-v[i], n[i]) ^ 2)

    # In other words, minimize || A * x - b || ^2 where A and b are a matrix and vector
    # derived from v and n

    normals = []
    for v in changes:
        n = f_normal(v[0], v[1], v[2])
        normals.append([n.x, n.y, n.z])

    return solve_qef_3d(x, y, z, changes, normals)


def dual_contour_3d(f, f_normal, xmin=XMIN, xmax=XMAX, ymin=YMIN, ymax=YMAX, zmin=ZMIN, zmax=ZMAX):
    """Iterates over a cells of size one between the specified range, and evaluates f and f_normal to produce
        a boundary by Dual Contouring. Returns a Mesh object."""
    # For each cell, find the the best vertex for fitting f
    vert_array = []
    vert_indices = {}
    for ix, x in enumerate(frange(xmin, xmax, CELL_SIZE)):
        for iy, y in enumerate(frange(ymin, ymax, CELL_SIZE)):
            for iz, z in enumerate(frange(zmin, zmax, CELL_SIZE)):
                vert = dual_contour_3d_find_best_vertex(f, f_normal, x, y, z)
                if vert is None:
                    continue
                vert_array.append(vert)
                vert_indices[ix, iy, iz] = len(vert_array)

    # For each cell edge, emit an face between the center of the adjacent cells if it is a sign changing edge
    faces = []
    for ix, x in enumerate(frange(xmin, xmax, CELL_SIZE)):
        for iy, y in enumerate(frange(ymin, ymax, CELL_SIZE)):
            for iz, z in enumerate(frange(zmin, zmax, CELL_SIZE)):
                if x > xmin and y > ymin:
                    solid1 = f(x, y, z + 0) > 0
                    solid2 = f(x, y, z + CELL_SIZE) > 0
                    if solid1 != solid2:
                        faces.append(Quad(
                            vert_indices[(ix - 1, iy - 1, iz)],
                            vert_indices[(ix - 0, iy - 1, iz)],
                            vert_indices[(ix - 0, iy - 0, iz)],
                            vert_indices[(ix - 1, iy - 0, iz)],
                        ).swap(solid2))
                if x > xmin and z > zmin:
                    solid1 = f(x, y + 0, z) > 0
                    solid2 = f(x, y + CELL_SIZE, z) > 0
                    if solid1 != solid2:
                        faces.append(Quad(
                            vert_indices[(ix - 1, iy, iz - 1)],
                            vert_indices[(ix - 0, iy, iz - 1)],
                            vert_indices[(ix - 0, iy, iz - 0)],
                            vert_indices[(ix - 1, iy, iz - 0)],
                        ).swap(solid1))
                if y > ymin and z > zmin:
                    solid1 = f(x + 0, y, z) > 0
                    solid2 = f(x + CELL_SIZE, y, z) > 0
                    if solid1 != solid2:
                        faces.append(Quad(
                            vert_indices[(ix, iy - 1, iz - 1)],
                            vert_indices[(ix, iy - 0, iz - 1)],
                            vert_indices[(ix, iy - 0, iz - 0)],
                            vert_indices[(ix, iy - 1, iz - 0)],
                        ).swap(solid2))

    return Mesh(vert_array, faces)


def circle_function(x, y, z):
    return 2.5 - math.sqrt(x*x + y*y + z*z)


def circle_normal(x, y, z):
    l = math.sqrt(x*x + y*y + z*z)
    return V3(-x / l, -y / l, -z / l)

def intersect_function(x, y, z):
    y -= 0.3
    x -= 0.5
    x = abs(x)
    return min(x - y, x + y)

def normal_from_function(f, d=0.01):
    """Given a sufficiently smooth 3d function, f, returns a function approximating of the gradient of f.
    d controls the scale, smaller values are a more accurate approximation."""
    def norm(x, y, z):
        return V3(
            (f(x + d, y, z) - f(x - d, y, z)) / 2 / d,
            (f(x, y + d, z) - f(x, y - d, z)) / 2 / d,
            (f(x, y, z + d) - f(x, y, z - d)) / 2 / d,
        ).normalize()
    return norm

__all__ = ["dual_contour_3d"]

if __name__ == "__main__":
    mesh = dual_contour_3d(circle_function, normal_from_function(circle_function))
    with open("output.obj", "w") as f:
        make_obj(f, mesh)
