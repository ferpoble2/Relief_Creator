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
File that contains all the exceptions related to the polygons.
"""
from typing import Dict

from src.error.base_error import BaseError


class PolygonError(BaseError):
    """
    Class used to represent the polygon related exceptions.
    """

    def __init__(self, code: int = 0, data: Dict[str, any] = None):
        """
        Constructor of the class.
        """
        super().__init__(code, data)

        self.codes = {
            0: 'Line intersect another one already on the polygon.',
            1: 'Point already exist on the polygon.'
        }
