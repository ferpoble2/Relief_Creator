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
File with utils functions to read CPT files. (file wih the information about how to set the colors of the models).
"""
from typing import List

from src.utils import get_logger

log = get_logger(module='CTP')


def is_numeric(text: str) -> bool:
    """
    Check if a string is numeric or not.

    Args:
        text: String to analyze.

    Returns:
        True if the string was numeric, False otherwise.

    """
    try:
        float(text)
        return True
    except ValueError:
        return False


def read_file(file_name: str) -> List[dict]:
    """
    Read a CTP file and extracts the colors and the limits associated to them.

    Return a list of dictionaries with the colors defined in CPT file in the same order as they are defined in the
    file.

    Important:
        This method does not delete repeated pairs of height/color that could be stored in the file.

    Example output:
        [{height: 0, color: [0,0,0]},
        {height: 100, color: [0,255,0]},
        {height: 100, color: [0,0,0]},
        {height: 200, color: [255,0,0]},
        ...]

    Args:
        file_name: Name of the file to read.

    Returns:
        Dictionary with the limits and the colors associated.

    """
    log.debug(f'Reading file {file_name}')

    file = open(file_name, 'r')

    color_pallet = []
    for line in file.readlines():

        # split the line to get the contents
        line = line.split()

        # Check if the line have information of the color
        # -----------------------------------------------
        # do not consider empty lines
        empty_line = len(line) == 0

        # do not consider lines that does not have enough elements to define colors
        not_enough_elements = len(line) < 4

        # dont consider lines not related to the definition of color
        not_color_definition = len(line) >= 4 and (not is_numeric(line[0]) or not is_numeric(line[2]))

        # Append color defined in the line only if the line has color information
        # -----------------------------------------------------------------------
        if not empty_line and not not_enough_elements and not not_color_definition:
            values = line
            color_pallet.append({
                'height': float(values[0]),
                'color': values[1].split('/')
            })
            color_pallet.append({
                'height': float(values[2]),
                'color': values[3].split('/')
            })

    return color_pallet
