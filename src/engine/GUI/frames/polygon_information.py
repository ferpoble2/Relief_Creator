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
        # Do not draw the screen if there is no active polygon.
        if self._GUI_manager.get_active_polygon_id() is not None:

            # set the flags if the windows should be collapsable or not
            if self._GUI_manager.are_frame_fixed():
                imgui.begin('Polygon Information', False,
                            imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE)
                self.change_position([self._GUI_manager.get_window_width() - self.__width,
                                      self._GUI_manager.get_window_height() - self.__height])
                imgui.set_window_position(self.get_position()[0], self.get_position()[1])
                imgui.set_window_size(self.__width, self.__height, 0)

            else:
                imgui.begin('Polygon Information')

            imgui.columns(2, 'Data List')
            imgui.separator()
            imgui.text("Field Name")
            imgui.next_column()
            imgui.text("Value")
            imgui.separator()

            for parameter in self._GUI_manager.get_polygon_parameters(self._GUI_manager.get_active_polygon_id()):
                imgui.next_column()
                imgui.text(parameter[0])
                imgui.next_column()
                imgui.text(parameter[1])
                imgui.separator()

            imgui.columns(1)

            imgui.end()
