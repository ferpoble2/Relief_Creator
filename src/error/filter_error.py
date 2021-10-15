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
Module that defines the class FilterError, class in charge of the errors related to the Filters.
"""
from typing import Dict

from src.error.base_error import BaseError


class FilterError(BaseError):
    """
    Class to raise when errors related to the filters happen in the program.
    """

    def __init__(self, code: int = 0, data: Dict[str, any] = None):
        """
        Constructor of the class

        Args:
            code: Code of the error.
        """
        super().__init__(code, data)

        self.codes: Dict[int, str] = {
            0: 'Polygon can not be None',
            1: 'Polygon does not have at least 3 points.',
            2: 'Polygon is not planar',
            3: 'Polygon not found in the program'
        }
