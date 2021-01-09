"""
Sample frame for the application GUI.
"""

import imgui
import psutil
import os

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

log = get_logger(module="DEBUG_FRAME")


class Debug(Frame):
    """
    Class that render a sample frame in the application.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        super().__init__(gui_manager)
        self.___width = 300
        self.__height = 300

        self.change_position(
            [self._GUI_manager.get_window_width() - self.___width,
             self._GUI_manager.get_window_height() - self.__height])

    def render(self) -> None:
        """
        Render the main sample text.
        Returns: None
        """
        zoom_level = self._GUI_manager.get_zoom_level()
        position = self._GUI_manager.get_map_position()
        view_mode = self._GUI_manager.get_view_mode()
        active_tool = self._GUI_manager.get_active_tool()
        loading = self._GUI_manager.is_program_loading()
        memory_usage_mb = (psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
        # cpu_percent = psutil.cpu_percent()

        imgui.begin('Debug')
        imgui.text(f"Zoom level: {zoom_level}")
        imgui.text(f"Map position: {position}")
        imgui.separator()
        imgui.text(f"View mode: {view_mode}")
        imgui.separator()
        imgui.text(f"Active tool: {active_tool}")
        imgui.separator()
        imgui.text(f"Loading: {loading}")
        imgui.separator()
        imgui.text(f"RAM used: {memory_usage_mb} MB")
        # imgui.text(f"CPU usage: {cpu_percent} %")  # This value change a lot in short time (dont give useful infromation)

        if self._GUI_manager.are_frame_fixed():
            self.change_position([self.get_position()[0], self._GUI_manager.get_window_height() - self.__height])
            imgui.set_window_position(self.get_position()[0], self.get_position()[1])
            imgui.set_window_size(self.___width,
                                  self.__height,
                                  0)

        imgui.end()
