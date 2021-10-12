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
Main Frame class for the others elements to use.
"""

from typing import TYPE_CHECKING

import imgui

if TYPE_CHECKING:
    from engine.GUI.guimanager import GUIManager


class Frame:
    """
    Class to manager the frame behaviour. New frames must be children of this class.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        self.__position = (100, 100)
        self.__size = (400, 400)
        self._GUI_manager = gui_manager

    @property
    def position(self) -> tuple:
        """
        Get the position of the frame.

        Returns: list with the position of the frame.
        """
        return self.__position

    @position.setter
    def position(self, new_position: tuple) -> None:
        """
        Change the position of the frame in the screen. Only works properly when fixed_position is set to True.

        Args:
            new_position: New position where to put the frame. ([x_pos, y_pos])
        Returns: None
        """
        self.__position = new_position

    @property
    def size(self) -> tuple:
        """
        Get the size of the frame.

        Returns: Tuple with the size of the frame.
        """
        return self.__size

    @size.setter
    def size(self, new_size: tuple) -> None:
        """
        Set the new size of the frame.

        Args:
            new_size: Tuple with the new size of the frame.

        Returns: None
        """
        self.__size = new_size

    def _begin_frame(self, frame_name: str, additional_flags: int = None):
        """
        Begin a new frame.

        Initialize all the logic related to the fix/unfix and the necessary flags for the frame to be rendered correctly
        on the GUI.

        Args:
            frame_name: Name of the frame to draw.
            additional_flags: Other flags to use on the frame.

        Returns: None
        """
        if self._GUI_manager.get_frame_fixed_state():
            flags = imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_FOCUS_ON_APPEARING
            flags = flags | additional_flags if additional_flags is not None else flags
            imgui.begin(frame_name,
                        False,
                        flags)
            imgui.set_window_position(self.position[0], self.position[1])
            imgui.set_window_size(self.size[0], self.size[1], 0)
        else:
            flags = imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_FOCUS_ON_APPEARING
            flags = flags | additional_flags if additional_flags is not None else flags
            imgui.begin(frame_name,
                        False,
                        flags)

    def _end_frame(self):
        """
        End a frame.

        Execute all the logic related to the closing process of a frame.

        Returns: None
        """
        imgui.end()

    def add_new_polygon(self, polygon_id) -> None:
        """
        Function called when a new polygon is added to the program. Do nothing unless defined in child classes.

        Args:
            polygon_id: ID of the polygon.

        Returns: None
        """
        pass

    def post_render(self) -> None:
        """
        Method that executes after the rendering process of all the frames.

        Notes:
            Due to the implementation of the module imgui, it is recommendable to implement all the logic
            related to the popups in this method to prevent bugs.

        Popup definition example:
            def render():
                if ...:
                    self.should_open_popup = True

            def post_render():
                if self.should_open_popup:
                    imgui.open_popup('popup_id')

                if imgui.begin_popup_modal("popup_id")[0]:
                    ...
                    imgui.end_popup()

        Returns: None
        """
        pass

    def render(self) -> None:
        """
        Draw the frames on the screen.

        Notes:
            Due to the implementation of imgui, it is recommendable to implement here all the logic related to the
            windows that the program will show always (imgui.begin(...)/imgui.end()) and to program all the logic
            related to the popups to the post_render method.

            By default, the imgui.begin() method focus the windows when being created, this may cause some popups to be
            closed when the windows are created. To change this behaviour use the flag
            imgui.WINDOW_NO_FOCUS_ON_APPEARING on the windows.

        Returns: None
        """
        raise NotImplementedError("Render method not implemented.")
