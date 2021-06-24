# BEGIN GPL LICENSE BLOCK
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# END GPL LICENSE BLOCK

"""
File that contains all the exceptions related to the scene.
"""

from src.error.base_error import BaseError


class SceneError(BaseError):
    """
    Class used to represent the scene related exceptions.
    """

    def __init__(self, code: int = 0):
        """
        Constructor of the class

        Args:
            code: Code of the error.
        """
        super(SceneError, self).__init__(code)

        self.codes = {
            0: 'Default Error',
            1: 'Polygon used is not planar.',
            2: 'The polygon used doesnt have at least 3 vertices.',
            3: 'Can not use that model for transforming points. Try using a Map2DModel.',
            4: 'Polygon id can not be None.',
            5: 'Polygon ID not found.',
            6: 'Polygon not in the list of polygons to be draw.',
            7: 'Model not found in the scene'
        }
