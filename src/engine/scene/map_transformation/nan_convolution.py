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
File with the definition of the NanConvolutionMapTransformation class, class in charge of deleting the points that are
surrounded with nan values.
"""

from typing import TYPE_CHECKING

import cv2
import numpy as np

from src.engine.scene.map_transformation.map_transformation import MapTransformation
from src.error.map_transformation_error import MapTransformationError

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene


class NanConvolutionMapTransformation(MapTransformation):
    """
    Class in charge of the map transformation that deletes points of the maps that are surrounded by nan values.
    """

    def __init__(self, model_to_modify: str, convolution_radius: int, nan_limit: float):
        """
        Constructor of the class.

        Args:
            model_to_modify: ID of the model to modify.
            convolution_radius: Radius of the kernel to use for the convolution.
            nan_limit: Percentage to use to check if to convert a point or not.

        """
        super().__init__(model_to_modify)
        self.__nan_percentage_limit = nan_limit
        self.__kernel_diameter = convolution_radius

        self.__model_vertices: np.ndarray = np.array([])

    def initialize(self, scene: 'Scene') -> None:
        """
        Get the data of the model and initialize the transformation.

        Args:
            scene: Scene to use to get the data of the model.

        Returns: None
        """
        model_list = scene.get_model_list()
        if self.model_id not in model_list:
            raise MapTransformationError(1)

        self.__model_vertices = scene.get_map2d_model_vertices_array(self.model_id)

    def apply(self) -> np.ndarray:
        """
        Apply the transformation to the vertices of the specified model.

        Returns: Array with the vertices of the model modified.
        """
        heights = self.__model_vertices[:, :, 2]
        heights_nan = np.isnan(heights)
        heights_nan_int = heights_nan.astype(np.float32)

        # Make the kernel of odd size if it is not
        # ----------------------------------------
        if self.__kernel_diameter % 2 == 0:
            self.__kernel_diameter += 1

        kernel = np.ones((self.__kernel_diameter, self.__kernel_diameter))
        kernel = kernel * (1.0 / (self.__kernel_diameter ** 2 - 1))
        kernel[int(self.__kernel_diameter / 2), int(self.__kernel_diameter / 2)] = 0

        # Apply the kernel to the vertices
        # --------------------------------
        nan_percentage_mask = cv2.filter2D(heights_nan_int, -1, kernel)

        # Modify values on the height matrix
        # ----------------------------------
        values_above_percentage = nan_percentage_mask > self.__nan_percentage_limit
        values_to_delete = np.logical_and(values_above_percentage, np.logical_not(heights_nan))
        heights[values_to_delete] = np.nan

        return self.__model_vertices
