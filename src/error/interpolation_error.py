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
File with the InterpolationError class, class to use when raising exceptions related to the interpolation process.
"""
from src.error.scene_error import SceneError


class InterpolationError(SceneError):
    """
    Class to use when there is an error in the transformation process of a model.
    """

    def __init__(self, code: int = 0):
        """
        Constructor of the class.
        """
        super(InterpolationError, self).__init__(code)

        self.codes = {
            0: 'Error description not selected.',
            1: 'Not enough points in the polygon to do the interpolation.',
            2: 'Distance must be greater than 0 to realize the interpolation.',
            3: 'Can not interpolate model that is not an instance of Map2DModel.',
            4: 'Model can not be None.',
            5: 'Polygon can not be None',
            6: 'Polygon is not planar'
        }
