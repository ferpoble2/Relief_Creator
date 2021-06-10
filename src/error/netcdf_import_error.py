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
File with the class definition of the NetCDFImportError, class to use when there is errors importing netcdf files.
"""


class NetCDFImportError(Exception):
    """
    Class to use when there are errors in the import of netcdf files.
    """

    def __init__(self, code, data=None):
        """
        Constructor of the class.
        """
        self.code = code
        self.data = data
        self.codes = {
            0: 'Default Error',
            1: 'A key from the file is not in the list of accepted keys on the program.',
            2: 'A key to read the latitude of the file is not in the list of accepted keys on the program',
            3: 'A key to read the longitude of the file is not in the list of accepted keys on the program',
            4: 'A key to read the height of the file is not in the list of accepted keys on the program'
        }

    def __str__(self) -> str:
        """
        Returns: Message showed in the console.
        """
        return self.get_code_message()

    def get_code_message(self) -> str:
        """
        Get the message stored describing the error.

        Returns: string
        """
        return self.codes[self.code]
