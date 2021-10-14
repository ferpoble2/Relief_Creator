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
File with the definition of the ConvolveNanModal, modal in charge of setting the parameters and apply a
NanConvolutionMapTransformation.
"""
from typing import TYPE_CHECKING

import imgui

from src.engine.GUI.frames.modal.modal import Modal
from src.engine.scene.map_transformation.nan_convolution import NanConvolutionMapTransformation

if TYPE_CHECKING:
    from src.engine.GUI.guimanager import GUIManager


class ConvolveNanModal(Modal):
    """
    Class in charge of setting the parameters and apply a NanConvolutionMapTransformation over the active model.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """Constructor of the class."""
        super().__init__(gui_manager)
        self.__button_width = self.size[0] / 2 - 12

        self.__nan_percentage_limit = 0
        self.__kernel_size_selected = 3

    def post_render(self) -> None:
        """
        Render the modal on the program if it is set to be showed.

        Returns: None
        """

        if self._begin_modal('Eliminate values surrounded by NaN'):

            # Input for the percentage of nan that should be surrounding the value to delete it
            # ---------------------------------------------------------------------------------
            imgui.push_item_width(50)
            _, self.__nan_percentage_limit = imgui.input_float('% of NaN surrounding the values.',
                                                               self.__nan_percentage_limit)
            self.__nan_percentage_limit = 0 if self.__nan_percentage_limit < 0 else self.__nan_percentage_limit
            self.__nan_percentage_limit = 100 if self.__nan_percentage_limit > 100 else self.__nan_percentage_limit
            imgui.pop_item_width()

            # Input for the size of the kernel to use
            # ---------------------------------------
            imgui.push_item_width(100)
            _, self.__kernel_size_selected = imgui.input_int('Distance to analyze from point.',
                                                             self.__kernel_size_selected)
            self.__kernel_size_selected = 3 if self.__kernel_size_selected < 3 else self.__kernel_size_selected
            imgui.pop_item_width()

            # Buttons to close or to apply the transformation
            # -----------------------------------------------
            if imgui.button('Close', self.__button_width):
                self._close_modal()

            imgui.same_line()
            if imgui.button('Interpolate', self.__button_width):
                map_transformation = NanConvolutionMapTransformation(self._GUI_manager.get_active_model_id(),
                                                                     self.__kernel_size_selected,
                                                                     float(self.__nan_percentage_limit) / 100)
                self._GUI_manager.apply_map_transformation(map_transformation)
                self._close_modal()

            imgui.end_popup()
