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
import imgui

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger
from src.type_hinting import *

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
        self.__width = 300
        self.__height = 35
        self.__alpha_value = 0.4

        self.__frame_name = 'Mouse Coordinates'
        self.__frame_fixed_flags = imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE | \
                                   imgui.WINDOW_NO_TITLE_BAR
        self.__frame_unfixed_flags = imgui.WINDOW_NO_TITLE_BAR

        self.change_position(
            [self._GUI_manager.get_left_frame_width(),
             self._GUI_manager.get_window_height() - self.__height])

    def render(self) -> None:
        """
        Render the main sample text.
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
            if self._GUI_manager.are_frame_fixed():
                imgui.begin(self.__frame_name, False, self.__frame_fixed_flags)
                imgui.set_window_position(self._GUI_manager.get_left_frame_width(),
                                          self._GUI_manager.get_window_height() - self.__height)
                imgui.set_window_size(self.__width,
                                      self.__height,
                                      0)
            else:
                imgui.begin(self.__frame_name, False, self.__frame_unfixed_flags)

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
            imgui.end()
