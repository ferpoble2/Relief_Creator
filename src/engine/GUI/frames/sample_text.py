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

        imgui.begin('test_text')
        imgui.text("This is a sample text to show iin the guy to test screens.")
        imgui.bullet_text("This is a bullet text, hope it helps.")

        if imgui.button("Open Modal popup"):
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
