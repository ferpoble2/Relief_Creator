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
Module that defines the abstract class NanInterpolation, class in charge of defining the logic of the interpolations
that do not consider the elements currently on the interpolation zone and just interpolate the new values from the
values at the border of the interpolation zone.
"""
from abc import ABC
from typing import List, TYPE_CHECKING

import numpy as np
from shapely.geometry.polygon import LinearRing

from src.engine.scene.geometrical_operations import delete_z_axis, generate_mask, get_bounding_box_indexes, \
    get_external_polygon_points
from src.engine.scene.interpolation.interpolation import Interpolation
from src.error.interpolation_error import InterpolationError
from src.utils import is_clockwise

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene


class NanInterpolation(Interpolation, ABC):
    """
    Abstract class to use when implementing new interpolation classes that do not use the values in the
    interpolation zone of the maps.
    """

    def __init__(self, model_id: str, polygon_id: str, distance: float):
        super().__init__(model_id, polygon_id, distance)

        self._polygon_points: List[float] = []
        self._external_polygon_points: List[float] = []
        self._model_vertices: np.ndarray = np.array([])

    def initialize(self, scene: 'Scene') -> None:
        """
        Get the data to use for the interpolation of the points external to the polygon.

        Args:
            scene: Scene to use to get the data.

        Returns: None
        """
        super().initialize(scene)

        self._model_vertices = scene.get_map2d_model_vertices_array(self.model_id)
        self._polygon_points = scene.get_polygon_points(self.polygon_id)

        if not scene.is_polygon_planar(self.polygon_id):
            raise InterpolationError(6)

        if len(self._polygon_points) < 9:
            raise InterpolationError(1)

        self._external_polygon_points = get_external_polygon_points(self._polygon_points, self.distance)

    def fill_interpolation_zone_with_nan(self,
                                         model_vertices: np.ndarray,
                                         external_polygon_points: list[float],
                                         internal_polygon_points: list[float]):
        """
        Fill the interpolation zone (points that are in the external polygon and outside of the internal polygon) with
        nan values.

        Args:
            model_vertices: Height array to modify (x, y)
            external_polygon_points: Points of the external polygon. [x, y, z, x, y, z, ...]
            internal_polygon_points: Points of the internal polygon. [x, y, z, x, y, z, ...]
        """

        # Get the bounding box of the external polygon
        # --------------------------------------------
        max_x_index, max_y_index, min_x_index, min_y_index = self.get_bounding_box_indices(external_polygon_points)
        points_cut = model_vertices[min_y_index:max_y_index, min_x_index:max_x_index, :]
        heights = model_vertices[:, :, 2]
        heights_cut = heights[min_y_index:max_y_index, min_x_index:max_x_index]

        # Generate masks to filter the points
        # -----------------------------------
        mask_external = generate_mask(points_cut, self._external_polygon_points)
        mask_internal = generate_mask(points_cut, self._polygon_points)

        # Modify the vertices height
        # --------------------------
        in_between_mask = mask_external != mask_internal
        heights_cut[in_between_mask == True] = np.nan  # noqa

    def get_bounding_box_indices(self, exterior_polygon: list[float]) -> (int, int, int, int):
        """
        Get the indices of the vertices that fully enclose the specified polygon.

        Args:
            exterior_polygon: Exterior polygon to use. [x, y, z, x, y, z, ...]

        Returns: Tuple with the indices to use as the bounding box. (max_x_index, max_y_index, min_x_index, min_y_index)
        """

        # Format points
        # -------------
        external_points_no_z_axis = delete_z_axis(exterior_polygon)
        if is_clockwise(external_points_no_z_axis):
            external_points_no_z_axis.reverse()

        exterior_polygon_linear_ring = LinearRing(external_points_no_z_axis)

        # Get bounding box
        # ----------------
        min_x_index, max_x_index, min_y_index, max_y_index = get_bounding_box_indexes(self._model_vertices,
                                                                                      exterior_polygon_linear_ring)
        min_x_index -= 1
        max_x_index += 1
        min_y_index -= 1
        max_y_index += 1

        return max_x_index, max_y_index, min_x_index, min_y_index
