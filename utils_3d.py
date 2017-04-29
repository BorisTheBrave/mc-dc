class V3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Tri:
    def __init__(self, v1, v2, v3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

    def map(self, f):
        return Tri(f(self.v1), f(self.v2), f(self.v3))


class Quad:
    def __init__(self, v1, v2, v3, v4):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4

    def map(self, f):
        return Quad(f(self.v1), f(self.v2), f(self.v3), f(self.v4))


    def swap(self, swap=True):
        if swap:
            return Quad(self.v4, self.v3, self.v2, self.v1)
        else:
            return Quad(self.v1, self.v2, self.v3, self.v4)

class Mesh:
    def __init__(self, verts=None, faces=None):
        self.verts = verts or []
        self.faces = faces or []

    def extend(self, other):
        l = len(self.verts)
        f = lambda v: v + l
        self.verts.extend(other.verts)
        self.faces.extend(face.map(f) for face in other.faces)

    def __add__(self, other):
        r = Mesh()
        r.extend(self)
        r.extend(other)
        return r

    def translate(self, offset):
        new_verts = [V3(v.x + offset.x, v.y + offset.y, v.z + offset.z) for v in self.verts]
        return Mesh(new_verts, self.faces)

def make_obj(f, mesh):
    """Crude export to Wavefront mesh format"""
    for v in mesh.verts:
        f.write("v {} {} {}\n".format(v.x, v.y, v.z))
    for face in mesh.faces:
        if isinstance(face, Quad):
            f.write("f {} {} {} {}\n".format(face.v1, face.v2, face.v3, face.v4))
        if isinstance(face, Tri):
            f.write("f {} {} {}\n".format(face.v1, face.v2, face.v3))
