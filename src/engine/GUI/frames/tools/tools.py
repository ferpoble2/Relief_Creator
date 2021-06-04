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

import imgui

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

from src.engine.GUI.frames.tools.relief_tools import ReliefTools
from src.engine.GUI.frames.tools.polygon_tools import PolygonTools
from src.engine.GUI.frames.tools.interpolation_tools import InterpolationTools

log = get_logger(module="TOOLS")


class Tools(Frame):
    """
    Class that render a sample frame in the application.
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        super().__init__(gui_manager)
        self.change_position([0, self._GUI_manager.get_main_menu_bar_height()])
        self.__double_button_margin_width = 13
        self.__button_margin_width = 17
        self.__slide_bar_quality = self._GUI_manager.get_quality()

        self.__tools_names_dict = {
            'move_map': 'Move Map',
            'create_polygon': 'Create Polygon'
        }

        # object in charge of render the relief tools
        self.__relief_tools = ReliefTools(gui_manager)
        self.__polygon_tools = PolygonTools(gui_manager, self.__button_margin_width)
        self.__interpolation_tools = InterpolationTools(gui_manager)

    def __show_active_tool(self):
        """
        Show the active tool in a formatted way to the user.
        """
        self._GUI_manager.set_bold_font()
        imgui.text(f"Active tool: {self.__tools_names_dict.get(self._GUI_manager.get_active_tool(), None)}")
        self._GUI_manager.set_regular_font()

    def __show_visualization_tools(self, left_frame_width: int) -> None:
        """
        Show the visualization tools on the frame.

        Args:
            left_frame_width: width of the frame.
        """
        self._GUI_manager.set_tool_title_font()
        imgui.text("Visualization Tools")
        self._GUI_manager.set_regular_font()

        if imgui.button("Zoom In", width=imgui.get_window_width() / 2 - self.__double_button_margin_width):
            log.debug("Pressed button Zoom in")
            log.debug("----------------------")
            self._GUI_manager.add_zoom()

        imgui.same_line()
        if imgui.button("Zoom Out", width=imgui.get_window_width() / 2 - self.__double_button_margin_width):
            log.debug("Pressed button Zoom out")
            log.debug("-----------------------")
            self._GUI_manager.less_zoom()

        if imgui.button("Move Map", -1):
            log.debug("Pressed button Move Map")
            log.debug("-----------------------")
            self._GUI_manager.set_active_tool('move_map')

        if imgui.button("Reload Map", -1):
            log.debug("Pressed Reload map with zoom button")
            log.debug("-----------------------------------")
            self._GUI_manager.reload_models()

        # if imgui.button("Optimize GPU memory", width=left_frame_width - self.__button_margin_width):
        #     log.debug("Optimize GPU memory button pressed")
        #     self._GUI_manager.optimize_gpu_memory()

        changed, values = imgui.slider_int("Quality", self.__slide_bar_quality, 1, 30)
        if changed:
            log.debug("Changed slide bar quality")
            log.debug("------------------------")
            log.debug(f"Changed to value {values}")
            self.__slide_bar_quality = values
            self._GUI_manager.change_quality(values)

    def add_new_polygon(self, polygon_id: str) -> None:
        """
        Add a polygon (externally generated, already existent in the program) to the GUI.
        Polygon must be already in some folder.

        Args:
            polygon_id: Id of the polygon externally generated.

        Returns: None
        """
        self.__polygon_tools.add_new_polygon(polygon_id)

    def render(self) -> None:
        """
        Render the main sample text.
        Returns: None
        """

        if self._GUI_manager.are_frame_fixed():
            imgui.begin('Tools', False, imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE)
            imgui.set_window_position(self.get_position()[0], self.get_position()[1])
            imgui.set_window_size(self._GUI_manager.get_left_frame_width(),
                                  self._GUI_manager.get_window_height() - self._GUI_manager.get_main_menu_bar_height(),
                                  0)
        else:
            imgui.begin('Tools')

        self.__show_active_tool()

        left_frame_width = self._GUI_manager.get_left_frame_width()

        imgui.separator()
        self.__show_visualization_tools(left_frame_width)

        imgui.separator()
        self.__polygon_tools.render(left_frame_width)

        if self._GUI_manager.get_active_polygon_id() is not None:
            imgui.separator()
            self.__relief_tools.render()

            imgui.separator()
            self.__interpolation_tools.render()

        imgui.end()
