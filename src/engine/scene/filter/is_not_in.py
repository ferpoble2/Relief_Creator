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
Module that defines the filter IsNotIn, filter in charge of selecting the points that are not inside a specified
polygon.
"""
from typing import List, TYPE_CHECKING, Union

import numpy as np

from src.engine.scene.filter.filter import Filter
from src.engine.scene.geometrical_operations import generate_mask
from src.error.filter_error import FilterError

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene


class IsNotIn(Filter):
    """
    Class in charge of the logic of the IsNotIn filter.
    """

    name: str = 'Is not in'

    def __init__(self, polygon_id: Union[str, None]):
        """
        Constructor of the class.

        Args:
            polygon_id: ID of the polygon to use for the transformation.
        """
        super().__init__()
        self.__polygon_id: Union[str, None] = polygon_id
        self.__polygon_points: List[float] = []

    @property
    def polygon_id(self) -> Union[str, None]:
        """Get the polygon used by the filter."""
        return self.__polygon_id

    @polygon_id.setter
    def polygon_id(self, new_value: str) -> None:
        """Set the polygon to use in the filter."""
        self.__polygon_id = new_value

    def initialize(self, scene: 'Scene') -> None:
        """
        Initialize the parameters of the filter using the values stored in the Scene.

        Args:
            scene: Scene to use to get the data for the initialization.
        """
        if self.polygon_id is None:
            raise FilterError(0)

        if self.polygon_id not in scene.get_polygon_id_list():
            raise FilterError(3)

        if not scene.is_polygon_planar(self.polygon_id):
            raise FilterError(2)

        self.__polygon_points = scene.get_polygon_points(self.__polygon_id)

        if len(self.__polygon_points) < 9:
            raise FilterError(1)

    def get_mask(self, model_vertices: 'np.ndarray', mask: 'np.ndarray') -> 'np.ndarray':
        """
        Set False value in the mask to all the points that are inside the specified polygon.

        The vertices of the model must have three values, the x-coordinate, the y-coordinate and the height of the
        vertices.

        The filter will be applied over the values specified in the mask variable, modifying the values stored inside
        the variable.

        Args:
            mask: Initial mask of booleans to use for the modification. Shape must be (x, y)
            model_vertices: Model vertices to use to get the mask. Shape must be (x, y, 3)

        Returns: Modified mask.
        """
        polygon_mask = generate_mask(model_vertices, self.__polygon_points)
        indices = np.where(polygon_mask == True)
        mask[indices] = False

        return mask
