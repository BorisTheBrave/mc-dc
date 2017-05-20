"""Stores some global settings, mostly to save on a lot of repetitive arguments.
These are mostly of interest for testing."""


# Both marching cube and dual contouring are adaptive, i.e. they select
# the vertex that best describes the underlying function. But for illustrative purposes
# you can turn this off, and simply select the midpoint vertex.
ADAPTIVE = True

# Bounds to evaluate over
XMIN = -3
XMAX = 3
YMIN = -3
YMAX = 3
ZMIN = -3
ZMAX = 3