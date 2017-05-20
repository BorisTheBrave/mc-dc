This is demonstration code to accompany a series of articles on meshing. Please consult those
articles for more details.

It covers how to implement 2d / 3d Marching Cubes and Dual Contouring. 

There's also additional code to nicely render the results, but that is not polished for re-use.
 
# Usage
 
Simply load one of the 4 modules and use the function side of the same name.

The meshing function takes an evaluation function, f, that determines whether a point is inside or outside
by returning a positive or negative number. The Dual Contouring functions take an additional argument, 
f_normal, that returns the gradient as a V2 or V3 object.

The 2d meshing functions return a unordered list of Edge objects, the 3d ones return a Mesh object.

# License

[CC0]([https://wiki.creativecommons.org/wiki/CC0)