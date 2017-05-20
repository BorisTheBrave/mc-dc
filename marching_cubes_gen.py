"""Reggenerates the 256 cases needed for the 3D Marching Cubes look up table. There's no need to run this,
the values have already been hard coded into marching_cubes_3d"""

# My convention for vertices is:
VERTICES = [
    (0, 0, 0),
    (1, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 0, 1),
    (1, 1, 1),
    (0, 1, 1),
]

# My convention for the edges

EDGES = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),
]

EDGES_BY_VERTSET = {}
for e, (v1, v2) in enumerate(EDGES):
    EDGES_BY_VERTSET[frozenset([v1, v2])] = e

# These are the 15 base cases.
# Each key is the bitwise representation of what is solid
# Each value is a list of triples indicating what edges are used for that triangle
# (Recall each edge of the cell may become a vertex in the output boundary)
# Copied up rather tediously from http://users.polytech.unice.fr/~lingrand/MarchingCubes/algo.html
BASE_CASES = {
    #
    0b00000000: (),
    0b00000001: ((8, 0, 3), ),
    0b00000011: ((8, 1, 3), (8, 9, 1)),
    0b00000101: ((8, 0, 3), (1, 10, 2)),
    #
    0b01000001: ((8, 0, 3), (10, 5, 6)),
    0b00110010: ((8, 7, 0), (0, 7, 1), (1, 7, 5)),
    0b01000011: ((8, 1, 3), (8, 9, 1), (10, 5, 6)),
    0b01001010: ((3, 2, 11), (0, 9, 1), (10, 5, 6)),
    #
    0b00110011: ((7, 5, 3), (3, 5, 1)),
    0b10110001: ((11, 6, 3), (3, 6, 0), (0, 6, 5), (0, 5, 9)),
    0b01101001: ((11, 8, 2), (2, 8, 0), (6, 10, 4), (4, 10, 9)),
    0b01110001: ((3, 7, 0), (0, 7, 10), (7, 6, 10), (0, 10, 9)),
    #
    0b00111010: ((3, 2, 11), (8, 7, 0), (0, 7, 1), (1, 7, 5)),
    0b10100101: ((8, 0, 3), (4, 5, 9), (10, 2, 1), (11, 6, 7)),
    0b10110010: ((8, 11, 0), (0, 11, 5), (5, 11, 6), (0, 5, 1)),
}

# Normally you can invert the base cases (replace solid with empty and visa versa) to generate more cases
# But this leads to a problem - such flips in 3d can swap the cube edges from one ambiguous configuration
# to another.
#
#     *-----o          *-----o
#     |  \  |          | /   |
#     |   \ |          |/    |
#     |\    |          |    /|
#     | \   |          |   / |
#     o-----*          o-----*
#
# This will lead to edges not properly lining up when putting adjacent cells together.
# To solve this, we specify a few more cases, that are flips of the above, but with a different arrangement of edges
# See http://users.polytech.unice.fr/~lingrand/MarchingCubes/algo.html

INVERSE_CASES = {
    255 - 0b00000101: ((3, 2, 8), (8, 2, 10), (8, 10, 1), (8, 1, 0)),
    255 - 0b01000011: ((6, 8, 3), (6, 9, 8), (6, 5, 9),  (6, 3, 1), (6, 1, 10)),
    255 - 0b01001010: ((3, 11, 0), (0, 11, 6), (0, 6, 9), (9, 6, 5), (1, 10, 2)),
    # ?? Docs say these case is needed, but it doesn't appear to be
    # 255 - 0b01101001: ((8, 11, 4), (4, 11, 6), (9, 10, 2), (9, 2, 0)),
    # 255 - 0b00111010: ((8, 0, 3), (2, 7, 11), (7, 2, 1), (7, 1, 5)),
    # ?? Docs say this case is needed, but it looks wrong
    #255 - 0b10100101: ((3, 2, 11), (0, 9, 1), (6, 10, 5), (7, 4, 8)),
}

ALL_CASES = BASE_CASES.copy()

# Add INVERSE_CASES to ALL_CASES
for bits, faces in INVERSE_CASES.items():
    ALL_CASES[bits] = faces


# Most operations are simply vertex permutations
ROTATE_1 = [
    1,
    2,
    3,
    0,
    5,
    6,
    7,
    4,
]
ROTATE_2 = [
    3,
    2,
    6,
    7,
    0,
    1,
    5,
    4
]
ROTATE_3 = [
    1,
    5,
    6,
    2,
    0,
    4,
    7,
    3,
]
REFLECT = [
    1,
    0,
    3,
    2,
    5,
    4,
    7,
    6
]

def bits_to_verts(n):
    """Converts from bitwise representation into an array of vertex indices"""
    return [v for v in range(8) if 2**v & n > 0]


def verts_to_bits(vs):
    """Converts from an array of vertex indices to a bitwise representation"""
    return sum(2**v for v in vs)


def bits_apply(op, n):
    """Applies a vertex permutation operation to a set of vertices in bitwise representation"""
    return verts_to_bits(op[v] for v in bits_to_verts(n))


def faces_apply(op, faces, flip):
    """Applies a vertex permutation to a list of faces, optionally flipping the faces"""
    return [face_apply(op, face, flip) for face in faces]


def face_apply(op, face, flip):
    """Applies a vertex permutation to a list of edges"""
    edges = [edge_apply(op, edge) for edge in face]
    if flip: edges = list(reversed(edges))
    return edges


def edge_apply(op, edge):
    """Applies a vertex permutation to an edge.
    I.e. it permutes both ends of the edge, and finds the new edge that adjoins the two
    resulting vertex indices."""
    vs = frozenset(op[v] for v in EDGES[edge])
    return EDGES_BY_VERTSET[vs]


def compose(*ops):
    """Applies a series of vertex permutations into a single new permutation"""
    if len(ops) == 0:
        return [0, 1, 2, 3, 4, 5, 6, 7]
    if len(ops) == 1:
        return ops[0]
    if len(ops) == 2:
        op1, op2 = ops
        return [op2[op1[v]] for v in range(8)]
    op1 = ops[0]
    rest = ops[1:]
    return compose(op1, compose(*rest))


def pow(op, n):
    """Repeats a vertex permutation n times"""
    return compose(* ([op] * n))

cases = {}

# Brute force try all combinations of operations to generate new entries in cases
# We try inverting last as all, as we want to prefer using an INVERSE_CASE
# to doing an invert operation, as explained above
for invert in (False, True):  # Invert swaps solid for empty and visa versa
    for r1 in range(4):
        for r2 in range(4):
            for r3 in range(4):
                for refl in range(2):
                    op = compose(
                        pow(ROTATE_1, r1),
                        pow(ROTATE_2, r2),
                        pow(ROTATE_3, r3),
                        pow(REFLECT, refl),
                    )
                    # Both REFLECT and invert cause faces to flip
                    flip = invert ^ (refl == 1)
                    for bits, faces in ALL_CASES.items():
                        new_bits = bits_apply(op, bits)
                        if invert:
                            new_bits = 255 - new_bits
                        if new_bits not in cases:
                            new_faces = faces_apply(op, faces, flip)
                            cases[new_bits] = new_faces


# Check that we only reference edges that really are between solid and non solid
def test1():
    for bits in range(256):
        verts = set(bits_to_verts(bits))
        all_edges = set(edge for face in cases[bits] for edge in face)
        for edge in all_edges:
            assert sum(v in verts for v in EDGES[edge]) == 1


def faces_to_edge_pairs(faces):
    return [frozenset([face[i], face[(i + 1) % 3]]) for face in faces for i in range(3)]


# Check that each case is manifold (except on the cell boundary)
def test2():
    from collections import Counter
    for bits in range(256):
        edge_pairs = faces_to_edge_pairs(cases[bits])
        edge_counts = Counter(edge_pairs)
        for edge_pair, count in edge_counts.items():
            # Ok, this edge_pair is used by two faces, forming a continuous surface
            if count == 2: continue
            # Find length squared of edge pair
            def d_midpoint(edge):
                """Returns the midpoint of the edge, scaled by 2"""
                v0, v1 = EDGES[edge]
                v0_pos = VERTICES[v0]
                v1_pos = VERTICES[v1]
                return ((x+y) for (x,y) in zip(v0_pos, v1_pos))
            def length_sq(pos1, pos2):
                """Returns the square of the length of two positions"""
                return sum((x-y)**2 for (x,y) in zip(pos1, pos2))
            edge1, edge2 = edge_pair
            l2 = length_sq(d_midpoint(edge1), d_midpoint(edge2))
            if l2 == 2 or l2 == 4:
                # These are the lengths of the edge_pairs on the boundary
                continue
            assert False


# Check that every face with the same solid/non-solid pattern also has the same edge pattern
def test3():
    CELL_FACES = [
        [0, 1, 2, 3],
        [1, 5, 6, 2],
        [3, 2, 6, 7],
        [4, 0, 3, 7],
        [1, 0, 4, 5],
        [7, 6, 5, 4],
    ]
    for cell_face in CELL_FACES:
        def edge_pair_on_face(edge_pair):
            return all(v in cell_face for e in edge_pair for v in EDGES[e])
        edges_by_case = {}
        for bits in range(256):
            edge_pairs = faces_to_edge_pairs(cases[bits])
            sub_bits = verts_to_bits(set(cell_face) & set(bits_to_verts(bits)))
            sub_edge_pairs = frozenset(filter(edge_pair_on_face, edge_pairs))
            if sub_bits in edges_by_case:
                assert edges_by_case[sub_bits] == sub_edge_pairs
            else:
                edges_by_case[sub_bits] = sub_edge_pairs


if __name__ == "__main__":
    # Run a few tests that we've generated something sensible
    test1()
    test2()
    test3()

    # Dump out the results
    import pprint
    pprint.pprint([cases[i] for i in range(256)])
