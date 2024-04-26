from typing import Optional
import vtk


def render(
    filenames: list[str],
    positions: list[tuple[float, float, float]],
    colors: list[tuple[float, float, float]],
    output_path: str,
    prefix: Optional[str] = None,
    short_positions: bool = False,
):
    # Create a rendering window and renderer
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.SetOffScreenRendering(1)
    renWin.AddRenderer(ren)

    for filename, position, color in zip(filenames, positions, colors):
        polydata = loadStl(filename)
        actor = polyDataToActor(polydata, color)
        actor.SetPosition(*position)
        ren.AddActor(actor)

    ren.SetBackground(1.0, 1.0, 1.0)

    renWin.Render()

    camera = ren.GetActiveCamera()
    camera_dist_to_origin = camera.GetDistance() * 1.1
    camera.SetClippingRange(0.1, camera_dist_to_origin * 2)

    positions = [
        ((1, 0, 0), (0, 0, camera_dist_to_origin), "top"),
        ((1, 0, 0), (0, 0, -camera_dist_to_origin), "bottom"),
        ((0, 0, 1), (0, camera_dist_to_origin, 0), "front"),
        ((0, 0, 1), (0, -camera_dist_to_origin, 0), "back"),
        ((0, 0, 1), (camera_dist_to_origin, 0, 0), "right"),
        ((0, 0, 1), (-camera_dist_to_origin, 0, 0), "left"),
    ]
    if short_positions:
        positions = [
            ((1, 0, 0), (0.1 * camera_dist_to_origin, 0.1 * camera_dist_to_origin, camera_dist_to_origin), "top"),
            ((1, 0, 0), (0.1 * camera_dist_to_origin, 0.1 * camera_dist_to_origin, -camera_dist_to_origin), "bottom"),
            ((0, 0, 1), (0.15 * camera_dist_to_origin, camera_dist_to_origin, 0), "front"),
        ((0, 0, 1), (-camera_dist_to_origin, 0, 0), "left"),
        ]

    camera.Zoom(1.1)

    for position in positions:
        (vt_x, vt_y, vt_z), (x, y, z), pos_name = position
        camera.SetPosition(x, y, z)
        camera.SetViewUp(vt_x, vt_y, vt_z)
        renWin.Render()

        windowToImageFilter = vtk.vtkWindowToImageFilter()
        windowToImageFilter.SetInput(renWin)
        windowToImageFilter.Update()

        writer = vtk.vtkJPEGWriter()
        writer.SetFileName(
            f"{output_path}/{prefix + '_' if prefix else ''}{pos_name}.jpg"
        )
        writer.SetInputConnection(windowToImageFilter.GetOutputPort())
        writer.Write()

    # Clean up
    renWin.Finalize()
    ren.RemoveAllViewProps()


def loadStl(fname):
    """Load the given STL file, and return a vtkPolyData object for it."""
    reader = vtk.vtkSTLReader()
    reader.SetFileName(fname)
    reader.Update()
    polydata = reader.GetOutput()
    return polydata


def polyDataToActor(polydata, color=(0.5, 0.5, 1.0)):
    """Wrap the provided vtkPolyData object in a mapper and an actor, returning
    the actor."""
    mapper = vtk.vtkPolyDataMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        mapper.SetInput(polydata)
    else:
        mapper.SetInputData(polydata)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color)
    return actor
