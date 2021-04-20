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

        self.__normalization_height_value = 0

        self.__heights_measure_units = ['Meters', 'Kilometers']
        self.__heights_measure_units_selected = 0

        self.__map_position_units = ['Degrees', 'UTM']
        self.__map_position_units_selected = 0

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

        self._GUI_manager.set_tool_title_font()
        imgui.text('Camera Information')
        self._GUI_manager.set_regular_font()

        camera_data = self._GUI_manager.get_camera_data()

        imgui.text(f'Elevation angle: {int(camera_data["elevation"])}°')
        imgui.text(f'Azimuthal angle: {int(camera_data["azimuthal"])}°')
        imgui.text(f'Radius: {camera_data["radius"]}')
        imgui.text(f'Position: {camera_data["position"]}')

        if imgui.button('Reset Camera', -1):
            self._GUI_manager.reset_camera_values()

        imgui.separator()

        self._GUI_manager.set_tool_title_font()
        imgui.text('View Tools')
        self._GUI_manager.set_regular_font()

        imgui.text('Elevation Exaggeration Factor')
        imgui.text(f'Current value: {self._GUI_manager.get_height_normalization_factor_of_active_3D_model()}')
        _, self.__normalization_height_value = imgui.input_float('New factor',
                                                                 self.__normalization_height_value,
                                                                 format='%.6f')
        self.__normalization_height_value = max(self.__normalization_height_value, 0)

        # Deprecated tooltip
        # ------------------
        # # show tooltip when mouse is hover
        # if imgui.is_item_hovered():
        #     imgui.begin_tooltip()
        #     imgui.text('Models usually use different units for the height and for the position of the points.\n\n'
        #                'Change this value to modify the factor used to normalize the height coordinates.')
        #     imgui.end_tooltip()

        # disable input if writing a value on the input
        if imgui.is_item_active():
            self._GUI_manager.disable_glfw_keyboard_callback()
        else:
            self._GUI_manager.enable_glfw_keyboard_callback()

        # apply changes
        if imgui.button('Change Factor', -1):
            self._GUI_manager.change_current_3D_model_normalization_factor(self.__normalization_height_value)

        imgui.separator()
        self._GUI_manager.set_tool_title_font()
        imgui.text('Unit Tools')
        self._GUI_manager.set_regular_font()

        imgui.text_wrapped('Height measure unit:')
        clicked, self.__heights_measure_units_selected = imgui.combo('',
                                                                     self.__heights_measure_units_selected,
                                                                     self.__heights_measure_units)

        imgui.text_wrapped('Map position measure unit:')
        clicked, self.__map_position_units_selected = imgui.combo(' ',
                                                                  self.__map_position_units_selected,
                                                                  self.__map_position_units)

        if imgui.button('Update Model', -1):
            self._GUI_manager.change_height_unit_current_3D_model(
                self.__heights_measure_units[self.__heights_measure_units_selected]
            )
            self._GUI_manager.change_map_position_unit_current_3D_model(
                self.__map_position_units[self.__map_position_units_selected]
            )
            self._GUI_manager.update_current_3D_model()

        imgui.end()
