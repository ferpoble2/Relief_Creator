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
Module that defines the NearestInterpolation class. Class in charge of executing the interpolation of the points
external to the specified polygon using the nearest algorithm.
"""

import numpy as np

from src.engine.scene.geometrical_operations import interpolate_nan
from src.engine.scene.interpolation.nan_interpolation import NanInterpolation


class NearestInterpolation(NanInterpolation):
    """
    Class in charge of interpolating the points external to the specified polygon using a nearest method of
    interpolation.
    """

    def apply(self) -> np.ndarray:
        """
        Apply the interpolation to the specified model.

        The interpolation modify the heights of the points that are between the external
        and internal polygon.

        The vertices of the model are modified directly, the returned array is a reference to the vertices of the
        model modified.

        Returns: Array with the modified points.
        """

        # Fill interpolation area with nan values
        # ---------------------------------------
        self.fill_interpolation_zone_with_nan(self._model_vertices,
                                              self._external_polygon_points,
                                              self._polygon_points)
        max_x_index, max_y_index, min_x_index, min_y_index = self.get_bounding_box_indices(
            self._external_polygon_points)

        # Modify the vertices height
        # --------------------------
        heights = self._model_vertices[:, :, 2]
        heights_cut = heights[min_y_index:max_y_index, min_x_index:max_x_index]
        interpolated_heights = interpolate_nan(heights_cut, np.isnan(heights_cut), 'nearest')
        heights[min_y_index:max_y_index, min_x_index:max_x_index] = interpolated_heights

        return self._model_vertices
