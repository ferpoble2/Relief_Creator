#  BEGIN GPL LICENSE BLOCK
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  END GPL LICENSE BLOCK

"""
Module in charge of the rendering of the modal that gives options to interpolate the nan values of the full map.
"""
from typing import TYPE_CHECKING, Union

import imgui

from src.engine.GUI.frames.frame import Frame
from src.engine.scene.map_transformation.interpolate_nan_map_transformation import InterpolateNanMapTransformation, \
    InterpolateNanMapTransformationType

if TYPE_CHECKING:
    from src.engine.GUI.guimanager import GUIManager


class InterpolateNanMapModal(Frame):
    """
    Class in charge of the rendering of the modal that gives options to interpolate the nan values of all the map.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        super().__init__(gui_manager)
        self.__should_show_frame: bool = False

        self.__modal_title: str = "Interpolate NaN values"
        self.__modal_width: float = 400
        self.__button_width: float = self.__modal_width / 2 - 12

        self.__tool_before_opening_modal: Union[str, None] = None

        # Types of interpolation
        # ----------------------
        self.__interpolation_type_options = ['Linear',
                                             'Nearest',
                                             'Cubic']
        self.__interpolation_type_values = [InterpolateNanMapTransformationType.linear,
                                            InterpolateNanMapTransformationType.nearest,
                                            InterpolateNanMapTransformationType.cubic]
        self.__interpolation_selected = 0

    @property
    def should_show(self) -> bool:
        """
        Get a boolean indicating if the frame will show when rendering.

        Returns: should_show property of the frame.
        """
        return self.__should_show_frame

    @should_show.setter
    def should_show(self, value: bool) -> None:
        """
        Setter for the should_show property.

        Returns: None
        """
        self.__should_show_frame = value

    def render(self) -> None:
        """
        Do nothing since the frame should not be rendered in each frame.

        Returns: None
        """
        pass

    def post_render(self) -> None:
        """
        Define and show the modal if the modal was set to show.

        Returns: None
        """
        imgui.set_next_window_size(self.__modal_width, -1)
        imgui.set_next_window_position(imgui.get_io().display_size.x * 0.5,
                                       imgui.get_io().display_size.y * 0.5,
                                       imgui.ALWAYS,
                                       0.5,
                                       0.5)
        if self.__should_show_frame:
            self.__tool_before_opening_modal = self._GUI_manager.get_active_tool()
            self._GUI_manager.set_active_tool(None)

            imgui.open_popup(self.__modal_title)
            self._GUI_manager.set_controller_keyboard_callback_state(False)
            self.__should_show_frame = False

        if imgui.begin_popup_modal(self.__modal_title)[0]:

            _, self.__interpolation_selected = imgui.combo('Type of interpolation',
                                                           self.__interpolation_selected,
                                                           self.__interpolation_type_options)

            if imgui.button("Close", self.__button_width):
                self._GUI_manager.set_controller_keyboard_callback_state(True)
                imgui.close_current_popup()

            imgui.same_line()
            if imgui.button("Interpolate", self.__button_width):
                map_transformation = InterpolateNanMapTransformation(
                    self._GUI_manager.get_active_model_id(),
                    self.__interpolation_type_values[self.__interpolation_selected])

                self._GUI_manager.apply_map_transformation(map_transformation)
                self._GUI_manager.set_controller_keyboard_callback_state(True)
                imgui.close_current_popup()

            imgui.end_popup()
