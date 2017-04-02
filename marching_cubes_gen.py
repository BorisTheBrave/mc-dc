# Generates the 256 cases of marching cubes

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
    0b01000001: ((8, 0, 3), (10, 6, 5)),
    0b00110010: ((8, 7, 0), (0, 7, 1), (1, 7, 5)),
    0b01000011: ((8, 1, 3), (8, 9, 1), (10, 6, 5)),
    0b01001010: ((3, 2, 11), (0, 9, 1), (10, 6, 5)),
    #
    0b00110011: ((7, 5, 3), (3, 5, 1)),
    0b10110001: ((11, 6, 3), (3, 6, 0), (0, 6, 5), (0, 5, 9)),
    0b01101001: ((11, 8, 2), (8, 2, 0), (6, 10, 4), (4, 10, 9)),
    0b01110001: ((3, 7, 0), (0, 7, 10), (7, 6, 10), (0, 10, 9)),
    #
    0b00111010: ((3, 2, 11), (8, 7, 0), (0, 7, 1), (1, 7, 5)),
    0b10100101: ((8, 0, 3), (4, 5, 9), (10, 2, 1), (11, 6, 7)),
    0b10110010: ((8, 11, 0), (0, 11, 5), (5, 11, 6), (0, 5, 1)),
}


# Most opererations are simply vertex permutations
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
for r1 in range(4):
    for r2 in range(4):
        for r3 in range(4):
            for refl in range(2):
                for invert in (False, True): # Invert swaps solid for empty and visa versa
                    op = compose(
                        pow(ROTATE_1, r1),
                        pow(ROTATE_2, r2),
                        pow(ROTATE_3, r3),
                        pow(REFLECT, refl),
                    )
                    # Both REFLECT and invert cause faces to flip
                    flip = invert ^ (refl == 1)
                    for bits, faces in BASE_CASES.items():
                        new_bits = bits_apply(op, bits)
                        if invert:
                            new_bits = 255 - new_bits
                        if new_bits not in cases:
                            new_faces = faces_apply(op, faces, flip)
                            cases[new_bits] = new_faces

# Dump out the results
# Important - we've made no attempt to deal with ambiguities when inverting
# which means the generated meshes can have holes in. Dealing with this
# is out of scope at present.
import pprint
pprint.pprint([cases[i] for i in range(256)])