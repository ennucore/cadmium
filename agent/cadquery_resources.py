CHEATSHEET = """
# CadQuery Cheatsheet

## 3D Construction
- box(length, width, height)
- sphere(radius)
- cylinder(height, radius)
- text(txt, fontsize, distance)
- extrude(until)
- revolve(angleDegrees)
- loft(ruled)
- sweep(path, isFrenet, transitionMode)
- cutBlind(until)
- cutThruAll()
- hole(diameter, depth)
- shell(thickness)
- fillet(radius)
- chamfer(length)
- union(shape)
- cut(shape)
- intersect(shape)

## 2D Construction
- rect(xLen, yLen)
- circle(radius)
- ellipse(x_radius, y_radius)
- center(x, y)
- moveTo(x, y)
- move(xDist, yDist)
- lineTo(x, y)
- line(xDist, yDist)
- polarLine(distance, angle)
- vLine(distance)
- hLine(distance)
- polyline(listOfXYTuple)

## Sketching
- rect(w, h)
- circle(r)
- ellipse(a1, a2)
- trapezoid(w, h, a1)
- regularPolygon(r, n)
- polygon(pts)
- fillet(d)
- chamfer(d)
- finalize()

## Export
- shape.val().exportStl(path)

## Selector String Modifiers
- | (Parallel to)
- # (Perpendicular to)
- +/- (Pos/Neg direction)
- \> (Max)
- < (Min)
- % (Curve/surface type)

## Selector Methods
- faces(selector)
- edges(selector)
- vertices(selector)
- solids(selector)
- shells(selector)

## Workplane Positioning
- translate(Vector(x, y, z))
- rotateAboutCenter(Vector(x, y, z), angleDegrees)
- rotate(Vector(x, y, z), Vector(x, 
"""

EXAMPLES = """
# Lego_Brick.py

# This script can create any regular rectangular Lego(TM) Brick
import cadquery as cq

#####
# Inputs
######
lbumps = 1  # number of bumps long
wbumps = 1  # number of bumps wide
thin = True  # True for thin, False for thick

#
# Lego Brick Constants-- these make a lego brick a lego :)
#
pitch = 8.0
clearance = 0.1
bumpDiam = 4.8
bumpHeight = 1.8
if thin:
    height = 3.2
else:
    height = 9.6

t = (pitch - (2 * clearance) - bumpDiam) / 2.0
postDiam = pitch - t  # works out to 6.5
total_length = lbumps * pitch - 2.0 * clearance
total_width = wbumps * pitch - 2.0 * clearance

# make the base
s = cq.Workplane("XY").box(total_length, total_width, height)

# shell inwards not outwards
s = s.faces("<Z").shell(-1.0 * t)

# make the bumps on the top
s = (
    s.faces(">Z")
    .workplane()
    .rarray(pitch, pitch, lbumps, wbumps, True)
    .circle(bumpDiam / 2.0)
    .extrude(bumpHeight)
)

# add posts on the bottom. posts are different diameter depending on geometry
# solid studs for 1 bump, tubes for multiple, none for 1x1
tmp = s.faces("<Z").workplane(invert=True)

if lbumps > 1 and wbumps > 1:
    tmp = (
        tmp.rarray(pitch, pitch, lbumps - 1, wbumps - 1, center=True)
        .circle(postDiam / 2.0)
        .circle(bumpDiam / 2.0)
        .extrude(height - t)
    )
elif lbumps > 1:
    tmp = (
        tmp.rarray(pitch, pitch, lbumps - 1, 1, center=True)
        .circle(t)
        .extrude(height - t)
    )
elif wbumps > 1:
    tmp = (
        tmp.rarray(pitch, pitch, 1, wbumps - 1, center=True)
        .circle(t)
        .extrude(height - t)
    )
else:
    tmp = s

# Case_Seam_Lip.py

import cadquery as cq
from cadquery.selectors import AreaNthSelector

case_bottom = (
    cq.Workplane("XY")
    .rect(20, 20)
    .extrude(10)  # solid 20x20x10 box
    .edges("|Z or <Z")
    .fillet(2)  # rounding all edges except 4 edges of the top face
    .faces(">Z")
    .shell(2)  # shell of thickness 2 with top face open
    .faces(">Z")
    .wires(AreaNthSelector(-1))  # selecting top outer wire
    .toPending()
    .workplane()
    .offset2D(-1)  # creating centerline wire of case seam face
    .extrude(1)  # covering the sell with temporary "lid"
    .faces(">Z[-2]")
    .wires(AreaNthSelector(0))  # selecting case crossection wire
    .toPending()
    .workplane()
    .cutBlind(2)  # cutting through the "lid" leaving a lip on case seam surface
)

# similar process repeated for the top part
# but instead of "growing" an inner lip
# material is removed inside case seam centerline
# to create an outer lip
case_top = (
    cq.Workplane("XY")
    .move(25)
    .rect(20, 20)
    .extrude(5)
    .edges("|Z or >Z")
    .fillet(2)
    .faces("<Z")
    .shell(2)
    .faces("<Z")
    .wires(AreaNthSelector(-1))
    .toPending()
    .workplane()
    .offset2D(-1)
    .cutBlind(-1)
)

# Swept_Helix.py

import cadquery as cq

r = 0.5  # Radius of the helix
p = 0.4  # Pitch of the helix - vertical distance between loops
h = 2.4  # Height of the helix - total height

# Helix
wire = cq.Wire.makeHelix(pitch=p, height=h, radius=r)
helix = cq.Workplane(obj=wire)

# Final result: A 2D shape swept along a helix.
result = (
    cq.Workplane("XZ")  # helix is moving up the Z axis
    .center(r, 0)  # offset isosceles trapezoid
    .polyline(((-0.15, 0.1), (0.0, 0.05), (0, 0.35), (-0.15, 0.3)))
    .close()  # make edges a wire
    .sweep(helix, isFrenet=True)  # Frenet keeps orientation as expected
)

# Sweep_With_Multiple_Sections.py

import cadquery as cq

# X axis line length 20.0
path = cq.Workplane("XZ").moveTo(-10, 0).lineTo(10, 0)

# Sweep a circle from diameter 2.0 to diameter 1.0 to diameter 2.0 along X axis length 10.0 + 10.0
defaultSweep = (
    cq.Workplane("YZ")
    .workplane(offset=-10.0)
    .circle(2.0)
    .workplane(offset=10.0)
    .circle(1.0)
    .workplane(offset=10.0)
    .circle(2.0)
    .sweep(path, multisection=True)
)

# We can sweep through different shapes
recttocircleSweep = (
    cq.Workplane("YZ")
    .workplane(offset=-10.0)
    .rect(2.0, 2.0)
    .workplane(offset=8.0)
    .circle(1.0)
    .workplane(offset=4.0)
    .circle(1.0)
    .workplane(offset=8.0)
    .rect(2.0, 2.0)
    .sweep(path, multisection=True)
)

circletorectSweep = (
    cq.Workplane("YZ")
    .workplane(offset=-10.0)
    .circle(1.0)
    .workplane(offset=7.0)
    .rect(2.0, 2.0)
    .workplane(offset=6.0)
    .rect(2.0, 2.0)
    .workplane(offset=7.0)
    .circle(1.0)
    .sweep(path, multisection=True)
)


# Placement of the Shape is important otherwise could produce unexpected shape
specialSweep = (
    cq.Workplane("YZ")
    .circle(1.0)
    .workplane(offset=10.0)
    .rect(2.0, 2.0)
    .sweep(path, multisection=True)
)

# Switch to an arc for the path : line l=5.0 then half circle r=4.0 then line l=5.0
path = (
    cq.Workplane("XZ")
    .moveTo(-5, 4)
    .lineTo(0, 4)
    .threePointArc((4, 0), (0, -4))
    .lineTo(-5, -4)
)

# Placement of different shapes should follow the path
# cylinder r=1.5 along first line
# then sweep along arc from r=1.5 to r=1.0
# then cylinder r=1.0 along last line
arcSweep = (
    cq.Workplane("YZ")
    .workplane(offset=-5)
    .moveTo(0, 4)
    .circle(1.5)
    .workplane(offset=5, centerOption="CenterOfMass")
    .circle(1.5)
    .moveTo(0, -8)
    .circle(1.0)
    .workplane(offset=-5, centerOption="CenterOfMass")
    .circle(1.0)
    .sweep(path, multisection=True)
)

# Translate the resulting solids so that they do not overlap and display them left to right

# Sweep.py

import cadquery as cq

# Points we will use to create spline and polyline paths to sweep over
pts = [(0, 1), (1, 2), (2, 4)]

# Spline path generated from our list of points (tuples)
path = cq.Workplane("XZ").spline(pts)

# Sweep a circle with a diameter of 1.0 units along the spline path we just created
defaultSweep = cq.Workplane("XY").circle(1.0).sweep(path)

# Sweep defaults to making a solid and not generating a Frenet solid. Setting Frenet to True helps prevent creep in
# the orientation of the profile as it is being swept
frenetShell = cq.Workplane("XY").circle(1.0).sweep(path, makeSolid=True, isFrenet=True)

# We can sweep shapes other than circles
defaultRect = cq.Workplane("XY").rect(1.0, 1.0).sweep(path)

# Switch to a polyline path, but have it use the same points as the spline
path = cq.Workplane("XZ").polyline(pts, includeCurrent=True)

# Using a polyline path leads to the resulting solid having segments rather than a single swept outer face
plineSweep = cq.Workplane("XY").circle(1.0).sweep(path)

# Switch to an arc for the path
path = cq.Workplane("XZ").threePointArc((1.0, 1.5), (0.0, 1.0))

# Use a smaller circle section so that the resulting solid looks a little nicer
arcSweep = cq.Workplane("XY").circle(0.5).sweep(path)

# Translate the resulting solids so that they do not overlap and display them left to right
show_object(defaultSweep)
show_object(frenetShell.translate((5, 0, 0)))
show_object(defaultRect.translate((10, 0, 0)))
show_object(plineSweep)
show_object(arcSweep.translate((20, 0, 0)))

# Revolution.py

import cadquery as cq

# The dimensions of the model. These can be modified rather than changing the
# shape's code directly.
rectangle_width = 10.0
rectangle_length = 10.0
angle_degrees = 360.0

# Revolve a cylinder from a rectangle
# Switch comments around in this section to try the revolve operation with different parameters
result = cq.Workplane("XY").rect(rectangle_width, rectangle_length, False).revolve()
# result = cq.Workplane("XY").rect(rectangle_width, rectangle_length, False).revolve(angle_degrees)
# result = cq.Workplane("XY").rect(rectangle_width, rectangle_length).revolve(angle_degrees,(-5,-5))
# result = cq.Workplane("XY").rect(rectangle_width, rectangle_length).revolve(angle_degrees,(-5, -5),(-5, 5))
# result = cq.Workplane("XY").rect(rectangle_width, rectangle_length).revolve(angle_degrees,(-5,-5),(-5,5), False)

# Revolve a donut with square walls
# result = cq.Workplane("XY").rect(rectangle_width, rectangle_length, True).revolve(angle_degrees, (20, 0), (20, 10))

# Splitting_an_Object.py

import cadquery as cq

# Create a simple block with a hole through it that we can split.
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the X and Y origins to define the workplane, meaning that the
#     positive Z direction is "up", and the negative Z direction is "down".
# 2.  Creates a plain box to base future geometry on with the box() function.
# 3.  Selects the top-most face of the box and establishes a workplane on it
#     that new geometry can be built on.
# 4.  Draws a 2D circle on the new workplane and then uses it to cut a hole
#     all the way through the box.
c = cq.Workplane("XY").box(1, 1, 1).faces(">Z").workplane().circle(0.25).cutThruAll()

# 5.  Selects the face furthest away from the origin in the +Y axis direction.
# 6.  Creates an offset workplane that is set in the center of the object.
# 6a. One possible improvement to this script would be to make the dimensions
#     of the box variables, and then divide the Y-axis dimension by 2.0 and
#     use that to create the offset workplane.
# 7.  Uses the embedded workplane to split the object, keeping only the "top"
#     portion.
result = c.faces(">Y").workplane(-0.5).split(keepTop=True)

# Rounding_Corners_with_Fillets.py

import cadquery as cq

# Create a plate with 4 rounded corners in the Z-axis.
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the X and Y origins to define the workplane, meaning that the
#     positive Z direction is "up", and the negative Z direction is "down".
# 2.  Creates a plain box to base future geometry on with the box() function.
# 3.  Selects all edges that are parallel to the Z axis.
# 4.  Creates fillets on each of the selected edges with the specified radius.
result = cq.Workplane("XY").box(3, 3, 0.5).edges("|Z").fillet(0.125)

# Counter_Sunk_Holes.py

import cadquery as cq

# Create a plate with 4 counter-sunk holes in it.
# 1.  Establishes a workplane using an XY object instead of a named plane.
# 2.  Creates a plain box to base future geometry on with the box() function.
# 3.  Selects the top-most face of the box and established a workplane on that.
# 4.  Draws a for-construction rectangle on the workplane which only exists for
#     placing other geometry.
# 5.  Selects the corner vertices of the rectangle and places a counter-sink
#     hole, using each vertex as the center of a hole using the cskHole()
#     function.
# 5a. When the depth of the counter-sink hole is set to None, the hole will be
#     cut through.
result = (
    cq.Workplane(cq.Plane.XY())
    .box(4, 2, 0.5)
    .faces(">Z")
    .workplane()
    .rect(3.5, 1.5, forConstruction=True)
    .vertices()
    .cskHole(0.125, 0.25, 82.0, depth=None)
)

# Making_Lofts.py

import cadquery as cq

# Create a lofted section between a rectangle and a circular section.
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 2.  Creates a plain box to base future geometry on with the box() function.
# 3.  Selects the top-most Z face of the box.
# 4.  Draws a 2D circle at the center of the the top-most face of the box.
# 5.  Creates a workplane 3 mm above the face the circle was drawn on.
# 6.  Draws a 2D circle on the new, offset workplane.
# 7.  Creates a loft between the circle and the rectangle.
result = (
    cq.Workplane("front")
    .box(4.0, 4.0, 0.25)
    .faces(">Z")
    .circle(1.5)
    .workplane(offset=3.0)
    .rect(0.75, 0.5)
    .loft(combine=True)
)

# Shelling_to_Create_Thin_Feature.py

import cadquery as cq

# Create a hollow box that's open on both ends with a thin wall.
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 2.  Creates a plain box to base future geometry on with the box() function.
# 3.  Selects faces with normal in +z direction.
# 4.  Create a shell by cutting out the top-most Z face.
result = cq.Workplane("front").box(2, 2, 2).faces("+Z").shell(0.05)

# Using_Construction_Geometry.py

import cadquery as cq

# Create a block with holes in each corner of a rectangle on that workplane.
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 2.  Creates a plain box to base future geometry on with the box() function.
# 3.  Selects the top-most Z face of the box.
# 4.  Creates a new workplane to build new geometry on.
# 5.  Creates a for-construction rectangle that only exists to use for placing
#     other geometry.
# 6.  Selects the vertices of the for-construction rectangle.
# 7.  Places holes at the center of each selected vertex.
result = (
    cq.Workplane("front")
    .box(2, 2, 0.5)
    .faces(">Z")
    .workplane()
    .rect(1.5, 1.5, forConstruction=True)
    .vertices()
    .hole(0.125)
)

# Rotated_Workplanes.py

import cadquery as cq

# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 2.  Creates a plain box to base future geometry on with the box() function.
# 3.  Selects the top-most Z face of the box.
# 4.  Creates a new workplane and then moves and rotates it with the
#     transformed function.
# 5.  Creates a for-construction rectangle that only exists to use for placing
#     other geometry.
# 6.  Selects the vertices of the for-construction rectangle.
# 7.  Places holes at the center of each selected vertex.
# 7a. Since the workplane is rotated, this results in angled holes in the face.
result = (
    cq.Workplane("front")
    .box(4.0, 4.0, 0.25)
    .faces(">Z")
    .workplane()
    .transformed(offset=(0, -1.5, 1.0), rotate=(60, 0, 0))
    .rect(1.5, 1.5, forConstruction=True)
    .vertices()
    .hole(0.25)
)

# Offset_Workplanes.py

import cadquery as cq

# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 2.  Creates a 3D box that will have geometry based off it later.
result = cq.Workplane("front").box(3, 2, 0.5)

# 3.  The lowest face in the X direction is selected with the <X selector.
# 4. A new workplane is created
# 4a.The workplane is offset from the object surface so that it is not touching
#    the original box.
result = result.faces("<X").workplane(offset=0.75)

# 5. Creates a thin disc on the offset workplane that is floating near the box.
result = result.circle(1.0).extrude(0.5)

# Locating_a_Workplane_on_a_Vertex.py

import cadquery as cq

# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 2.  Creates a 3D box that will have a hole placed in it later.
result = cq.Workplane("front").box(3, 2, 0.5)

# 3.  Select the lower left vertex and make a workplane.
# 3a. The top-most Z face is selected using the >Z selector.
# 3b. The lower-left vertex of the faces is selected with the <XY selector.
# 3c. A new workplane is created on the vertex to build future geometry on.
result = result.faces(">Z").vertices("<XY").workplane(centerOption="CenterOfMass")

# 4.  A circle is drawn with the selected vertex as its center.
# 4a. The circle is cut down through the box to cut the corner out.
result = result.circle(1.0).cutThruAll()

# Creating_Workplanes_on_Faces.py

import cadquery as cq

# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 2.  Creates a 3D box that will have a hole placed in it later.
result = cq.Workplane("front").box(2, 3, 0.5)

# 3.  Find the top-most face with the >Z max selector.
# 3a. Establish a new workplane to build geometry on.
# 3b.  Create a hole down into the box.
result = result.faces(">Z").workplane().hole(0.5)

# Mirroring_Symmetric_Geometry.py

import cadquery as cq

# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 2.  A horizontal line is drawn on the workplane with the hLine function.
# 2a. 1.0 is the distance, not coordinate. hLineTo allows using xCoordinate
#     not distance.
r = cq.Workplane("front").hLine(1.0)

# 3.  Draw a series of vertical and horizontal lines with the vLine and hLine
#     functions.
r = r.vLine(0.5).hLine(-0.25).vLine(-0.25).hLineTo(0.0)

# 4.  Mirror the geometry about the Y axis and extrude it into a 3D object.
result = r.mirrorY().extrude(0.25)

# Defining_an_Edge_with_a_Spline.py

import cadquery as cq

# 1.  Establishes a workplane to create the spline on to extrude.
# 1a. Uses the X and Y origins to define the workplane, meaning that the
# positive Z direction is "up", and the negative Z direction is "down".
s = cq.Workplane("XY")

# The points that the spline will pass through
sPnts = [
    (2.75, 1.5),
    (2.5, 1.75),
    (2.0, 1.5),
    (1.5, 1.0),
    (1.0, 1.25),
    (0.5, 1.0),
    (0, 1.0),
]

# 2.  Generate our plate with the spline feature and make sure it is a
#     closed entity
r = s.lineTo(3.0, 0).lineTo(3.0, 1.0).spline(sPnts, includeCurrent=True).close()

# 3.  Extrude to turn the wire into a plate
result = r.extrude(0.5)

# Polylines.py

import cadquery as cq

# These can be modified rather than hardcoding values for each dimension.
# Define up our Length, Height, Width, and thickness of the beam
(L, H, W, t) = (100.0, 20.0, 20.0, 1.0)

# Define the points that the polyline will be drawn to/thru
pts = [
    (0, H / 2.0),
    (W / 2.0, H / 2.0),
    (W / 2.0, (H / 2.0 - t)),
    (t / 2.0, (H / 2.0 - t)),
    (t / 2.0, (t - H / 2.0)),
    (W / 2.0, (t - H / 2.0)),
    (W / 2.0, H / -2.0),
    (0, H / -2.0),
]

# We generate half of the I-beam outline and then mirror it to create the full
# I-beam.
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 2.  moveTo() is used to move the first point from the origin (0, 0) to
#     (0, 10.0), with 10.0 being half the height (H/2.0). If this is not done
#     the first line will start from the origin, creating an extra segment that
#     will cause the extrude to have an invalid shape.
# 3.  The polyline function takes a list of points and generates the lines
#     through all the points at once.
# 3.  Only half of the I-beam profile has been drawn so far. That half is
#     mirrored around the Y-axis to create the complete I-beam profile.
# 4.  The I-beam profile is extruded to the final length of the beam.
result = cq.Workplane("front").polyline(pts).mirrorY().extrude(L)

# Polygon_Creation.py

import cadquery as cq

# These can be modified rather than hardcoding values for each dimension.
width = 3.0  # The width of the plate
height = 4.0  # The height of the plate
thickness = 0.25  # The thickness of the plate
polygon_sides = 6  # The number of sides that the polygonal holes should have
polygon_dia = 1.0  # The diameter of the circle enclosing the polygon points

# Create a plate with two polygons cut through it
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 2.  A 3D box is created in one box() operation to represent the plate.
# 2a. The box is centered around the origin, which creates a result that may
#     be unituitive when the polygon cuts are made.
# 3.  2 points are pushed onto the stack and will be used as centers for the
#     polygonal holes.
# 4.  The two polygons are created, on for each point, with one call to
#     polygon() using the number of sides and the circle that bounds the
#     polygon.
# 5.  The polygons are cut thru all objects that are in the line of extrusion.
# 5a. A face was not selected, and so the polygons are created on the
#     workplane. Since the box was centered around the origin, the polygons end
#     up being in the center of the box. This makes them cut from the center to
#     the outside along the normal (positive direction).
# 6.  The polygons are cut through all objects, starting at the center of the
#     box/plate and going "downward" (opposite of normal) direction. Functions
#     like cutBlind() assume a positive cut direction, but cutThruAll() assumes
#     instead that the cut is made from a max direction and cuts downward from
#     that max through all objects.
result = (
    cq.Workplane("front")
    .box(width, height, thickness)
    .pushPoints([(0, 0.75), (0, -0.75)])
    .polygon(polygon_sides, polygon_dia)
    .cutThruAll()
)

# Using_Point_Lists.py

import cadquery as cq

# These can be modified rather than hardcoding values for each dimension.
plate_radius = 2.0  # The radius of the plate that will be extruded
hole_pattern_radius = 0.25  # Radius of circle where the holes will be placed
thickness = 0.125  # The thickness of the plate that will be extruded

# Make a plate with 4 holes in it at various points in a polar arrangement from
# the center of the workplane.
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 2.  A 2D circle is drawn that will become though outer profile of the plate.
r = cq.Workplane("front").circle(plate_radius)

# 3. Push 4 points on the stack that will be used as the center points of the
#    holes.
r = r.pushPoints([(1.5, 0), (0, 1.5), (-1.5, 0), (0, -1.5)])

# 4. This circle() call will operate on all four points, putting a circle at
#    each one.
r = r.circle(hole_pattern_radius)

# 5.  All 2D geometry is extruded to the specified thickness of the plate.
# 5a. The small hole circles are enclosed in the outer circle of the plate and
#     so it is assumed that we want them to be cut out of the plate.  A
#     separate cut operation is not needed.
result = r.extrude(thickness)

# Moving_the_Current_Working_Point.py

import cadquery as cq

# These can be modified rather than hardcoding values for each dimension.
circle_radius = 3.0  # The outside radius of the plate
thickness = 0.25  # The thickness of the plate

# Make a plate with two cutouts in it by moving the workplane center point
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 1b. The initial workplane center point is the center of the circle, at (0,0).
# 2.  A circle is created at the center of the workplane
# 2a. Notice that circle() takes a radius and not a diameter
result = cq.Workplane("front").circle(circle_radius)

# 3.  The work center is movide to (1.5, 0.0) by calling center().
# 3a. The new center is specified relative to the previous center,not
#     relative to global coordinates.
# 4.  A 0.5mm x 0.5mm 2D square is drawn inside the circle.
# 4a. The plate has not been extruded yet, only 2D geometry is being created.
result = result.center(1.5, 0.0).rect(0.5, 0.5)

# 5.  The work center is moved again, this time to (-1.5, 1.5).
# 6.  A 2D circle is created at that new center with a radius of 0.25mm.
result = result.center(-1.5, 1.5).circle(0.25)

# 7.  All 2D geometry is extruded to the specified thickness of the plate.
# 7a. The small circle and the square are enclosed in the outer circle of the
#      plate and so it is assumed that we want them to be cut out of the plate.
#      A separate cut operation is not needed.
result = result.extrude(thickness)

# Extruded_Lines_and_Arcs.py

import cadquery as cq

# These can be modified rather than hardcoding values for each dimension.
width = 2.0  # Overall width of the plate
thickness = 0.25  # Thickness of the plate

# Extrude a plate outline made of lines and an arc
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 2.  Draws a line from the origin to an X position of the plate's width.
# 2a. The starting point of a 2D drawing like this will be at the center of the
#     workplane (0, 0) unless the moveTo() function moves the starting point.
# 3.  A line is drawn from the last position straight up in the Y direction
#     1.0 millimeters.
# 4.  An arc is drawn from the last point, through point (1.0, 1.5) which is
#     half-way back to the origin in the X direction and 0.5 mm above where
#     the last line ended at. The arc then ends at (0.0, 1.0), which is 1.0 mm
#     above (in the Y direction) where our first line started from.
# 5.  An arc is drawn from the last point that ends on (-0.5, 1.0), the sag of
#     the curve 0.2 determines that the curve is concave with the midpoint 0.1 mm
#     from the arc baseline. If the sag was -0.2 the arc would be convex.
#     This convention is valid when the profile is drawn counterclockwise.
#     The reverse is true if the profile is drawn clockwise.
#     Clockwise:        +sag => convex,  -sag => concave
#     Counterclockwise: +sag => concave, -sag => convex
# 6.  An arc is drawn from the last point that ends on (-0.7, -0.2), the arc is
#     determined by the radius of -1.5 mm.
#     Clockwise:        +radius => convex,  -radius => concave
#     Counterclockwise: +radius => concave, -radius => convex
# 7.  close() is called to automatically draw the last line for us and close
#     the sketch so that it can be extruded.
# 7a. Without the close(), the 2D sketch will be left open and the extrude
#     operation will provide unpredictable results.
# 8.  The 2D sketch is extruded into a solid object of the specified thickness.
result = (
    cq.Workplane("front")
    .lineTo(width, 0)
    .lineTo(width, 1.0)
    .threePointArc((1.0, 1.5), (0.0, 1.0))
    .sagittaArc((-0.5, 1.0), 0.2)
    .radiusArc((-0.7, -0.2), -1.5)
    .close()
    .extrude(thickness)
)

# Extruded_Cylindrical_Plate.py

import cadquery as cq

# These can be modified rather than hardcoding values for each dimension.
circle_radius = 50.0  # Radius of the plate
thickness = 13.0  # Thickness of the plate
rectangle_width = 13.0  # Width of rectangular hole in cylindrical plate
rectangle_length = 19.0  # Length of rectangular hole in cylindrical plate

# Extrude a cylindrical plate with a rectangular hole in the middle of it.
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 2.  The 2D geometry for the outer circle is created at the same time as the
#     rectangle that will create the hole in the center.
# 2a. The circle and the rectangle will be automatically centered on the
#     workplane.
# 2b. Unlike some other functions like the hole(), circle() takes
#     a radius and not a diameter.
# 3.  The circle and rectangle are extruded together, creating a cylindrical
#     plate with a rectangular hole in the center.
# 3a. circle() and rect() could be changed to any other shape to completely
#     change the resulting plate and/or the hole in it.
result = (
    cq.Workplane("front")
    .circle(circle_radius)
    .rect(rectangle_width, rectangle_length)
    .extrude(thickness)
)

# Pillow_Block_With_Counterbored_Holes.py

import cadquery as cq

# These can be modified rather than hardcoding values for each dimension.
length = 80.0  # Length of the block
width = 100.0  # Width of the block
thickness = 10.0  # Thickness of the block
center_hole_dia = 22.0  # Diameter of center hole in block
cbore_hole_diameter = 2.4  # Bolt shank/threads clearance hole diameter
cbore_inset = 12.0  # How far from the edge the cbored holes are set
cbore_diameter = 4.4  # Bolt head pocket hole diameter
cbore_depth = 2.1  # Bolt head pocket hole depth

# Create a 3D block based on the dimensions above and add a 22mm center hold
# and 4 counterbored holes for bolts
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the X and Y origins to define the workplane, meaning that the
#     positive Z direction is "up", and the negative Z direction is "down".
# 2.  The highest(max) Z face is selected and a new workplane is created on it.
# 3.  The new workplane is used to drill a hole through the block.
# 3a. The hole is automatically centered in the workplane.
# 4.  The highest(max) Z face is selected and a new workplane is created on it.
# 5.  A for-construction rectangle is created on the workplane based on the
#     block's overall dimensions.
# 5a. For-construction objects are used only to place other geometry, they
#     do not show up in the final displayed geometry.
# 6.  The vertices of the rectangle (corners) are selected, and a counter-bored
#     hole is placed at each of the vertices (all 4 of them at once).
result = (
    cq.Workplane("XY")
    .box(length, width, thickness)
    .faces(">Z")
    .workplane()
    .hole(center_hole_dia)
    .faces(">Z")
    .workplane()
    .rect(length - cbore_inset, width - cbore_inset, forConstruction=True)
    .vertices()
    .cboreHole(cbore_hole_diameter, cbore_diameter, cbore_depth)
    .edges("|Z")
    .fillet(2.0)
)

# Displays the result of this script
show_object(result)

# Block_With_Bored_Center_Hole.py

import cadquery as cq

# These can be modified rather than hardcoding values for each dimension.
length = 80.0  # Length of the block
height = 60.0  # Height of the block
thickness = 10.0  # Thickness of the block
center_hole_dia = 22.0  # Diameter of center hole in block

# Create a block based on the dimensions above and add a 22mm center hole.
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the X and Y origins to define the workplane, meaning that the
# positive Z direction is "up", and the negative Z direction is "down".
# 2.  The highest (max) Z face is selected and a new workplane is created on it.
# 3.  The new workplane is used to drill a hole through the block.
# 3a. The hole is automatically centered in the workplane.
result = (
    cq.Workplane("XY")
    .box(length, height, thickness)
    .faces(">Z")
    .workplane()
    .hole(center_hole_dia)
)

# Displays the result of this script
show_object(result)

# Simple_Block.py

import cadquery as cq

# These can be modified rather than hardcoding values for each dimension.
length = 80.0  # Length of the block
height = 60.0  # Height of the block
thickness = 10.0  # Thickness of the block

# Create a 3D block based on the dimension variables above.
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the X and Y origins to define the workplane, meaning that the
# positive Z direction is "up", and the negative Z direction is "down".
result = cq.Workplane("XY").box(length, height, thickness)
"""

LITTLE_GUIDE = """
offset by 10 mm from the edge

3. Create the CadQuery code:

```python
import cadquery as cq

# Dimensions
can_diameter = 66
can_height = 122
can_wall_thickness = 0.5
pull_tab_length = 20
pull_tab_width = 10
pull_tab_thickness = 1
pull_tab_offset = 10

# Create the can body
can_body = cq.Workplane("XY").circle(can_diameter / 2).extrude(can_height)

# Create the can top and bottom
can_top = cq.Workplane("XY").workplane(offset=can_height).circle(can_diameter / 2).extrude(can_wall_thickness)
can_bottom = cq.Workplane("XY").circle(can_diameter / 2).extrude(can_wall_thickness)

# Create the pull tab
pull_tab = (
    cq.Workplane("XY")
    .workplane(offset=can_height + can_wall_thickness)
    .center(can_diameter / 2 - pull_tab_offset, 0)
    .rect(pull_tab_length, pull_tab_width)
    .extrude(pull_tab_thickness)
)

# Combine the can parts
can = can_body.union(can_top).union(can_bottom).union(pull_tab)

# Hollow out the can
can = can.faces(">Z").shell(-can_wall_thickness)
```

Example 3: A simple house with a pitched roof

1. Break down the object:
   - House body: A rectangular cuboid
   - Roof: Two sloped faces forming a triangular prism

2. Identify dimensions and relationships:
   - House body dimensions: length = 10000 mm, width = 8000 mm, height = 6000 mm
   - Roof dimensions: same length and width as the house body, height = 3000 mm
   - Roof slope: 30 degrees

3. Create the CadQuery code:

```python
import cadquery as cq
import math

# Dimensions
house_length = 10000
house_width = 8000
house_height = 6000
roof_height = 3000
roof_slope = math.radians(30)

# Create the house body
house_body = cq.Workplane("XY").box(house_length, house_width, house_height)

# Create the roof
roof = (
    cq.Workplane("XY")
    .workplane(offset=house_height)
    .polyline([(0, 0), (house_length / 2, roof_height), (house_length, 0), (0, 0)])
    .close()
    .extrude(house_width)
)

# Combine the house body and roof
house = house_body.union(roof)
```

These examples demonstrate how to break down an object into its constituent parts, identify their dimensions and relationships, and then use CadQuery methods to create the corresponding 3D model. By following this process, LLM chatbots can effectively translate casual text descriptions into accurate and coherent CadQuery code.

Reasoning About Geometry and Angles
-----------------------------------

When working with CadQuery, it's essential to reason step-by-step about geometry and angles, especially for LLMs that may not be proficient at visualizing or performing mathematical calculations. Here are some tips to help LLMs better understand and work with geometric concepts:

1. Break down complex shapes into simpler components: Identify the basic shapes that make up the object, such as rectangles, circles, triangles, or cylinders. This makes it easier to understand the overall structure and dimensions of the object.

2. Use cardinal directions and relative positions: Describe the position and orientation of shapes using cardinal directions (e.g., north, south, east, west) and relative positions (e.g., above, below, left, right). This helps establish a clear understanding of the spatial relationships between components.

3. Specify angles using degrees or radians: When describing angles, always specify whether the angle is in degrees or radians. This helps avoid confusion and ensures that the correct values are used in the CadQuery code.

4. Use trigonometric functions for angle calculations: If angle calculations are required, use trigonometric functions like sine, cosine, and tangent to determine the necessary dimensions. Provide step-by-step explanations of the calculations to help LLMs understand the process.

5. Employ symmetry and repetition: Identify patterns of symmetry and repetition in the object, as this can simplify the modeling process. For example, if an object has multiple identical components, you can create one component and then use transformations (e.g., translations, rotations) to position the copies.

6. Utilize workplanes and local coordinate systems: Use workplanes to establish local coordinate systems that make it easier to reason about the position and orientation of shapes. This is particularly helpful when creating complex objects with multiple components.

7. Sketch 2D profiles before extruding: When creating 3D shapes, it often helps to sketch the 2D profile first and then extrude it. This allows you to focus on the cross-sectional shape and dimensions before considering the depth or height of the object.

By following these tips and providing clear, step-by-step explanations, LLMs can more effectively reason about geometry and angles when working with CadQuery.

Using Constraints
-----------------

CadQuery allows you to create parametric models by using constraints. Constraints define the relationships between different parts of a model, making it easier to modify and update the design. Here are five examples that demonstrate the use of constraints in CadQuery:

Example 1: A rectangle with a constrained aspect ratio

```python
import cadquery as cq

# Dimensions
width = 100
aspect_ratio = 1.5

# Create the rectangle
rectangle = cq.Workplane("XY").rect(width, width * aspect_ratio)
```

In this example, the rectangle's height is constrained to be 1.5 times its width. By modifying the `width` variable, the height will automatically update to maintain the aspect ratio.

Example 2: A cylinder with a constrained diameter-to-height ratio

```python
import cadquery as cq

# Dimensions
diameter = 50
diameter_to_height_ratio = 0.8

# Create the cylinder
cylinder = cq.Workplane("XY").circle(diameter / 2).extrude(diameter * diameter_to_height_ratio)
```

Here, the cylinder's height is constrained to be 0.8 times its diameter. Changing the `diameter` variable will automatically update the height to maintain the ratio.

Example 3: A box with a constrained wall thickness

```python
import cadquery as cq

# Dimensions
length = 100
width = 80
height = 60
wall_thickness = 5

# Create the outer box
outer_box = cq.Workplane("XY").box(length, width, height)

# Create the inner box
inner_box = cq.Workplane("XY").box(
    length - 2 * wall_thickness,
    width - 2 * wall_thickness,
    height - wall_thickness
)

# Subtract the inner box from the outer box
box_with_walls = outer_box.cut(inner_box)
```

In this example, the wall thickness of the box is constrained to be a constant value. The inner box dimensions are calculated based on the outer box dimensions and the wall thickness, ensuring that the walls remain a consistent thickness even if the outer dimensions are modified.

Example 4: A plate with holes constrained to be a certain distance from the edges

```python
import cadquery as cq

# Dimensions
plate_length = 200
plate_width = 150
plate_thickness = 10
hole_diameter = 10
edge_distance = 20

# Create the plate
plate = cq.Workplane("XY").box(plate_length, plate_width, plate_thickness)

# Create the holes
holes = (
    cq.Workplane("XY")
    .workplane(offset=plate_thickness / 2)
    .rect(
        plate_length - 2 * edge_distance,
        plate_width - 2 * edge_distance,
        forConstruction=True
    )
    .vertices()
    .hole(hole_diameter)
)

# Subtract the holes from the plate
plate_with_holes = plate.cut(holes)
```

In this example, the holes are constrained to be a certain distance from the edges of the plate. The hole positions are calculated based on the plate dimensions and the edge distance, ensuring that the holes remain a consistent distance from the edges even if the plate dimensions are modified.

Example 5: A gear with constrained tooth dimensions

```python
import cadquery as cq
import math

# Dimensions
gear_diameter = 100
num_teeth = 20
pressure_angle = math.radians(20)
clearance = 0.1
backlash = 0.1

# Calculate the gear parameters
pitch_diameter = gear_diameter
diametral_pitch = num_teeth / pitch_diameter
addendum = 1 / diametral_pitch
dedendum = 1.25 / diametral_pitch
tooth_thickness = (math.pi / (2 * diametral_pitch)) - (backlash / 2)
root_diameter = pitch_diameter - 2 * dedendum
base_diameter = pitch_diameter * math.cos(pressure_angle)

# Create the gear profile
gear_profile = (
    cq.Workplane("XY")
    .parametricCurve(
        lambda t: (
            (root_diameter / 2 + addendum * math.sin(t)) * math.cos(t),
            (root_diameter / 2 + addendum * math.sin(t)) * math.sin(t)
        ),
        start=0,
        stop=math.pi / num_teeth,
        N=50
    )
    .rotateAndCopy(360 / num_teeth, num_teeth)
    .close()
)

# Extrude the gear profile
gear = gear_profile.extrude(10)
```

In this example, the gear tooth dimensions are constrained by the gear diameter, number of teeth, pressure angle, clearance, and backlash. The gear profile is generated using a parametric curve based on these constraints, ensuring that the tooth dimensions remain consistent and properly proportioned even if the gear diameter or number of teeth are modified.

These examples demonstrate how constraints can be used in CadQuery to create parametric models that are easier to modify and update. By defining the relationships between different parts of a model, you can ensure that the design remains consistent and properly proportioned even when dimensions are changed.

Modeling a Door and Door Frame
------------------------------

In this example, we'll create a well-proportioned door and door frame using CadQuery. We'll use constraints and accurate placement/rotations to ensure that the door fits properly within the frame and can be easily modified if needed.

```python
import cadquery as cq

# Dimensions
frame_width = 1000
frame_height = 2100
frame_thickness = 100
frame_depth = 150
door_width = frame_width - 2 * frame_thickness
door_height = frame_height - frame_thickness
door_thickness = 50
handle_diameter = 50
handle_offset = 70

# Create the door frame
left_jamb = cq.Workplane("XY").box(frame_thickness, frame_depth, frame_height)
right_jamb = left_jamb.translate((frame_width - frame_thickness, 0, 0))
head_jamb = cq.Workplane("XY").box(frame_width, frame_depth, frame_thickness)
head_jamb = head_jamb.translate((0, 0, frame_height - frame_thickness))
frame = left_jamb.union(right_jamb).union(head_jamb)

# Create the door
door = (
    cq.Workplane("XY")
    .workplane(offset=frame_depth)
    .box(door_width, door_thickness, door_height)
    .translate((frame_thickness, -door_thickness / 2, frame_thickness))
)

# Create the door handle
handle = (
    cq.Workplane("XY")
    .workplane(offset=frame_depth + door_thickness / 2)
    .circle(handle_diameter / 2)
    .extrude(door_thickness / 2)
    .translate((door_width - handle_offset, 0, door_height / 2))
)

# Combine the door and handle
door_with_handle = door.union(handle)

# Create the hinge cylinders
hinge_diameter = 20
hinge_height = 100
top_hinge_position = (frame_thickness / 2, 0, door_height - hinge_height / 2)
middle_hinge_position = (frame_thickness / 2, 0, door_height / 2)
bottom_hinge_position = (frame_thickness / 2, 0, hinge_height / 2)

hinge = cq.Workplane("XY").circle(hinge_diameter / 2).extrude(hinge_height)
top_hinge = hinge.translate(top_hinge_position)
middle_hinge = hinge.translate(middle_hinge_position)
bottom_hinge = hinge.translate(bottom_hinge_position)

hinges = top_hinge.union(middle_hinge).union(bottom_hinge)

# Subtract the hinges from the door and frame
door_with_hinges = door_with_handle.cut(hinges)
frame_with_hinges = frame.cut(hinges)

# Combine the door and frame
door_assembly = frame_with_hinges.union(door_with_hinges)
```

In this example, we start by defining the dimensions of the door and frame components. We then create the frame using three rectangular boxes (left_jamb, right_jamb, and head_jamb) and position them correctly using the `translate()` method.

Next, we create the door by creating a box with the appropriate dimensions and positioning it within the frame using the `translate()` method. We also create a cylindrical door handle and position it on the door using the `translate()` method.

To create the hinges, we define the hinge dimensions and positions, create a cylindrical shape for each hinge, and then position them using the `translate()` method. We then subtract the hinges from both the door and the frame using the `cut()` method.

Finally, we combine the door and frame using the `union()` method to create the complete door assembly.

This example demonstrates how to use well-structured code, constraints, and accurate placement/rotations to create a complex object with multiple parts in CadQuery. By defining the dimensions and positions of each component in relation to the others, we ensure that the door and frame remain properly proportioned and aligned even if the dimensions are modified.

Best Practices
--------------

When working with CadQuery, it's essential to follow best practices to ensure that your code is clean, efficient, and maintainable. Here are some tips:

1. Use meaningful variable and method names that clearly describe their purpose.
2. Break down complex models into smaller, reusable components.
3. Use selectors and chaining to keep your code concise and readable.
4. Avoid hardcoding values; instead, use variables to make your models parametric.
5. Add comments to explain complex or non-obvious parts of your code.
6. Use version control (e.g., Git) to track changes and collaborate with others.

Conclusion
----------

This guide has provided a comprehensive overview of CadQuery, covering its core concepts, terminology, and usage. By following the examples and best practices outlined in this guide, LLM chatbots should be able to generate, understand, and edit CadQuery code effectively.

Remember that practice is key to mastering CadQuery. Experiment with different methods, create your own models, and don't hesitate to consult the official CadQuery documentation for more advanced topics and features.

With this knowledge, LLM chatbots can now provide valuable assistance and guidance to users working with CadQuery, helping them create complex and parametric 3D models with ease.
"""