"""
File with the class ImguiWrapper, class that act as a wrapper for the imgui functions.
"""

import imgui


class ImguiWrapper:
    """
    Class that act as a wrapper for the imgui functionality.
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.

        Args:
            gui_manager: gui_manager to use.
        """
        self.__gui_manager = gui_manager

    def close_current_popup_modal(self) -> None:
        """
        Close the current popup modal and set all the configuration necessary to continue with the program.

        Returns:

        """
        self.__gui_manager.enable_glfw_keyboard_callback()
        imgui.close_current_popup()

    def open_popup_modal(self, popup_id: str) -> None:
        """
        Open the popup modal with the given name and set all the configuration previous too open it.

        Args:
            popup_id: Popup ID

        Returns: None
        """
        self.__gui_manager.disable_glfw_keyboard_callback()
        imgui.open_popup(popup_id)
