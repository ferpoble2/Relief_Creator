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
Module that defines the CubicInterpolation class. Class in charge of executing the interpolation of the points
external to the specified polygon using a cubic algorithm.
"""

from typing import List, TYPE_CHECKING

import numpy as np
from shapely.geometry.polygon import LinearRing

from src.engine.scene.geometrical_operations import delete_z_axis, generate_mask, get_bounding_box_indexes, \
    get_external_polygon_points, interpolate_nan
from src.engine.scene.interpolation.interpolation import Interpolation
from src.error.interpolation_error import InterpolationError
from src.utils import is_clockwise

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene


class CubicInterpolation(Interpolation):
    """
    Class in charge of interpolating the points external to the specified polygon using a cubic method of
    interpolation.

    The interpolation generates a surface with the points to interpolate with the minimum curvature, the values of the
    points to interpolate are extracted from the generated surface.
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

        self.__model_vertices = scene.get_map2d_model_vertices_array(self.model_id).copy()
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

        Returns: Array with the modified points.
        """

        # Format the data of the external polygon
        # ---------------------------------------
        external_points_no_z_axis = delete_z_axis(self.__external_polygon_points)

        if is_clockwise(external_points_no_z_axis):
            external_points_no_z_axis.reverse()

        exterior_polygon = LinearRing(external_points_no_z_axis)

        # Get the bounding box of the external polygon
        # --------------------------------------------
        min_x_index, max_x_index, min_y_index, max_y_index = get_bounding_box_indexes(self.__model_vertices,
                                                                                      exterior_polygon)
        min_x_index -= 1
        max_x_index += 1
        min_y_index -= 1
        max_y_index += 1

        heights = self.__model_vertices[:, :, 2]
        points_cut = self.__model_vertices[min_y_index:max_y_index, min_x_index:max_x_index, :]
        heights_cut = heights[min_y_index:max_y_index, min_x_index:max_x_index]

        # Generate masks to filter the points
        # -----------------------------------
        mask_external = generate_mask(points_cut, self.__external_polygon_points)
        mask_internal = generate_mask(points_cut, self.__polygon_points)

        # Modify the vertices height
        # --------------------------
        in_between_mask = mask_external != mask_internal
        heights_cut[in_between_mask == True] = np.nan  # noqa
        heights_cut = interpolate_nan(heights_cut, in_between_mask, 'cubic')
        heights[min_y_index:max_y_index, min_x_index:max_x_index] = heights_cut

        return self.__model_vertices
