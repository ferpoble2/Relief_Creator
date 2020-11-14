"""
File with all the windows that the program must use to render the gui.
"""
import imgui


def test_window() -> None:
    """
    Define the test window to use in the GUI.
    Returns: None
    """
    imgui.new_frame()
    imgui.show_test_window()
    imgui.end_frame()
