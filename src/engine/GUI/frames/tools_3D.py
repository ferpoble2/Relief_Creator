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
File with the class tools3D, class in charge of rendering the tools frame for the 3D apps.
"""

from typing import TYPE_CHECKING

import imgui

from src.engine.GUI.font import Font
from src.engine.GUI.frames.frame import Frame

if TYPE_CHECKING:
    from src.engine.GUI.guimanager import GUIManager


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
        self.position = (0, self._GUI_manager.get_main_menu_bar_height())
        self.__double_button_margin_width = 13
        self.__button_margin_width = 17

        self.__normalization_height_value = 0

        self.__heights_measure_units = ['Meters', 'Kilometers']
        self.__heights_measure_units_selected = 0

        self.__map_position_units = ['Degrees']
        self.__map_position_units_selected = 0

    def render(self) -> None:
        """
        Draw the components of the frame into the GUI.

        Returns: None
        """

        # Create the window on the screen depending on the mode selected on the program
        # -----------------------------------------------------------------------------
        self.size = (self._GUI_manager.get_left_frame_width(),
                     self._GUI_manager.get_window_height() - self._GUI_manager.get_main_menu_bar_height())
        self._begin_frame('Tools 3D')

        # ------------
        # Camera Tools
        # ------------

        # Add a title to the camera section
        self._GUI_manager.set_font(Font.TOOL_SUB_TITLE)
        imgui.text('Camera Information')
        self._GUI_manager.set_font(Font.REGULAR)

        # Get the camera data and show it in the frame
        camera_data = self._GUI_manager.get_camera_data()
        imgui.text(f'Elevation angle: {int(camera_data["elevation"])}°')
        imgui.text(f'Azimuthal angle: {int(camera_data["azimuthal"])}°')
        imgui.text(f'Radius: {camera_data["radius"]}')
        imgui.text(f'Position: {camera_data["position"]}')
        if imgui.button('Reset Camera', -1):
            self._GUI_manager.reset_camera_values()

        imgui.separator()

        # ----------
        # View Tools
        # ----------

        # Add a title to the view tools section
        self._GUI_manager.set_font(Font.TOOL_SUB_TITLE)
        imgui.text('View Tools')
        self._GUI_manager.set_font(Font.REGULAR)

        # Show the current exaggeration factor to the user and set an input section where the user can enter a new
        # value to use
        imgui.text('Elevation Exaggeration Factor')
        imgui.text(f'Current value: {self._GUI_manager.get_height_normalization_factor_of_active_3D_model()}')
        _, self.__normalization_height_value = imgui.input_float('New factor',
                                                                 self.__normalization_height_value,
                                                                 0,
                                                                 0,
                                                                 '%.0f')
        self.__normalization_height_value = max(self.__normalization_height_value, 0)

        # Disable the keyboard controller if the user is writing something on the GUI
        if imgui.is_item_active() and self._GUI_manager.get_controller_keyboard_callback_state():
            self._GUI_manager.set_controller_keyboard_callback_state(False)
        if (not imgui.is_item_active()) and (not self._GUI_manager.get_controller_keyboard_callback_state()):
            self._GUI_manager.set_controller_keyboard_callback_state(True)

        # Apply changes using the data written by the user in the options
        if imgui.button('Change Factor', -1):
            self._GUI_manager.change_current_3D_model_normalization_factor(self.__normalization_height_value)

        imgui.separator()

        # ----------
        # Unit Tools
        # ----------

        # Add a title to the unit tools section
        self._GUI_manager.set_font(Font.TOOL_SUB_TITLE)
        imgui.text('Unit Tools')
        self._GUI_manager.set_font(Font.REGULAR)

        # Render boxes where the user can select the measure unit of the maps and the heights
        imgui.text_wrapped('Height measure unit:')
        clicked, self.__heights_measure_units_selected = imgui.combo('',
                                                                     self.__heights_measure_units_selected,
                                                                     self.__heights_measure_units)
        imgui.text_wrapped('Map position measure unit:')
        clicked, self.__map_position_units_selected = imgui.combo(' ',
                                                                  self.__map_position_units_selected,
                                                                  self.__map_position_units)

        # Render a button where the user can update the information of the model
        if imgui.button('Update Model', -1):
            self._GUI_manager.change_height_unit_current_3D_model(
                self.__heights_measure_units[self.__heights_measure_units_selected]
            )
            self._GUI_manager.change_map_position_unit_current_3D_model(
                self.__map_position_units[self.__map_position_units_selected]
            )
            self._GUI_manager.update_current_3D_model()

        self._end_frame()
