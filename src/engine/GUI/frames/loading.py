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
Sample frame for the application GUI.
"""

from typing import TYPE_CHECKING

import imgui

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

if TYPE_CHECKING:
    from src.engine.GUI.guimanager import GUIManager

log = get_logger(module="LOADING_FRAME")


class Loading(Frame):
    """
    Class that render a sample frame in the application.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        super().__init__(gui_manager)
        self.__loading_message = "Please wait a moment..."
        self.__windows_width, self.__windows_height = 300, 100

    def post_render(self) -> None:
        """
        Implement all the logic related to the popup to show when the program is loading.

        Returns: None
        """

        if self._GUI_manager.is_program_loading():
            imgui.open_popup("Loading")
            self._GUI_manager.set_controller_keyboard_callback_state(False)

        if imgui.begin_popup_modal("Loading")[0]:
            imgui.set_window_size(self.__windows_width, self.__windows_height)
            imgui.text(self.__loading_message)

            if not self._GUI_manager.is_program_loading():
                imgui.close_current_popup()
                self._GUI_manager.set_controller_keyboard_callback_state(True)

            imgui.end_popup()

    def render(self) -> None:
        """
        Do nothing since this frame does not have any windows to render.
        Returns: None
        """
        pass

    def set_loading_message(self, new_msg: str) -> None:
        """
        Set a new loading message to show in the frame.

        Args:
            new_msg: New message to show

        Returns: None
        """
        self.__loading_message = new_msg
