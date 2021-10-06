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
Module that defines the class HeightGreaterThan, class in charge of the application of the filter that select points
depending of the height that they have.
"""
import numpy as np

from src.engine.scene.filter.filter import Filter


class HeightGreaterThan(Filter):
    """
    Class in charge of the application of the filter HeightGreaterThan.
    """
    name: str = 'Height >='

    def __init__(self, height_limit: float):
        super().__init__()
        self.__height_limit = height_limit

    @property
    def height_limit(self) -> float:
        """Get the height limit used by the filter."""
        return self.__height_limit

    @height_limit.setter
    def height_limit(self, new_value: float) -> None:
        """Set the height limit to use in the filter."""
        self.__height_limit = new_value

    def get_mask(self, model_vertices: 'np.ndarray', mask: 'np.ndarray') -> 'np.ndarray':
        """
        Set False value to all vertices with height less than specified.

        The vertices of the model must have three values, the x-coordinate, the y-coordinate and the height of the
        vertices.

        The filter will be applied over the values specified in the mask variable, modifying the values stored inside
        the variable.

        Args:
            mask: Initial mask of booleans to use for the modification. Shape must be (x, y)
            model_vertices: Model vertices to use to get the mask. Shape must be (x, y, 3)

        Returns: Modified mask.
        """
        height = model_vertices[:, :, 2]

        indices_outside_filter = np.where(height < self.__height_limit)
        mask[indices_outside_filter] = False

        return mask
