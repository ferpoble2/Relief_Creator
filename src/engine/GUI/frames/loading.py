"""
Sample frame for the application GUI.
"""

import imgui

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

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

    def render(self) -> None:
        """
        Render the loading text when the program is in a loading state.
        Returns: None
        """

        if self._GUI_manager.is_program_loading():
            imgui.open_popup("Loading")

        if imgui.begin_popup_modal("Loading")[0]:
            imgui.text("Please wait a moment...")
            imgui.end_popup()

