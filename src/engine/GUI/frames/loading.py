"""
Sample frame for the application GUI.
"""

import src.engine.GUI.imgui_wrapper as imgui

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

log = get_logger(module="LOADING_FRAME")


class Loading(Frame):
    """
    Class that render a sample frame in the application.
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        super().__init__(gui_manager)
        self.__loading_message = "Please wait a moment..."
        self.__windows_width, self.__windows_height = 300, 100

    def render(self) -> None:
        """
        Render the loading text when the program is in a loading state.
        Returns: None
        """

        if self._GUI_manager.is_program_loading():
            imgui.open_popup_modal(self._GUI_manager, "Loading")

        if imgui.begin_popup_modal("Loading")[0]:
            imgui.set_window_size(self.__windows_width, self.__windows_height)
            imgui.text(self.__loading_message)
            if not self._GUI_manager.is_program_loading():
                imgui.close_current_popup_modal(self._GUI_manager)
            imgui.end_popup()

    def set_loading_message(self, new_msg: str) -> None:
        """
        Set a new loading message to show in the frame.

        Args:
            new_msg: New message to show

        Returns: None
        """
        self.__loading_message = new_msg
