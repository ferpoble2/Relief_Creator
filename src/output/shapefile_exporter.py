"""
File that contains the class shapefileExporter.
"""
import shapefile

from src.error.not_enought_points_error import NotEnoughPointsError
from src.utils import is_clockwise


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

    def export_list_of_polygons(self, list_of_points: list, list_of_parameters: list, list_of_polygon_names: list,
                                directory: str) -> None:
        """
        Export a list of polygons into a shapefile file.

        Args:
            list_of_points: List with list of points of the polygons. (list of lists)
            list_of_parameters: List with the parameters of the polygons. (list of dictionaries)
            list_of_polygon_names: List with the names of the polygons.
            directory: Directory + filename of the shapefile file to store.

        Returns: None
        """
        assert len(list_of_points) == len(list_of_parameters) == len(list_of_polygon_names)

        polygon_number = len(list_of_points)
        key_type_dict = {}
        processed_point_list = []

        # add the name to the parameters
        for ind in range(polygon_number):
            if 'name' not in list_of_parameters[ind]:
                list_of_parameters[ind]['name'] = list_of_polygon_names[ind]

            if len(list_of_points[ind]) < 6:
                raise NotEnoughPointsError('One or more polygons from the list does not have enough points'
                                           'to export')

            # sort the points to be counter clockwise
            points = self.__delete_z_axis(list_of_points[ind])
            if is_clockwise(points):
                points.reverse()  # polygons must be defined CCW

            processed_point_list.append(points)

            # store all the keys and the type of the parameter in another dictionary
            for k, v in list(list_of_parameters[ind].items()):
                if k not in key_type_dict:
                    key_type_dict[k] = type(v)

        w = shapefile.Writer(directory)

        # create the fields for the parameters
        for k, v in list(key_type_dict.items()):
            if v == str:
                w.field(k, 'C')
            elif v == float:
                w.field(k, 'N')
            elif v == bool:
                w.field(k, 'L')
            else:  # in case of unknown data type
                w.field(k, 'C')  # convert the parameter to string
                key_type_dict[k] = str

        for ind in range(polygon_number):

            # dictionary with all the keys
            dict_params = {k: None for k in key_type_dict.keys()}
            for k, v in list(list_of_parameters[ind].items()):
                dict_params[k] = key_type_dict[k](v)  # convert the value to the specified type

            params = list(dict_params.values())
            w.record(*params)
            w.poly([processed_point_list[ind]])

        w.close()

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

        Any other parameter with another type will be converted to string.

        Fieldnames should not be longer than 10 characters (accepted by shapefile standarts). Any name longer than
        10 characters long will be split and only the first 10 characters will be considered for the name of the field.

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

        # add the name if there is not in the parameters
        if 'name' not in parameters:
            parameters['name'] = polygon_name
        if len(list_of_points) < 6:  # two points
            raise NotEnoughPointsError('Not enough points to export this polygon.')

        w = shapefile.Writer(directory)

        # create the fields
        for k, v in list(parameters.items()):
            if type(v) == str:
                w.field(k, 'C', size=len(v))
            elif type(v) == float:
                decimals = len(str(v).split('.')[1])
                w.field(k, 'N', decimal=decimals)
            elif type(v) == bool:
                w.field(k, 'L')
            else:  # in case of unknown data type
                w.field(k, 'C')  # convert the parameter to string
                parameters[k] = str(v)

        # Save the polygons
        points = self.__delete_z_axis(list_of_points)
        if is_clockwise(points):
            points.reverse()  # polygons must be defined CCW

        params = list(parameters.values())
        w.record(*params)
        w.poly([points])

        # Save the data in the previously created fields.
        w.close()
