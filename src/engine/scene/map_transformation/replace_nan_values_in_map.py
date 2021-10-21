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
File that defines the class ReplaceNanValuesInMap, class in charge of replacing with nan all the values that are
correctly defined in another map.
"""
from typing import TYPE_CHECKING

import numpy as np

from src.engine.scene.map_transformation.map_transformation import MapTransformation
from src.error.map_transformation_error import MapTransformationError

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene


class ReplaceNanValuesInMap(MapTransformation):
    """
    Class in charge of applying the transformation that replaces all the values defined correctly in one map with nan
    values in another map.
    """

    def __init__(self, base_model: str, model_to_check_for_values: str):
        super().__init__(base_model)

        self.__secondary_model_id = model_to_check_for_values
        self.__main_model_vertices = np.array([])
        self.__secondary_model_vertices = np.array([])

    def initialize(self, scene: 'Scene') -> None:
        """
        Get the vertices of the models.

        Args:
            scene: Scene to use to get the data.

        Returns: None
        """
        model_list = scene.get_model_list()
        if self.model_id not in model_list:
            raise MapTransformationError(1)
        if self.__secondary_model_id not in model_list:
            raise MapTransformationError(1)

        self.__main_model_vertices = scene.get_map2d_model_vertices_array(self.model_id)
        self.__secondary_model_vertices = scene.get_map2d_model_vertices_array(self.__secondary_model_id)

    def apply(self) -> np.ndarray:
        """
        Change all the correctly defined vertices on the secondary model into nan in the main model.

        Returns: Vertices modified.
        """
        main_model_heights = self.__main_model_vertices[:, :, 2]
        secondary_model_heights = self.__secondary_model_vertices[:, :, 2]

        values_to_modify = np.logical_not(np.isnan(secondary_model_heights))
        main_model_heights[values_to_modify] = np.nan

        return self.__main_model_vertices
