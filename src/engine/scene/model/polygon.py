# BEGIN GPL LICENSE BLOCK
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# END GPL LICENSE BLOCK

"""
File containing the class polygon.

This class stores all the information related to the polygons that can be draw on the screen of the program.
"""
import OpenGL.GL as GL
import numpy as np
from shapely.geometry import LineString

from src.engine.scene.model.dashed_lines import DashedLines
from src.engine.scene.model.lines import Lines
from src.engine.scene.model.model import Model
from src.engine.scene.model.points import Points
from src.error.polygon_error import PolygonError
from src.utils import get_logger

log = get_logger(module="POLYGON")


class Polygon(Model):
    """
    Class in charge of the polygons of the program.

    The parameter z_offset can be modified to change the value of the z-axis used for the polygons (and all the
    sub-models that are used to render a polygon).
    """

    def __init__(self, scene, id_polygon: str, point_list: list = None, parameters: dict = None):
        """
        Constructor of the class.

        Generate a new polygon with or without data.

        Polygons should be rendered in 2D mode. The default value for the z-axis coordinate of the points of the models
        that conform a polygon is set to 0.5. This height can be changed using the variable z_offset, the value stored
        in this variable will be added to the z_coordinate on the shaders.

        Args:
            id_polygon: Id to use to identify the polygon on the program.
            point_list: List of initial points to use in the polygon. [[x,y],[x,y],...]
            parameters: Dictionary with initial parameters to set in the polygon. {parameter_name: value,...}
        """
        super().__init__(scene)

        # Information of the model
        # ------------------------
        self.id = id_polygon
        self.draw_mode = GL.GL_LINES
        self.update_uniform_values = False
        self.__name = self.get_id()

        # Models used to generate the polygon on the scene
        # ------------------------------------------------
        self.__point_model = Points(scene)  # model to use to draw the points
        self.__lines_model = Lines(scene)  # model to use to draw the lines
        self.__last_line_model = DashedLines(scene)  # model to use to render the last line of the polygon

        # Parameters stored in the polygon to use when exporting to shapefile
        # -------------------------------------------------------------------
        self.__parameters = parameters if parameters is not None else {}

        # Properties of the model
        # -----------------------
        self.__is_planar = True
        self.__default_height_value = 0.5

        # Initialize polygon if data is given
        # -----------------------------------
        if point_list is not None:

            # check for consistency on the data
            test_line = LineString(point_list)
            if not test_line.is_simple:
                raise PolygonError(0)

            if len(point_list) != len(set(point_list)):
                raise PolygonError(1, {'point_list': point_list})

            # prepare the data
            point_array = np.array(point_list)
            point_array = point_array.reshape((-1, 2))

            points = np.empty((len(point_list), 3))
            points[:, 0] = point_array[:, 0]
            points[:, 1] = point_array[:, 1]
            points[:, 2] = self.__default_height_value

            self.__point_model = Points(scene, points)
            self.__lines_model = Lines(scene, point_list=points)

            self.__update_planar_state()
            self.update_last_line()

    def __check_intersection(self, points: list = None) -> bool:
        """
        Join the points given in a line and check if there is intersections.

        Args:
            points: List with the points to check. [x,y,z,x,y,z,x,y,z,...]
        """
        points_array = np.array(points)
        points_array = points_array.reshape((-1, 3))
        return not LineString(points_array).is_simple

    def __check_repeated_point(self, x: float, y: float, z: float) -> bool:
        """
        Check if a point already exist on the polygon.

        Args:
            x: x-coordinate of the point
            y: y-coordinate of the point
            z: z-coordinate of the point

        Returns: Boolean representing if point already exist in the polygon.
        """
        point_list_array = np.array(self.get_point_list() + [x, y, z])
        point_list_array = point_list_array.reshape((-1, 3))
        return len(np.unique(point_list_array, axis=0)) != len(point_list_array)

    def __str__(self):
        """
        Format how polygons are printed on the console.

        Returns: String representing the polygon.
        """
        return f"Points model: {self.__point_model}\nLines model: {self.__lines_model}"

    def __update_planar_state(self):
        """
        Update the variable indicating if the polygon is planar or not.

        Returns: None
        """
        if self.get_point_number() > 2:
            # ask for intersections on the closed polygon.
            point_list = self.get_point_list()
            if self.__check_intersection(points=point_list + [point_list[0], point_list[1], point_list[2]]):
                self.__is_planar = False
            else:
                self.__is_planar = True

    def add_point(self, x: float, y: float, z: float = None) -> None:
        """
        Add a new point to the list of points.

        Args:
            x: x position of the point
            y: y position of the point
            z: z position of the point

        Returns: None
        """
        if z is None:
            z = self.__default_height_value

        # check if point is already on the polygon
        if self.__check_repeated_point(x, y, z):
            raise PolygonError(1, {'repeated_point': (x, y, z)})

        # check if lines intersect
        if self.get_point_number() > 2:
            point_list = self.get_point_list()

            # do not let the creation of lines that intersect
            if self.__check_intersection(point_list + [x, y, z]):
                raise PolygonError(0)

            # if the completion line intersect, then change the state of the polygon.
            if self.__check_intersection(point_list + [x, y, z, point_list[0], point_list[1], point_list[2]]):
                self.__is_planar = False
            else:
                self.__is_planar = True

        # add points to the point model
        self.__point_model.add_point(x, y, z)

        # list of points
        point_list = self.get_point_list()

        # draw line only if there is more than one point
        if self.get_point_number() > 1:
            self.__lines_model.add_line((point_list[-6], point_list[-5], point_list[-4]),
                                        (point_list[-3], point_list[-2], point_list[-1]))

        # update the last line of the model
        self.update_last_line()

    def remove_parameter(self, key: str) -> None:
        """
        Remove a parameter from the dictionary of parameters.

        Args:
            key: Key to be deleted.

        Returns: None
        """
        self.__parameters.pop(key)

    def draw(self, active_polygon=False) -> None:
        """
        Set how and when to draw the polygons.
        """

        # draw the components on the screen
        if active_polygon:
            self.__lines_model.set_use_borders(True)
            self.__last_line_model.set_use_borders(True)
        else:
            self.__lines_model.set_use_borders(False)
            self.__last_line_model.set_use_borders(False)

        self.__lines_model.draw()
        self.__last_line_model.draw()
        self.__point_model.draw()

    def get_id(self) -> str:
        """
        Get the id of the polygon.

        Returns: Id of the polygon
        """
        return self.id

    def get_name(self) -> str:
        """
        Get the name of the polygon.

        Returns: Name of the polygon
        """
        return self.__name

    def get_parameter(self, key: str) -> any:
        """
        Get the parameter from the polygon.

        Args:
            key: Key of the parameter.

        Returns: Value of the parameter. None if parameter does not exist.
        """
        return self.__parameters.get(key)

    def get_parameter_list(self) -> list:
        """
        Return all the parameters of the polygon as a list.

        Returns: List with the parameters [(key, value), (key, value), ...]
        """
        return [(k, v) for k, v in self.__parameters.items()]

    def get_point_list(self) -> list:
        """
        Get the list of points.
        The format of the list is as follows: [x1, y1, z1, x2, y2, z2, ...]

        Returns: List of points
        """
        return self.__point_model.get_point_list()

    def get_point_number(self) -> int:
        """
        Return the number of points of the polygon.

        Returns: Number of points of the polygon.
        """
        # return int(len(self.__point_list) / 3)
        return int(len(self.get_point_list()) / 3)

    def is_planar(self) -> bool:
        """
        Check if the polygon is planar or not

        Returns: Boolean indicating if the polygon is planar or not.
        """
        return self.__is_planar

    def remove_last_added_point(self) -> None:
        """
        Remove the last point added to the polygon.

        Does nothing if there is no points.

        Returns: None
        """

        # only works when there is points in the model
        if self.get_point_number() > 0:
            self.__point_model.remove_last_added_point()
            self.__lines_model.remove_last_added_line()

            self.update_last_line()
            self.__update_planar_state()

    def set_dot_color(self, color: list) -> None:
        """
        Set the color to draw the dots of the polygon.

        The color must be in a list-like object in the order of RGBA with values between 0 and 1.

        Args:
            color: Color to be used by the polygon

        Returns: None
        """
        log.debug(f"Changing polygon dot color to {color}")
        self.__point_model.set_normal_color(tuple(color))

    def set_id(self, new_id: str) -> None:
        """
        Set a new id for the polygon.

        Args:
            new_id: New ID of the polygon.

        Returns: None
        """
        self.id = new_id

    def set_line_color(self, color: list) -> None:
        """
        Set the color to draw the lines of the polygon.

        The color must be in a list-like object in the order of RGBA with values between 0 and 1.

        Args:
            color: Color to be used by the polygon

        Returns: None
        """
        log.debug(f"Changing polygon color to {color}")
        self.__lines_model.set_line_color(color)
        self.__last_line_model.set_line_color(color)

    def set_name(self, new_name: str) -> None:
        """
        Set a new name for the polygon.

        Args:
            new_name: New name of the polygon

        Returns: None
        """
        self.__name = new_name

    def set_new_parameter(self, key: str, value: str) -> None:
        """
        Set a new parameter to be stored in the polygon.

        Args:
            key: Key for the parameter
            value: Value to store

        Returns: None
        """
        self.__parameters[key] = value

    def update_last_line(self) -> None:
        """
        Update the last line of the polygon.

        Returns: None
        """
        # Remove the last line if exist
        point_list = self.get_point_list()
        point_number = self.get_point_number()

        self.__last_line_model.remove_last_added_line()

        # Add a new line only if there is 3 or more points
        if point_number >= 3:
            self.__last_line_model.add_line((point_list[-3], point_list[-2], point_list[-1]),
                                            (point_list[0], point_list[1], point_list[2]))
