"""
Sample frame for the application GUI.
"""

import imgui

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

log = get_logger(module="TOOLS")


class Tools(Frame):
    """
    Class that render a sample frame in the application.
    """

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

    def generate_polygon_list(self) -> None:
        """
        Generate the list of polygons to show to the user.

        Returns: None
        """

        list_polygons = self._GUI_manager.get_polygon_list()
        active_polygon = self._GUI_manager.get_active_polygon_id()

        for polygon in list_polygons:
            polygon_id = polygon.get_id()
            clicked, current_state = imgui.checkbox(polygon_id, True if polygon_id == active_polygon else False)

            if clicked:
                # Change the active polygon to the clicked one
                self._GUI_manager.set_active_polygon(polygon_id)

                # Activate the create_polygon tool when clicked the polygon
                self._GUI_manager.set_active_tool('create_polygon')

    def render(self) -> None:
        """
        Render the main sample text.
        Returns: None
        """

        imgui.begin('Tools')
        self.show_active_tool()

        left_frame_width = self._GUI_manager.get_left_frame_width()

        imgui.separator()
        self.show_visualization_tools(left_frame_width)

        imgui.separator()
        self.show_editing_tools(left_frame_width)

        imgui.separator()
        self.show_polygon_tools(left_frame_width)

        imgui.separator()
        self.show_other_tools(left_frame_width)

        if self._GUI_manager.are_frame_fixed():
            imgui.set_window_position(self.get_position()[0], self.get_position()[1])
            imgui.set_window_size(self._GUI_manager.get_left_frame_width(),
                                  self._GUI_manager.get_window_height() - self._GUI_manager.get_main_menu_bar_height(),
                                  0)

        imgui.end()

    def show_active_tool(self):
        """
        Show the active tool in a formatted way to the user.
        """
        self._GUI_manager.set_bold_font()
        imgui.text(f"Active tool: {self.__tools_names_dict.get(self._GUI_manager.get_active_tool(), None)}")
        self._GUI_manager.set_regular_font()

    def show_editing_tools(self, left_frame_width: int) -> None:
        """
        Show the editing tools on the frame.

        Args:
            left_frame_width: width of the frame.
        """
        imgui.text("Editing Tools")
        if imgui.button("Move Map", width=left_frame_width - self.__button_margin_width):
            log.debug("Pressed button Move Map")
            log.debug("-----------------------")
            self._GUI_manager.set_active_tool('move_map')

    def show_other_tools(self, left_frame_width: int) -> None:
        """
        Show the other tools buttons on the frame.

        Args:
            left_frame_width: width of the frame.
        """
        imgui.text("Other tools")
        if imgui.button("Optimize GPU memory", width=left_frame_width - self.__button_margin_width):
            log.debug("Optimize GPU memory button pressed")
            self._GUI_manager.optimize_gpu_memory()
        if imgui.button("Modal Pop-Up Menu", width=left_frame_width - self.__button_margin_width):
            self._GUI_manager.set_modal_text("This is a modal", "A very good modal")

    def show_polygon_tools(self, left_frame_width: int) -> None:
        """
        Show the polygon tools on the frame

        Args:
            left_frame_width: width of the frame.
        """
        imgui.text("Polygon Tools")
        if imgui.button("Create polygon", width=left_frame_width - self.__button_margin_width):
            log.debug(f"Pressed button create polygon")
            log.debug("------------------------------")
            self._GUI_manager.set_active_tool('create_polygon')
        self.generate_polygon_list()

    def show_visualization_tools(self, left_frame_width: int) -> None:
        """
        Show the visualization tools on the frame.

        Args:
            left_frame_width: width of the frame.
        """
        imgui.text("Visualization Tools")
        if imgui.button("Zoom in", width=left_frame_width / 2 - self.__double_button_margin_width):
            log.debug("Pressed button Zoom in")
            log.debug("----------------------")
            self._GUI_manager.add_zoom()
        imgui.same_line()
        if imgui.button("Zoom out", width=left_frame_width / 2 - self.__double_button_margin_width):
            log.debug("Pressed button Zoom out")
            log.debug("-----------------------")
            self._GUI_manager.less_zoom()
        if imgui.button("Reload map with zoom", width=left_frame_width - self.__button_margin_width):
            log.debug("Pressed Reload map with zoom button")
            log.debug("-----------------------------------")
            self._GUI_manager.reload_models()
        changed, values = imgui.slider_int("Quality", self.__slide_bar_quality, 1, 30)
        if changed:
            log.debug("Changed slidebar quality")
            log.debug("------------------------")
            log.debug(f"Changed to value {values}")
            self.__slide_bar_quality = values
            self._GUI_manager.change_quality(values)
