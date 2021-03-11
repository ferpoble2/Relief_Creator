"""
Frame that indicate the parameters of the polygons
"""

import imgui
import psutil
import os

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

log = get_logger(module="Polygon Information")


class PolygonInformation(Frame):
    """
    Class that render a frame to store the parameters of the active polygon.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        super().__init__(gui_manager)

    def render(self) -> None:
        """
        Render the frame.
        Returns: None
        """
        imgui.begin('Polygon Information')

        imgui.columns(2, 'Data List')
        imgui.separator()
        imgui.text("Field Name")
        imgui.next_column()
        imgui.text("Value")
        imgui.separator()

        imgui.next_column()
        imgui.text("Sample_name")
        imgui.next_column()
        imgui.text("some_text")
        imgui.separator()

        imgui.columns(1)
        imgui.end()
