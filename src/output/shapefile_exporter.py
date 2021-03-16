"""
File that contains the class shapefileExporter.
"""
import shapefile

from src.error.not_enought_points_error import NotEnoughPointsError
from src.error.unknown_data_type_error import UnknownDataTypeError


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

    def __is_clockwise(self, points):
        """
        Check if a list of 2D points are in CW order or not.

        Args:
            points: List of 2D points [(1.x,1.y),(2.x,2.y),...]

        Returns: Boolean indicating if points are CW or not.
        """

        # points is your list (or array) of 2d points.
        assert len(points) > 0
        s = 0.0
        for p1, p2 in zip(points, points[1:] + [points[0]]):
            s += (p2[0] - p1[0]) * (p2[1] + p1[1])
        return s > 0.0

    def export_polygon_to_shapefile(self, list_of_points=None,
                                    directory: str = './polygon',
                                    polygon_name: str = 'polygon',
                                    parameters: dict = None) -> None:
        """
        Export a list of points as a polygon in a shapefile file.

        Will only export the parameters that are from the follow types:
        - str
        - float
        - boolean

        Any other parameter with another type will be converted to string

        Args:
            parameters: Dictionary with the parameters of the polygon.
            polygon_name: Name of the polygon to store.
            list_of_points: List of points to store as a polygon in shapefile format.
            directory: Directory and filename of the file to create.

        Returns: None
        """
        if parameters is None:
            parameters = {}
        if list_of_points is None:
            list_of_points = []

        if len(list_of_points) < 6:  # two points
            raise NotEnoughPointsError('Not enough points to export this polygon.')

        w = shapefile.Writer(directory)

        # create the fields
        for k, v in list(parameters.items()):
            if type(v) == str:
                w.field(k, 'C')
            elif type(v) == float:
                w.field(k, 'N')
            elif type(v) == bool:
                w.field(k, 'L')
            else:   # in case of unknown data type
                w.field(k, 'C')  # convert the parameter to string
                parameters[k] = str(v)

        # Save the polygons
        points = self.__delete_z_axis(list_of_points)
        if self.__is_clockwise(points):
            points.reverse()  # polygons must be defined CCW

        params = list(parameters.values())
        w.record(*params)
        w.poly([points])

        # Save the data in the previously created fields.
        w.close()
