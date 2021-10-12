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
Frame for the confirmation modals of the application.
"""

from typing import TYPE_CHECKING

import imgui

from src.engine.GUI.frames.modal.modal import Modal
from src.utils import get_logger

if TYPE_CHECKING:
    from engine.GUI.guimanager import GUIManager

log = get_logger(module="CONFIRMATION_MODAL")


class ConfirmationModal(Modal):
    """
    Class to render a modal in the application with a specified text.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.

        Args:
            gui_manager: GUI manager to use for the render process.
        """
        super().__init__(gui_manager)

        self.__yes_func = lambda: log.debug('Called yes function.')
        self.__no_func = lambda: log.debug('Called no function.')

        self.size = (300, -1)
        self.__button_width = self.size[0] / 2 - 12

        self.__modal_title = "Confirmation Modal"
        self.__msg = "This is a mock message to show in the confirmation modal. If you're watching this" \
                     " then there is a problem in the program."

    def post_render(self) -> None:
        """
        Render a modal with the specified text.
        Returns: None
        """
        if self._begin_modal(self.__modal_title):
            imgui.text_wrapped(self.__msg)

            if imgui.button("yes", self.__button_width):
                self.__yes_func()
                self._close_modal()

            imgui.same_line()
            if imgui.button("no", self.__button_width):
                self.__no_func()
                self._close_modal()

            imgui.end_popup()

    def set_confirmation_text(self, modal_title: str, msg: str, yes_func: callable, no_func: callable) -> None:
        """
        Set a modal to show in the program.

        Args:
            no_func: Function to execute when the answer to the popup is no.
            yes_func: Function to execute when the answer to the popup is yes.
            modal_title: Title of the modal to show.
            msg: New message to show.

        Returns: None
        """
        log.debug("Modal set to show")
        self.__modal_title = modal_title
        self.__msg = msg

        self.__yes_func = yes_func
        self.__no_func = no_func
