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
Module that defines the main filter of the scene.

All filters defined on the scene must inherit from this class.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from src.engine.scene.scene import Scene


class Filter:
    """
    Class that defines the main logic of the filters in the application.
    """
    name: str = 'Base Filter'

    def initialize(self, scene: 'Scene') -> None:
        """
        Initialize the parameters of the filter using a specified scene.

        Args:
            scene: Scene to use for the initialization.

        Returns: None
        """
        pass

    def get_mask(self, model_vertices: 'np.ndarray', mask: 'np.ndarray') -> 'np.ndarray':
        """
        Return the mask generated from the application of the filter.

        The vertices of the model must have three values, the x-coordinate, the y-coordinate and the height of the
        vertices.

        The filter will be applied over the values specified in the mask variable, modifying the values stored inside
        the variable.

        Args:
            mask: Initial mask of booleans to use for the modification. Shape must be (x, y)
            model_vertices: Model vertices to use to get the mask. Shape must be (x, y, 3)

        Returns: Modified mask.
        """
        raise NotImplementedError('Method get mask not implemented on the filter.')
