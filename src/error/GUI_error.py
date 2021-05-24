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
File containing the class GUIError
"""
from src.error.base_error import BaseError


class GUIError(BaseError):
    """
    Error to use for GUI related errors.
    """

    def __init__(self, code=0):
        """
        Constructor of the class.
        """
        super(GUIError, self).__init__(code=code)

        self.codes = {
            0: 'Default Error.',
            1: 'Filter ID not found on the list of filters.'
        }
