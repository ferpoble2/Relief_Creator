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
File with the definition of a base error, class to use as parent to all the new generated errors of the program.
"""
from typing import Dict


class BaseError(Exception):
    """
    Class to use as parent to all the new exceptions.
    """

    def __init__(self, code: int = 0, data: Dict[str, any] = None):
        """
        Constructor of the class.

        Args:
            code: Code of the error.
        """
        # Data associated with the error.
        self.data: Dict[str, any] = data if data is not None else {}

        # Code of the error
        self.code: int = code

        # List of all codes that the error can have and its description.
        self.codes: Dict[int, str] = {
            0: 'Default Error.'
        }

    def __str__(self) -> str:
        """
        Returns: Message showed in the console.
        """
        return f"{self.get_code_message()} Data: {self.data}"

    def get_code_message(self) -> str:
        """
        Get the message stored describing the error.

        Returns: string
        """
        return self.codes[self.code]
