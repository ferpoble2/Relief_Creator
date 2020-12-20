"""
Sample frame for the application GUI.
"""

import imgui

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

log = get_logger(module="SAMPLE TEXT")


class Debug(Frame):
    """
    Class that render a sample frame in the application.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        super().__init__(gui_manager)
        self.__height = 300

        self.change_position(
            [self._GUI_manager.get_left_frame_width(), self._GUI_manager.get_window_height() - self.__height])

    def render(self) -> None:
        """
        Render the main sample text.
        Returns: None
        """
        zoom_level = self._GUI_manager.get_zoom_level()
        position = self._GUI_manager.get_map_position()
        view_mode = self._GUI_manager.get_view_mode()
        active_tool = self._GUI_manager.get_active_tool()

        imgui.begin('Debug')
        imgui.text(f"Zoom level: {zoom_level}")
        imgui.text(f"Map position: {position}")
        imgui.text(f"View mode: {view_mode}")
        imgui.text(f"Active tool: {active_tool}")

        if self._GUI_manager.are_frame_fixed():
            self.change_position([self.get_position()[0], self._GUI_manager.get_window_height() - self.__height])
            imgui.set_window_position(self.get_position()[0], self.get_position()[1])
            imgui.set_window_size(self._GUI_manager.get_window_width() - self._GUI_manager.get_left_frame_width(),
                                  self.__height,
                                  0)

        imgui.end()
