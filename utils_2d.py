"""Contains utilities common to 2d meshing methods"""

from settings import XMIN, XMAX, YMIN, YMAX, CELL_SIZE, EPS
from common import frange
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

    file.write("<g transform='scale({})'>\n".format(scale))
    # Draw grid
    for x in frange(XMIN, XMAX, CELL_SIZE):
        for y in frange(YMIN, YMAX, CELL_SIZE):
            file.write(element("rect", x=x, y=y, width=CELL_SIZE, height=CELL_SIZE,
                               style="stroke: grey; stroke-width: 0.02; fill: none"))

    # Draw filled / unfilled circles
    for x in frange(XMIN, XMAX+CELL_SIZE, CELL_SIZE):
        for y in frange(YMIN, YMAX+CELL_SIZE, CELL_SIZE):
            is_solid = f(x, y) > 0
            fill_color = ("black" if is_solid else "white")
            file.write(element("circle", cx=x, cy=y, r=0.05,
                               style="stroke: black; stroke-width: 0.02; fill: " + fill_color))
    # Draw edges
    for edge in edges:
        file.write(element("line", x1=edge.v1.x, y1=edge.v1.y, x2=edge.v2.x, y2=edge.v2.y,
                           style='stroke:rgb(255,0,0);stroke-width:0.04'))

    # Draw vertices
    r = 0.05
    for v in [v for edge in edges for v in (edge.v1, edge.v2) ]:
        file.write(element("rect", x=(v.x-r), y=(v.y-r), width=2*r, height=2*r,
                           style='fill: red'))

    file.write("</g>\n")
    file.write("</svg>\n")