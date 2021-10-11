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
Module that defines the class Transformation, class that stores the logic of the transformation of the program.

Every transformation must have, at least, one model and polygon associated to them. Otherwise, an exception is raised.
"""

from typing import List, TYPE_CHECKING

import numpy as np

from src.engine.scene.filter.filter import Filter
from src.error.transformation_error import TransformationError

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene


class Transformation:
    """
    Class that defines the base logic for the transformations defined in the program.
    """

    def __init__(self, model_id: str, polygon_id: str, filter_list=None):
        if filter_list is None:
            filter_list = []

        self.__model_id = model_id
        self.__polygon_id = polygon_id
        self.__filter_list: List[Filter] = filter_list

    @property
    def model_id(self) -> str:
        """Get the ID of the model used in the transformation."""
        return self.__model_id

    @property
    def polygon_id(self) -> str:
        """Get the ID of the polygon used in the transformation."""
        return self.__polygon_id

    @property
    def filter_list(self) -> List[Filter]:
        """Get a list with the filters to be used in the transformation."""
        return self.__filter_list

    def initialize(self, scene: 'Scene') -> None:
        """
        Initialize the parameters of the transformation using the data from the specified scene.

        Args:
            scene: Scene to use to initialize the parameters of the transformation.

        Returns: None
        """
        for transformation_filter in self.filter_list:
            transformation_filter.initialize(scene)

        if self.model_id is None:
            raise TransformationError(10)

        if self.polygon_id is None:
            raise TransformationError(11)

    def apply_filters(self, model_vertices: np.ndarray) -> np.ndarray:
        """
        Apply the filters defined in the transformation and returns the mask array.

        Args:
            model_vertices: Vertices of the model to use for the application of the filters. Shape must be (x, y, 3)
                            with each vertex containing the x-coordinate, y-coordinate and the height of the vertex.

        Returns: Numpy array with shape (x, y) with True in the values that should be considered for the transformation
                 and False in the values that should not be considered.
        """
        mask = np.full(model_vertices.shape[:2], True)
        for transformation_filter in self.filter_list:
            mask = transformation_filter.get_mask(model_vertices, mask)

        return mask

    def apply(self) -> np.ndarray:
        """
        Apply the transformation to the specified points.

        Returns: Array with the modified points.
        """
        raise NotImplementedError('Method not implemented.')
