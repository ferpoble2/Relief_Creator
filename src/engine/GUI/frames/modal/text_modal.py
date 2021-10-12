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
Frame for the text modals to use in the application.
"""

from typing import TYPE_CHECKING

import imgui

from src.engine.GUI.frames.modal.modal import Modal
from src.utils import get_logger

if TYPE_CHECKING:
    from src.engine.GUI.guimanager import GUIManager

log = get_logger(module="TEXT_MODAL")


class TextModal(Modal):
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
        self.size = (300, -1)
        self.__margin_button = 20
        self.__button_height = 25

        # Variables of the modal window
        # -----------------------------
        self.__modal_title = "Modal"
        self.__msg = "Sample text for the modal"

        # Auxiliary variables
        # -------------------
        self.__first_frame_call = False

    def post_render(self) -> None:
        """
        Render the popup if it is necessary.

        Returns: None
        """
        if self._begin_modal(self.__modal_title):
            imgui.text_wrapped(self.__msg)

            if imgui.button("Close", self.size[0] - self.__margin_button, self.__button_height):
                self._close_modal()

            imgui.end_popup()

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
