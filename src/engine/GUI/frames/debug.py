# BEGIN GPL LICENSE BLOCK
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# END GPL LICENSE BLOCK

"""
Sample frame for the application GUI.
"""
import os
from typing import TYPE_CHECKING

import imgui
import psutil

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

if TYPE_CHECKING:
    from engine.GUI.guimanager import GUIManager

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
        self.size = (300, 500)
        self.position = (
            self._GUI_manager.get_window_width() - self.size[0] - 200,
            self._GUI_manager.get_window_height() - self.size[1])

    def render(self) -> None:
        """
        Render the main sample text.
        Returns: None
        """
        zoom_level = self._GUI_manager.get_zoom_level()
        position = self._GUI_manager.get_map_position()
        view_mode = self._GUI_manager.get_program_view_mode()
        active_tool = self._GUI_manager.get_active_tool()
        active_polygon = self._GUI_manager.get_active_polygon_id()
        active_model = self._GUI_manager.get_active_model_id()
        loading = self._GUI_manager.is_program_loading()
        memory_usage_mb = (psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
        # cpu_percent = psutil.cpu_percent()

        self._begin_frame('Debug')
        imgui.text(f"Zoom level: {zoom_level}")
        imgui.text(f"Map position: {position}")
        imgui.separator()
        imgui.text(f"View mode: {view_mode}")
        imgui.separator()
        imgui.text(f"Active model: {active_model}")
        imgui.text(f"Active tool: {active_tool}")
        imgui.text(f"Active polygon: {active_polygon}")
        imgui.separator()
        imgui.text(f"Loading: {loading}")
        imgui.separator()
        imgui.text(f"RAM used: {memory_usage_mb} MB")
        # imgui.text(f"CPU usage: {cpu_percent} %")  # This value change a lot in short time

        imgui.separator()
        imgui.text_wrapped(f"List of polygons: {self._GUI_manager.get_polygon_id_list()}")
        imgui.text_wrapped(f"List of folders: {self._GUI_manager.get_polygon_folder_id_list()}")
        imgui.text_wrapped(f"List of models: {self._GUI_manager.get_model_list()}")
        imgui.text_wrapped(f"List of 3D models: {self._GUI_manager.get_3d_model_list()}")

        # if self._GUI_manager.are_frame_fixed():
        #     self.change_position([self.get_position()[0], self._GUI_manager.get_window_height() - self.__height])
        #     imgui.set_window_position(self.get_position()[0], self.get_position()[1])
        #     imgui.set_window_size(self.___width,
        #                           self.__height,
        #                           0)

        self._end_frame()
