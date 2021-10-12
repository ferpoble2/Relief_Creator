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
File with the definition of the frame that shows the coordinates where the mouse is located on the map.
"""
from typing import TYPE_CHECKING

import imgui

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

if TYPE_CHECKING:
    from engine.GUI.guimanager import GUIManager

log = get_logger(module="DEBUG_FRAME")


class MouseCoordinates(Frame):
    """
    Class that render a frame with the mouse coordinates calculated according to the loaded map on the program.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        super().__init__(gui_manager)
        self.size = (300, 35)
        self.position = (
            self._GUI_manager.get_left_frame_width(),
            self._GUI_manager.get_window_height() - self.size[1])

        self.__alpha_value = 0.4
        self.__frame_name = 'Mouse Coordinates'

    def render(self) -> None:
        """
        Render the frame that shows the mouse coordinates.

        Returns: None
        """

        # Get the mouse position and get the coordinates of the map related to the position
        mouse_position = imgui.get_mouse_pos()
        map_coordinates = list(self._GUI_manager.get_map_coordinates_from_window_coordinates(mouse_position[0],
                                                                                             mouse_position[1]))

        # Render the frame only if the coordinates where obtained correctly, otherwise do not render it
        if map_coordinates != [None, None]:

            # Set the transparency and configure the frame before rendering it
            imgui.set_next_window_bg_alpha(self.__alpha_value)
            self._begin_frame(self.__frame_name, imgui.WINDOW_NO_TITLE_BAR)

            # Round the values obtained to show only two decimals
            map_coordinates[0] = round(map_coordinates[0], 2)
            map_coordinates[1] = round(map_coordinates[1], 2)

            height = self._GUI_manager.get_map_height_on_coordinates(map_coordinates[0],
                                                                     map_coordinates[1])
            if height is not None:
                height = round(height, 2)
                imgui.text(f'Mouse Coordinates: ({map_coordinates[0]}, {map_coordinates[1]}, {height})')
            else:
                imgui.text(f'Mouse Coordinates: ({map_coordinates[0]}, {map_coordinates[1]})')

            # Close the frame
            self._end_frame()
