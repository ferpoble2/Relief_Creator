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
Module that defines the FillNanTransformation class. Class that is in charge of the transformation tha fill the
selected values with nan.
"""
from typing import List, TYPE_CHECKING

import numpy as np
from shapely.geometry import LinearRing

from src.engine.scene.geometrical_operations import delete_z_axis, generate_mask, get_bounding_box_indexes
from src.engine.scene.transformation.transformation import Transformation
from src.error.model_transformation_error import ModelTransformationError

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene


class FillNanTransformation(Transformation):
    """
    Class in charge of the FillNanTransformation. Transformation change all the heights selected to Nan values.
    """

    def __init__(self, model_id: str, polygon_id: str, filter_list=None):
        super().__init__(model_id, polygon_id, filter_list)

        self.__polygon_points: List[float] = []
        self.__vertex_array: np.ndarray = np.array([])

    def initialize(self, scene: 'Scene') -> None:
        """
        Initialize the parameters of the transformation.

        Args:
            scene: Scene to use to get the data for the transformation.

        Returns: None
        """
        super().initialize(scene)

        self.__polygon_points = scene.get_polygon_points(self.polygon_id)
        self.__vertex_array = scene.get_map2d_model_vertices_array(self.model_id).copy()

        if len(self.__polygon_points) < 9:
            raise ModelTransformationError(2)

        if not scene.is_polygon_planar(self.polygon_id):
            raise ModelTransformationError(3)

    def apply(self) -> np.ndarray:
        """
        Apply the transformation of the points over the vertices of the model.

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
            height_cut[flags] = np.nan
            height[min_y_index:max_y_index, min_x_index:max_x_index] = height_cut

        return self.__vertex_array
