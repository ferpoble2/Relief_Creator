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
        self.__height = 300
        self.__width = 200

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

        if self._GUI_manager.are_frame_fixed():
            self.change_position([self._GUI_manager.get_window_width() - self.__width,
                                  self._GUI_manager.get_window_height() - self.__height])
            imgui.set_window_position(self.get_position()[0], self.get_position()[1])
            imgui.set_window_size(self.__width,
                                  self.__height,
                                  0)

        imgui.end()
