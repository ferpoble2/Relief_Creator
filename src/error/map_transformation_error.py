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
Module that defines the class MapTransformationError, class to use when errors related to the map_transformation
module occur.
"""
from src.error.scene_error import SceneError


class MapTransformationError(SceneError):
    """
    Class to use when there is an error in the transformation process of a model.
    """

    def __init__(self, code: int = 0, filter_name=''):
        """
        Constructor of the class.
        """
        super().__init__(code)

        self.codes = {
            0: 'Model can not be None',
            1: 'Model not found in the scene',
            2: 'One polygon used in the transformation is not planar.'
        }
