"""
Frame for the text modals to use in the application.
"""

import imgui

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

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

        self.__windows_width = 300
        self.__windows_height = None
        self.__margin_button = 20
        self.__button_height = 25

        self.__should_show = False
        self.__modal_title = "Modal"
        self.__msg = "Sample text for the modal"

        # auxiliary variables
        # -------------------
        self.__tool_before_pop_up = None

    def render(self) -> None:
        """
        Render a modal with the specified text.
        Returns: None
        """

        if self.__should_show:
            # stores the active tool and deactivate it
            # ----------------------------------------
            self.__tool_before_pop_up = self._GUI_manager.get_active_tool()
            self._GUI_manager.set_active_tool(None)

            # open the pop up and size it
            # ---------------------------
            imgui.open_popup(self.__modal_title)
            self.__should_show = False

        imgui.set_next_window_size(self.__windows_width, -1)
        if imgui.begin_popup_modal(self.__modal_title)[0]:
            imgui.text_wrapped(self.__msg)

            if imgui.button("Close", self.__windows_width - self.__margin_button, self.__button_height):
                # return the original tool to the program
                # ---------------------------------------
                self._GUI_manager.set_active_tool(self.__tool_before_pop_up)

                # close the pop up
                # ----------------
                imgui.close_current_popup()

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
