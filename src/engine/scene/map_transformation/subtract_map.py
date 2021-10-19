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
Transformation that calculate the difference between the selected maps, generating a new map from there.
"""
from typing import TYPE_CHECKING

import numpy as np

from src.engine.scene.map_transformation.map_transformation import MapTransformation
from src.error.map_transformation_error import MapTransformationError

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene


class SubtractMap(MapTransformation):
    """
    Class in charge of the application of the SubtractMap transformation.

    Class modify the first map specified, subtracting the heights of the second map specified.
    """

    def __init__(self, model_to_modify: str, model_to_subtract: str):
        super().__init__(model_to_modify)
        self.__secondary_model_id = model_to_subtract

        self.__main_model_vertices = np.array([])
        self.__secondary_model_vertices = np.array([])

    def initialize(self, scene: 'Scene') -> None:
        """
        Get the information from the maps.

        Args:
            scene: Scene to use to get the information.

        Returns: None
        """
        model_list = scene.get_model_list()
        if self.model_id not in model_list:
            raise MapTransformationError(1)

        if self.__secondary_model_id is None:
            raise MapTransformationError(0)

        if self.__secondary_model_id not in model_list:
            raise MapTransformationError(1)

        self.__main_model_vertices = scene.get_map2d_model_vertices_array(self.model_id)
        self.__secondary_model_vertices = scene.get_map2d_model_vertices_array(self.__secondary_model_id)

    def apply(self) -> np.ndarray:
        """
        Apply the transformation over the vertices of the main model.

        This method modify the vertices of the model directly. Modifying the heights of the specified model and
        returning a reference to the vertices array of the model.

        Returns: Vertices of the main model modified.
        """
        main_model_heights = self.__main_model_vertices[:, :, 2]
        secondary_model_heights = np.nan_to_num(self.__secondary_model_vertices[:, :, 2])

        main_model_heights = main_model_heights - secondary_model_heights
        self.__main_model_vertices[:, :, 2] = main_model_heights

        return self.__main_model_vertices
