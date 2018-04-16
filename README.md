This is demonstration code to accompany a <a href="http://www.boristhebrave.com/2018/04/15/marching-cubes-tutorial/">series</a> <a href="http://www.boristhebrave.com/2018/04/15/marching-cubes-3d-tutorial/">of</a> <a href="http://www.boristhebrave.com/2018/04/15/dual-contouring-tutorial/">articles</a> on meshing. Please consult those
articles for more details.

It covers how to implement 2d / 3d Marching Cubes and Dual Contouring. 

There's also additional code to nicely render the results, but that is not polished for re-use.
 
# Usage
 
Simply import one of `marching_cubes_2d.marching_cubes_2d`, `marching_cubes_3d.marching_cubes_3d`,
`dual_contour_2d.dual_contour_2d`, `dual_contour_3d.dual_contour_3d`.

Each function takes an evaluation function, `f`, that determines whether a point is inside or outside
by returning a positive or negative number. The Dual Contouring functions take an additional argument, 
`f_normal`, that returns the gradient as a `V2` or `V3` object. You can optionally pass the range of values
to evaluate f over. The cell size is always 1.

The 2d meshing functions return a unordered list of `common.Edge` objects, the 3d ones return a `utils_3d.Mesh` object.

# License

[CC0]([https://wiki.creativecommons.org/wiki/CC0)