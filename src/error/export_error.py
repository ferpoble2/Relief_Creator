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
Document with the class ExportError, class to use for error that happens during the export process
"""
from src.error.base_error import BaseError


class ExportError(BaseError):
    """
    Base class to use for exportation errors.
    """

    def __init__(self, code: int = 0):
        """
        Constructor of the class

        Args:
            code: Code of the error.
        """
        self.code = code
        self.codes = {
            0: 'Default Error.',
            1: 'One or more polygon from the list does not have enough points',
            2: 'Not enough points to export this polygon',
            3: 'Can not find key containing height information in the loaded file.',
            4: 'Can not read longitude or latitude values from file.'
        }
