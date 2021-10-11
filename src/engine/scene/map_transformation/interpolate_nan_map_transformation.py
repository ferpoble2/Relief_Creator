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
File with the definition of the InterpolateNanMapTransformation class, class in charge of the interpolation of all the
nan values that are present on a map.

Module also defines an enum class with the types of interpolation that can be used when interpolating the nan values
of the map.
"""
from enum import Enum
from typing import TYPE_CHECKING

import numpy as np

from src.engine.scene.geometrical_operations import interpolate_nan
from src.engine.scene.map_transformation.map_transformation import MapTransformation
from src.error.map_transformation_error import MapTransformationError

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene


class InterpolateNanMapTransformationType(Enum):
    """
    Enum that defines the types of interpolation that can be used in the transformation.
    """
    linear = 'linear'
    cubic = 'cubic'
    nearest = 'nearest'


class InterpolateNanMapTransformation(MapTransformation):
    """
    Class in charge of the map transformation that interpolate all the nan values present on the map.
    """

    def __init__(self, model_id: str,
                 interpolation_type: InterpolateNanMapTransformationType = InterpolateNanMapTransformationType.linear):
        """
        Constructor of the class.
        """
        super().__init__(model_id)
        self.__interpolation_type = interpolation_type
        self.__model_vertices = np.array([])

    def initialize(self, scene: 'Scene') -> None:
        """
        Get the data for the model to modify.

        Args:
            scene: Scene to use to get the data from the model.

        Returns: None
        """
        model_list = scene.get_model_list()
        if self.model_id not in model_list:
            raise MapTransformationError(1)

        self.__model_vertices = scene.get_map2d_model_vertices_array(self.model_id)

    def apply(self) -> np.ndarray:
        """
        Interpolate all the NaN values of the map.

        The transformation modify the vertices of the model directly. The returned array is a pointer to the vertices
        of the model.
        """
        heights = self.__model_vertices[:, :, 2]
        nan_mask = np.isnan(heights)

        new_heights = interpolate_nan(heights,
                                      nan_mask,
                                      self.__interpolation_type.value)

        self.__model_vertices[:, :, 2] = new_heights
        return self.__model_vertices
