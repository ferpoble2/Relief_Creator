"""
File with the class ImguiWrapper, class that act as a wrapper for the imgui functions.
"""

from imgui import *


def close_current_popup_modal(gui_manager) -> None:
    """
    Close the current popup modal and set all the configuration necessary to continue with the program.

    Args:
        gui_manager: Gui manager being used by the program.

    Returns:

    """
    gui_manager.enable_glfw_keyboard_callback()
    close_current_popup()


def open_popup_modal(gui_manager, popup_id: str) -> None:
    """
    Open the popup modal with the given name and set all the configuration previous too open it.

    Args:
        gui_manager: Gui manager being used by the program.
        popup_id: Popup ID

    Returns: None
    """
    gui_manager.disable_glfw_keyboard_callback()
    open_popup(popup_id)
