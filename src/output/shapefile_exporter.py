"""
File that contains the class shapefileExporter.
"""
import shapefile


class ShapefileExporter:
    """
    Class in charge of exporting data to shapefile format.
    """

    def __init__(self):
        """
        Constructor of the class
        """
        pass

    def __delete_z_axis(self, list_of_points: list) -> list:
        """
        Delete the third component of a list of points, returning a list only with the first two components of
        each point.

        input: [a.x,a.y,a.z,b.x,b.y,b.z,c.x,...]
        output: [[a.x,a.y],[b.x,b.y],[c.x,...]

        Args:
            list_of_points: List of points to use

        Returns: List with the points without the third component
        """
        new_list = []
        pair_used = []
        for component_ind in range(len(list_of_points)):
            if component_ind % 3 == 0:
                pair_used.append(list_of_points[component_ind])
            elif component_ind % 3 == 1:
                pair_used.append(list_of_points[component_ind])
            elif component_ind % 3 == 2:
                new_list.append(pair_used)
                pair_used = []
        return new_list

    def export_polygon_to_shapefile(self, list_of_points=None,
                                    directory: str = './polygon',
                                    polygon_name='polygon') -> None:
        """
        Export a list of points as a polygon in a shapefile file.

        Args:
            polygon_name: Name of the polygon to store
            list_of_points: List of points to store as a polygon in shapefile format.
            directory: Directory and filename of the file to create

        Returns: None
        """
        if list_of_points is None:
            list_of_points = []

        w = shapefile.Writer(directory)

        # create the fields
        w.field('name', 'C')

        # Save the polygons
        points = self.__delete_z_axis(list_of_points)
        w.poly([points])

        # Save the data in the previously created fields.
        w.record(polygon_name)
        w.close()
