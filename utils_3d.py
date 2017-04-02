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

    def swap(self, swap=True):
        if swap:
            return Face(self.v3, self.v2, self.v1)
        else:
            return Face(self.v1, self.v2, self.v3)

class Quad:
    def __init__(self, v1, v2, v3, v4):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4

    def swap(self, swap=True):
        if swap:
            return Quad(self.v4, self.v3, self.v2, self.v1)
        else:
            return Quad(self.v1, self.v2, self.v3, self.v4)


def make_obj(f, vert_array, faces):
    """Crude export to Wavefront mesh format"""
    for v in vert_array:
        f.write("v {} {} {}\n".format(v.x, v.y, v.z))
    for face in faces:
        if isinstance(face, Quad):
            f.write("f {} {} {} {}\n".format(face.v1, face.v2, face.v3, face.v4))
        if isinstance(face, Tri):
            f.write("f {} {} {}\n".format(face.v1, face.v2, face.v3))
