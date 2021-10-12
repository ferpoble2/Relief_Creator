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
from typing import TYPE_CHECKING

import imgui

from src.engine.GUI.frames.frame import Frame
from src.engine.GUI.frames.tools.interpolation_tools import InterpolationTools
from src.engine.GUI.frames.tools.map_tools import MapTools
from src.engine.GUI.frames.tools.polygon_tools import PolygonTools
from src.engine.GUI.frames.tools.relief_tools import ReliefTools
from src.program.tools import Tools as ProgramTools
from src.utils import get_logger

if TYPE_CHECKING:
    from engine.GUI.guimanager import GUIManager

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
        self.position = (0, self._GUI_manager.get_main_menu_bar_height())

        self.__double_button_margin_width = 13
        self.__button_margin_width = 17
        self.__slide_bar_quality = self._GUI_manager.get_quality()

        self.__tools_names_dict = {
            ProgramTools.move_map: 'Move Map',
            ProgramTools.create_polygon: 'Create Polygon'
        }

        # Generate the objects in charge of rendering the information of the different tools
        # ----------------------------------------------------------------------------------
        self.__relief_tools = ReliefTools(gui_manager)
        self.__polygon_tools = PolygonTools(gui_manager, self.__button_margin_width)
        self.__interpolation_tools = InterpolationTools(gui_manager)
        self.__map_tools = MapTools(gui_manager)

    def __show_active_tool(self):
        """
        Show the active tool in a formatted way to the user.
        """
        self._GUI_manager.set_bold_font()
        imgui.text(f"Active tool: {self.__tools_names_dict.get(self._GUI_manager.get_active_tool(), None)}")
        self._GUI_manager.set_regular_font()

    def __show_visualization_tools(self) -> None:
        """
        Show the visualization tools on the frame.
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
            self._GUI_manager.set_active_tool(ProgramTools.move_map)

        if imgui.button("Reload Map", -1):
            log.debug("Pressed Reload map with zoom button")
            log.debug("-----------------------------------")
            self._GUI_manager.reload_models()

        changed, values = imgui.slider_int("Quality", self.__slide_bar_quality, 1, 30)
        if changed:
            log.debug("Changed slide bar quality")
            log.debug("------------------------")
            log.debug(f"Changed to value {values}")
            self.__slide_bar_quality = values
            self._GUI_manager.change_map_quality(values)

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

        # Create the frame with the correct size
        # --------------------------------------
        self.size = (self._GUI_manager.get_left_frame_width(),
                     self._GUI_manager.get_window_height() - self._GUI_manager.get_main_menu_bar_height())
        self._begin_frame('Tools')

        # Show the active tool on the application
        # ---------------------------------------
        self.__show_active_tool()

        # Show the different tools of the application
        # -------------------------------------------
        imgui.separator()
        self.__show_visualization_tools()

        imgui.separator()
        self.__polygon_tools.render()

        # Show relief and interpolation tools only if there is an active polygon on the program
        if self._GUI_manager.get_active_polygon_id() is not None:
            imgui.separator()
            self.__relief_tools.render()

            imgui.separator()
            self.__interpolation_tools.render()

        imgui.separator()
        self.__map_tools.render()

        self._end_frame()
