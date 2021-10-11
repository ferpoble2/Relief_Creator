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
Module that defines the MergeMapsTransformation class, class in charge of the transformation tha merge two maps into
one.

The resulting map has the values of the specified base map with the values of the second map into the cells where the
base map has nan values.
"""

from typing import TYPE_CHECKING

import numpy as np

from src.engine.scene.geometrical_operations import merge_matrices
from src.engine.scene.map_transformation.map_transformation import MapTransformation
from src.error.map_transformation_error import MapTransformationError

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene


class MergeMapsTransformation(MapTransformation):
    """
    Class in charge of the transformation that merges two maps into one.
    """

    def __init__(self, base_model_id: str, second_model_id: str):
        super().__init__(base_model_id)
        self.__second_model_id = second_model_id

        self.__base_model_vertices = np.array([])
        self.__second_model_vertices = np.array([])

    def initialize(self, scene: 'Scene') -> None:
        """
        Get the data of the models to generate the new map.

        Args:
            scene: Scene to use to get the information of the maps.

        Returns: None
        """
        if self.__second_model_id is None:
            raise MapTransformationError(0)

        model_id_list = scene.get_model_list()
        if self.model_id not in model_id_list or self.__second_model_id not in model_id_list:
            raise MapTransformationError(1)

        self.__base_model_vertices = scene.get_map2d_model_vertices_array(self.model_id)
        self.__second_model_vertices = scene.get_map2d_model_vertices_array(self.__second_model_id)

    def apply(self) -> np.ndarray:
        """
        Merge the two proportioned maps and store the resulting map in the result model specified.

        The vertices of the base model are modified directly on the model. The returned array is a pointer to the
        array of the vertices of the model.

        Returns: Vertices of the new map generated
        """
        base_model_heights = self.__base_model_vertices[:, :, 2]
        second_model_heights = self.__second_model_vertices[:, :, 2]

        new_heights = merge_matrices(base_model_heights, second_model_heights)

        self.__base_model_vertices[:, :, 2] = new_heights
        return self.__base_model_vertices
