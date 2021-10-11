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
Module that defines the main class to use for the transformation of the maps. All transformation that uses
complete maps must inherit from the class defined in this module.
"""

from typing import TYPE_CHECKING

import numpy as np

from src.error.map_transformation_error import MapTransformationError

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene


class MapTransformation:
    """
    Base class to use for the transformation of the maps.
    """

    def __init__(self, model_to_modify: str):
        self.__modified_model_id: str = model_to_modify

    @property
    def model_id(self) -> str:
        """Get the id of the model modified."""
        return self.__modified_model_id

    @model_id.setter
    def model_id(self, new_value: str) -> None:
        """Modify the id of the modified model."""
        self.__modified_model_id = new_value

    def initialize(self, scene: 'Scene') -> None:
        """
        Get the data necessary to apply the transformation over the maps.

        Args:
            scene: Scene to use to get the data.

        Returns: None
        """
        if self.model_id is None:
            raise MapTransformationError(0)

    def apply(self) -> np.ndarray:
        """
        Apply the transformation over the maps.

        Returns: Vertices of the new map.
        """
        raise NotImplementedError('Method not implemented.')
