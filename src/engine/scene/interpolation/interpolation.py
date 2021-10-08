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
Module that defines the class interpolation. Base class to use for the definition of the other types of interpolation.
"""
from typing import TYPE_CHECKING

import numpy as np

from src.error.interpolation_error import InterpolationError

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene


class Interpolation:
    """
    Base class to use for the definition of the interpolation.

    The interpolation modify the height of the vertices that are external to the specified polygon at a given distance.
    """

    def __init__(self, model_id: str, polygon_id: str, distance: float):
        self.__model_id = model_id
        self.__polygon_id = polygon_id
        self.__distance_interpolation = distance

    @property
    def model_id(self) -> str:
        """Get the ID of the model used in the interpolation."""
        return self.__model_id

    @property
    def polygon_id(self) -> str:
        """Get the ID of the polygon used in the interpolation."""
        return self.__polygon_id

    @property
    def distance(self) -> float:
        """Get the distance to use for the interpolation"""
        return self.__distance_interpolation

    def initialize(self, scene: 'Scene') -> None:
        """
        Initialize the parameters of the transformation using the data from the specified scene.

        Args:
            scene: Scene to use to initialize the parameters of the transformation.

        Returns: None
        """
        if self.model_id is None:
            raise InterpolationError(4)

        if self.polygon_id is None:
            raise InterpolationError(5)

        if self.distance <= 0:
            raise InterpolationError(2)

    def apply(self) -> np.ndarray:
        """
        Apply the interpolation to the specified model.

        Returns: Array with the modified points.
        """
        raise NotImplementedError('Method not implemented.')
