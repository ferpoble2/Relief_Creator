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
Module that defines the SmoothInterpolation class. Class in charge of executing the smooth interpolation of the points
external to the specified polygon.
"""

from typing import List, TYPE_CHECKING

import numpy as np
from shapely.geometry.polygon import LinearRing
from skimage.filters import gaussian

from src.engine.scene.geometrical_operations import delete_z_axis, generate_mask, get_bounding_box_indexes, \
    get_external_polygon_points
from src.engine.scene.interpolation.interpolation import Interpolation
from src.error.interpolation_error import InterpolationError

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene


class SmoothInterpolation(Interpolation):
    """
    Class in charge of applying the smoothing algorithm to the points external to the specified polygon.

    The interpolation is executed using a gaussian filter over the points external to the polygon, modifying them
    so the difference between the height of the points and they neighbours become smaller.
    """

    def __init__(self, model_id: str, polygon_id: str, distance: float):
        super().__init__(model_id, polygon_id, distance)

        self.__polygon_points: List[float] = []
        self.__external_polygon_points: List[float] = []
        self.__model_vertices: np.ndarray = np.array([])

    def initialize(self, scene: 'Scene') -> None:
        """
        Get the data to use for the interpolation of the points external to the polygon.

        Args:
            scene: Scene to use to get the data.

        Returns: None
        """
        super().initialize(scene)

        self.__model_vertices = scene.get_map2d_model_vertices_array(self.model_id)
        self.__polygon_points = scene.get_polygon_points(self.polygon_id)

        if not scene.is_polygon_planar(self.polygon_id):
            raise InterpolationError(6)

        if len(self.__polygon_points) < 9:
            raise InterpolationError(1)

        self.__external_polygon_points = get_external_polygon_points(self.__polygon_points, self.distance)

    def apply(self) -> np.ndarray:
        """
        Apply the interpolation to the specified model.

        The interpolation modify the heights of the points that are between the external
        and internal polygon.

        The vertices of the model are modified directly, the returned array is a reference to the vertices of the
        model modified.

        Returns: Array with the modified points.
        """

        # Format the data
        # ---------------
        external_points_no_z_axis = delete_z_axis(self.__external_polygon_points)

        # Get bounding box and cut the data to use for the interpolation
        # --------------------------------------------------------------
        min_x_index, max_x_index, min_y_index, max_y_index = get_bounding_box_indexes(
            self.__model_vertices,
            LinearRing(external_points_no_z_axis))

        heights = self.__model_vertices[:, :, 2]

        points_cut = self.__model_vertices[min_y_index:max_y_index, min_x_index:max_x_index, :]
        heights_cut = heights[min_y_index:max_y_index, min_x_index:max_x_index]

        # Apply the filter to the points
        # ------------------------------
        new_heights = gaussian(heights_cut)

        mask = generate_mask(points_cut, self.__polygon_points)
        mask_external = generate_mask(points_cut, self.__external_polygon_points)
        mask_in_between = mask != mask_external

        heights_cut[mask_in_between] = new_heights[mask_in_between]
        heights[min_y_index:max_y_index, min_x_index:max_x_index] = heights_cut

        return self.__model_vertices
