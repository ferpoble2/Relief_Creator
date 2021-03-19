"""
Frame for the confirmation modals of the application.
"""

import imgui

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

log = get_logger(module="CONFIRMATION_MODAL")


class ConfirmationModal(Frame):
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

        self.__button_width = 150

        self.__should_show = False
        self.__modal_title = "Confirmation Modal"
        self.__msg = "This is a mock message to show in the confirmation modal. If you're watching this" \
                     " then there is a problem in the program."

        # auxiliary variables
        # -------------------
        self.__tool_before_pop_up = None

    def render(self) -> None:
        """
        Render a modal with the specified text.
        Returns: None
        """

        if self.__should_show:
            log.debug('Opened')

            # stores the active tool and deactivate it
            # ----------------------------------------
            self.__tool_before_pop_up = self._GUI_manager.get_active_tool()
            self._GUI_manager.set_active_tool(None)

            # open the pop up and size it
            # ---------------------------
            imgui.open_popup(self.__modal_title)
            self.__should_show = False

        imgui.set_next_window_size(-1, -1)
        imgui.set_next_window_position(imgui.get_io().display_size.x * 0.5,
                                       imgui.get_io().display_size.y * 0.5,
                                       imgui.ALWAYS,
                                       0.5,
                                       0.5)
        if imgui.begin_popup_modal(self.__modal_title)[0]:
            imgui.text_wrapped(self.__msg)

            if imgui.button("yes", self.__button_width):
                # call the function stored previously
                # -----------------------------------
                self.__yes_func()

                # return the original tool to the program
                # ---------------------------------------
                self._GUI_manager.set_active_tool(self.__tool_before_pop_up)

                # close the pop up
                # ----------------
                imgui.close_current_popup()

            imgui.same_line()
            if imgui.button("no", self.__button_width):
                # call the function stored previously
                # -----------------------------------
                self.__no_func()

                # return the original tool to the program
                # ---------------------------------------
                self._GUI_manager.set_active_tool(self.__tool_before_pop_up)

                # close the pop up
                # ----------------
                imgui.close_current_popup()

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
        self.__should_show = True
        self.__modal_title = modal_title
        self.__msg = msg

        self.__yes_func = yes_func
        self.__no_func = no_func