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
Module that defines the Font Enum class, class in charge of defining the different fonts that can be used in the
GUI.
"""
from enum import Enum


class Font(Enum):
    """
    Enum class with all the fonts defined on the GUI.

    To add a new font to the GUI, define it here as follows: (ttf_file_location, font_size)
    """
    REGULAR = ('resources/fonts/open_sans/OpenSans-Regular.ttf', 18)
    BOLD = ('resources/fonts/open_sans/OpenSans-Bold.ttf', 18)
    TOOL_TITLE = ('resources/fonts/open_sans/OpenSans-Regular.ttf', 25)
    TOOL_SUB_TITLE = ('resources/fonts/open_sans/OpenSans-Regular.ttf', 22)
