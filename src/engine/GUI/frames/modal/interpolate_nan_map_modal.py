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
from typing import TYPE_CHECKING

import imgui

from src.engine.GUI.frames.modal.modal import Modal
from src.engine.scene.map_transformation.interpolate_nan_map_transformation import InterpolateNanMapTransformation, \
    InterpolateNanMapTransformationType

if TYPE_CHECKING:
    from src.engine.GUI.guimanager import GUIManager


class InterpolateNanMapModal(Modal):
    """
    Class in charge of the rendering of the modal that gives options to interpolate the nan values of all the map.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        super().__init__(gui_manager)
        self.__modal_title: str = "Interpolate NaN values"
        self.size = (400, -1)
        self.__button_width: float = self.size[0] / 2 - 12

        # Types of interpolation
        # ----------------------
        self.__interpolation_type_options = ['Linear',
                                             'Nearest',
                                             'Cubic']
        self.__interpolation_type_values = [InterpolateNanMapTransformationType.linear,
                                            InterpolateNanMapTransformationType.nearest,
                                            InterpolateNanMapTransformationType.cubic]
        self.__interpolation_selected = 0

    def post_render(self) -> None:
        """
        Define and show the modal if the modal was set to show.

        Returns: None
        """
        if self._begin_modal(self.__modal_title):

            _, self.__interpolation_selected = imgui.combo('Type of interpolation',
                                                           self.__interpolation_selected,
                                                           self.__interpolation_type_options)

            if imgui.button("Close", self.__button_width):
                self._close_modal()

            imgui.same_line()
            if imgui.button("Interpolate", self.__button_width):
                map_transformation = InterpolateNanMapTransformation(
                    self._GUI_manager.get_active_model_id(),
                    self.__interpolation_type_values[self.__interpolation_selected])

                self._GUI_manager.apply_map_transformation(map_transformation)
                self._close_modal()

            imgui.end_popup()
