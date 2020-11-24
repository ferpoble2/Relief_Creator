"""
Test frame for the GUI (default for imgui)
"""
from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger
import imgui

log = get_logger(module="TEST WINDOW")


class TestWindow(Frame):
    """
    Class that render the test_window of imgui.
    """

    def render(self) -> None:
        """
        Render the test window on the application.
        Returns: None
        """
        imgui.show_test_window()
