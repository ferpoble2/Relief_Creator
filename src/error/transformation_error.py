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
File with the class TransformationError, class to raise when there is an error in the transformation process.
"""
from src.error.scene_error import SceneError


class TransformationError(SceneError):
    """
    Class to use when there is an error in the transformation process of a model.
    """

    def __init__(self, code: int = 0, filter_name=''):
        """
        Constructor of the class.
        """
        super().__init__(code)

        self.codes = {
            0: 'Default Error.',
            1: 'Transformation type not recognized by the program.',
            2: 'The polygon used doesnt have at least 3 vertices.',
            3: 'Polygon used is not planar.',
            4: 'Can not use that model for transforming points. Try using a Map2DModel.',
            5: f'Can not get data of filter. Unrecognized filter {filter_name}',
            6: 'Polygon to use in a filter not found or selected.',
            7: 'Polygon used in a filter does not have at least 3 vertices.',
            8: 'Polygon used in filter is not simple/planar',
            9: 'Max height selected is lower than the min height selected',
            10: 'Model not specified.',
            11: 'Polygon not specified.'
        }
