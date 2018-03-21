"""Contains utilities common to 2d meshing methods"""

from settings import XMIN, XMAX, YMIN, YMAX
import math

class V2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def normalize(self):
        d = math.sqrt(self.x*self.x+self.y*self.y)
        return V2(self.x / d, self.y / d)


def element(e, **kwargs):
    """Utility function used for rendering svg"""
    s = "<" + e
    for key, value in kwargs.items():
        s += " {}='{}'".format(key, value)
    s += "/>\n"
    return s


def make_svg(file, edges, f):
    """Writes an svg file showing the given edges and solidity"""
    scale = 50
    file.write("<?xml version='1.0' encoding='UTF-8'?>\n")
    file.write("<svg version='1.1' xmlns='http://www.w3.org/2000/svg' viewBox='{} {} {} {}'>\n".format(
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
    for edge in edges:
        file.write(element("line", x1=edge.v1.x*scale, y1=edge.v1.y*scale, x2=edge.v2.x*scale, y2=edge.v2.y*scale,
                           style='stroke:rgb(255,0,0);stroke-width:2'))

    # Draw vertices
    r = 0.05
    for v in [v for edge in edges for v in (edge.v1, edge.v2) ]:
        file.write(element("rect", x=(v.x-r)*scale, y=(v.y-r)*scale, width=2*r*scale, height=2*r*scale,
                           style='fill: red'))

    file.write("</svg>\n")