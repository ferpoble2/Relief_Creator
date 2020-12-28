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
        self.double_button_margin_width = 13
        self.button_margin_width = 17
        self.slide_bar_quality = 3

    def render(self) -> None:
        """
        Render the main sample text.
        Returns: None
        """

        imgui.begin('Tools')

        left_frame_width = self._GUI_manager.get_left_frame_width()

        imgui.text("Visualization Tools")
        if imgui.button("Zoom in", width=left_frame_width / 2 - self.double_button_margin_width):
            log.debug("Pressed button Zoom in")
            log.debug("----------------------")
            self._GUI_manager.add_zoom()

        imgui.same_line()
        if imgui.button("Zoom out", width=left_frame_width / 2 - self.double_button_margin_width):
            log.debug("Pressed button Zoom out")
            log.debug("-----------------------")
            self._GUI_manager.less_zoom()

        if imgui.button("Reload map with zoom", width=left_frame_width - self.button_margin_width):
            log.debug("Pressed Reload map with zoom button")
            log.debug("-----------------------------------")
            self._GUI_manager.reload_models()

        changed, values = imgui.slider_int("Quality", self.slide_bar_quality, 1, 30)
        if changed:
            log.debug("Changed slidebar quality")
            log.debug("------------------------")
            log.debug(f"Changed to value {values}")
            self.slide_bar_quality = values
            self._GUI_manager.change_quality(values)

        imgui.separator()
        imgui.text("Editing Tools")
        if imgui.button("Move Map", width=left_frame_width - self.button_margin_width):
            log.debug("Pressed button Move Map")
            log.debug("-----------------------")

        imgui.separator()
        imgui.text("Polygon Tools")
        if imgui.button("Create polygon", width=left_frame_width - self.button_margin_width):
            log.debug(f"Pressed button create polygon")
            log.debug("------------------------------")

        imgui.separator()
        imgui.text("Other tools")
        if imgui.button("Modal Pop-Up Menu", width=left_frame_width - self.button_margin_width):
            imgui.open_popup("select-popup")

        imgui.same_line()

        if imgui.begin_popup_modal("select-popup")[0]:
            imgui.text("Select an option:")
            imgui.separator()
            imgui.selectable("One")
            imgui.selectable("Two")
            imgui.selectable("Three")
            imgui.end_popup()

        if self._GUI_manager.are_frame_fixed():
            imgui.set_window_position(self.get_position()[0], self.get_position()[1])
            imgui.set_window_size(self._GUI_manager.get_left_frame_width(),
                                  self._GUI_manager.get_window_height() - self._GUI_manager.get_main_menu_bar_height(),
                                  0)

        imgui.end()
