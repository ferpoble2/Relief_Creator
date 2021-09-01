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
Frame for the text modals to use in the application.
"""

from typing import TYPE_CHECKING

import imgui

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

if TYPE_CHECKING:
    from engine.GUI.guimanager import GUIManager

log = get_logger(module="TEXT_MODAL")


class TextModal(Frame):
    """
    Class to render a modal in the application with a specified text.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        super().__init__(gui_manager)

        # Variables of the window to draw on the GUI
        # ------------------------------------------
        self.__windows_width = 300
        self.__windows_height = None
        self.__margin_button = 20
        self.__button_height = 25

        # Variables of the modal window
        # -----------------------------
        self.__should_show = False
        self.__modal_title = "Modal"
        self.__msg = "Sample text for the modal"

        # Auxiliary variables
        # -------------------
        self.__tool_before_pop_up = None
        self.__first_frame_call = False

    def post_render(self) -> None:
        """
        Render the popup if it is necessary.

        Returns: None
        """

        # Open the popup modal if the variable should_show was changed to True in some point of the application and
        # do the logic related to the opening of a modal (deactivate tools, disable controller, ...)
        # ---------------------------------------------------------------------------------------------------------
        if self.__should_show:
            # Ask imgui to open the popup modal
            imgui.open_popup(self.__modal_title)

            # Stores the active tool and deactivate it
            self.__tool_before_pop_up = self._GUI_manager.get_active_tool()
            self._GUI_manager.set_active_tool(None)

            # Disable keyboard input
            self._GUI_manager.disable_controller_keyboard_callback()

            # Return the variable should_show to false since the modal was already opened
            self.__should_show = False

        # Set the window size and position and then render the popup modal if it was opened before
        # ----------------------------------------------------------------------------------------
        imgui.set_next_window_size(self.__windows_width, -1)
        imgui.set_next_window_position(imgui.get_io().display_size.x * 0.5,
                                       imgui.get_io().display_size.y * 0.5,
                                       imgui.ALWAYS,
                                       0.5,
                                       0.5)
        if imgui.begin_popup_modal(self.__modal_title)[0]:
            # Show the text in the modal popup
            imgui.text_wrapped(self.__msg)

            # Render a button to close the popup and do the logic related to the closing of a modal
            if imgui.button("Close", self.__windows_width - self.__margin_button, self.__button_height):
                # Return the original tool to the program
                self._GUI_manager.set_active_tool(self.__tool_before_pop_up)

                # Close the pop up
                self.__should_show = False
                imgui.close_current_popup()
                self._GUI_manager.enable_controller_keyboard_callback()

            imgui.end_popup()

    def render(self) -> None:
        """
        Do nothing since there is not a window to draw.

        Returns: None
        """
        pass

    def set_modal_text(self, modal_title: str, msg: str) -> None:
        """
        Set a modal to show in the program.

        Args:
            modal_title: Title of the modal to show
            msg: New message to show

        Returns: None
        """
        log.debug("Modal set to show")
        self.__should_show = True
        self.__modal_title = modal_title
        self.__msg = msg
