"""
File with the class tools3D, class in charge of rendering the tools frame for the 3D apps.
"""

import imgui

from src.type_hinting import *
from src.engine.GUI.frames.frame import Frame


class Tools3D(Frame):
    """
    Class in charge of rendering the tools for the 3D visualizations.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.

        Args:
            gui_manager: Guimanager who uses the frame.
        """
        super().__init__(gui_manager)
        self.change_position([0, self._GUI_manager.get_main_menu_bar_height()])
        self.__double_button_margin_width = 13
        self.__button_margin_width = 17

    def render(self) -> None:
        """
        Draw the components of the frame into the GUI.

        Returns: None
        """
        if self._GUI_manager.are_frame_fixed():
            imgui.begin('Tools 3D', False, imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE)
            imgui.set_window_position(self.get_position()[0], self.get_position()[1])
            imgui.set_window_size(self._GUI_manager.get_left_frame_width(),
                                  self._GUI_manager.get_window_height() - self._GUI_manager.get_main_menu_bar_height(),
                                  0)
        else:
            imgui.begin('Tools 3D')

        imgui.text('Tools 3D')
        imgui.end()
