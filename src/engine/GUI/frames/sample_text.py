"""
Sample frame for the application GUI.
"""

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger
import imgui

log = get_logger(module="SAMPLE TEXT")


class SampleText(Frame):
    """
    Class that render a sample frame in the application.
    """

    def __init__(self):
        """
        Constructor of the class.
        """
        super().__init__()

    def render(self) -> None:
        """
        Render the main sample text.
        Returns: None
        """

        imgui.begin('Test Window')
        imgui.text("Test text to show in the frame.")
        imgui.bullet_text("This window accepts ballpoints and a lot more features")

        if imgui.button("Modal Pop-Up Menu"):
            imgui.open_popup("select-popup")

        imgui.same_line()

        if imgui.begin_popup_modal("select-popup")[0]:
            imgui.text("Select an option:")
            imgui.separator()
            imgui.selectable("One")
            imgui.selectable("Two")
            imgui.selectable("Three")
            imgui.end_popup()

        if self._fixed_position:
            imgui.set_window_position(0, 40)

        imgui.end()
