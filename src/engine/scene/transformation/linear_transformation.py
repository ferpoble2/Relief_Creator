#  BEGIN GPL LICENSE BLOCK
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  END GPL LICENSE BLOCK

"""
Module that defines the LinearTransformation class. Class that is in charge of the linear transformation of the points.
"""

from typing import List, TYPE_CHECKING

import numpy as np
from shapely.geometry.polygon import LinearRing as LinearRing

from src.engine.scene.filter.filter import Filter
from src.engine.scene.geometrical_operations import delete_z_axis, generate_mask, get_bounding_box_indexes
from src.engine.scene.transformation.transformation import Transformation
from src.error.transformation_error import TransformationError

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene


class LinearTransformation(Transformation):
    """
    Class in charge of the Linear Transformation of the points inside a polygon.
    """

    def __init__(self,
                 model_id: str,
                 polygon_id: str,
                 min_height: float,
                 max_height: float,
                 filter_list: List[Filter] = None):
        super().__init__(model_id, polygon_id, filter_list)

        self.__min_height = min_height
        self.__max_height = max_height

        self.__polygon_points: List[float] = []
        self.__vertex_array: np.ndarray = np.array([])

    def __interpolate(self, value: float, value_min: float, value_max: float, target_min: float = -1,
                      target_max: float = 1, convert: bool = True) -> float:

        """
        Interpolate the given value between the other specified values.

        To interpolate the value between the target values it is necessary to specify an initial interval in which
        the value exists (value_min and value_max) and the target interval to interpolate it (target_min and target_max).

        If value_min and value_max are equal, then average between the targets values will be returned.

        Args:
            convert: True to convert the value to float
            value: Value to interpolate.
            value_min: Minimum value of the values.
            value_max: Maximum value of the values.
            target_min: Minimum value of the interpolation interval.
            target_max: Maximum value of the interpolation interval.

        Returns: Interpolated value.
        """
        if convert:
            value = float(value)

        # Check values and store them in the correct variables
        value_min, value_max = min(value_min, value_max), max(value_min, value_max)
        target_min, target_max = min(target_min, target_max), max(target_min, target_max)

        # Case initial interval is just one value.
        if value_min == value_max:
            return (target_min + target_max) / 2.0

        if target_min == target_max:
            return target_max

        # Return corresponding values
        return (value - value_min) * (float(target_max) - target_min) / (float(value_max) - value_min) + target_min

    def initialize(self, scene: 'Scene') -> None:
        """
        Initialize the parameters of the transformation.

        Args:
            scene: Scene to use to get the data for the transformation.

        Returns: None
        """
        super().initialize(scene)

        self.__polygon_points = scene.get_polygon_points(self.polygon_id)
        self.__vertex_array = scene.get_map2d_model_vertices_array(self.model_id)

        if self.__min_height > self.__max_height:
            raise TransformationError(9)

        if len(self.__polygon_points) < 9:
            raise TransformationError(2)

        if not scene.is_polygon_planar(self.polygon_id):
            raise TransformationError(3)

    def apply(self) -> np.ndarray:
        """
        Apply the transformation of the points over the vertices of the model.

        The vertices of the model are modified directly, the returned array is a reference to the vertices of the
        model modified.

        Returns: Model vertices modified.
        """
        points_array = self.__vertex_array
        height = self.__vertex_array[:, :, 2]

        # generate polygon and get the bounding box of the indices.
        points_no_z_axis = delete_z_axis(self.__polygon_points)
        closed_polygon = LinearRing(points_no_z_axis)
        [min_x_index, max_x_index, min_y_index, max_y_index] = get_bounding_box_indexes(points_array,
                                                                                        closed_polygon)

        points_array_cut = points_array[min_y_index:max_y_index, min_x_index:max_x_index, :]
        height_cut = height[min_y_index:max_y_index, min_x_index:max_x_index]

        # do nothing in case that no points from the map are selected
        if len(points_array_cut) == 0:
            return self.__vertex_array

        polygon_flags = generate_mask(points_array_cut, self.__polygon_points)
        filtered_flags = self.apply_filters(points_array_cut)
        flags = polygon_flags & filtered_flags

        # modify the height linearly if there are points to modify
        if len(height_cut[filtered_flags]) > 0:
            current_min_height = np.nanmin(height_cut[flags])
            current_max_height = np.nanmax(height_cut[flags])

            new_height = self.__interpolate(height_cut[flags],
                                            float(current_min_height),
                                            float(current_max_height),
                                            self.__min_height,
                                            self.__max_height,
                                            False)

            height_cut[flags] = new_height
            height[min_y_index:max_y_index, min_x_index:max_x_index] = height_cut

        return self.__vertex_array
