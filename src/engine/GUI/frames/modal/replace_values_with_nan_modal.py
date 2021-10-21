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
Modal to use to set the parameters to apply the ReplaceNanValuesInMap transformation.
"""
from typing import List, TYPE_CHECKING

import imgui

from src.engine.GUI.frames.modal.modal import Modal
from src.engine.scene.map_transformation.replace_nan_values_in_map import ReplaceNanValuesInMap

if TYPE_CHECKING:
    from src.engine.GUI.guimanager import GUIManager


class ReplaceValuesWithNanModal(Modal):
    """
    Modal in charge of the application of the ReplaceNanValuesInMap map transformation.

    This modal set the parameters for the transformation and apply it to the selected map.
    """

    def __init__(self, gui_manager: 'GUIManager',
                 model_id_list: List[str],
                 model_name_list: List[str]):
        super().__init__(gui_manager)
        self.size = (400, -1)
        self.__button_width: float = self.size[0] / 2 - 12

        self.__model_id_list = model_id_list
        self.__model_name_list = model_name_list
        self.__selected_model_primary = 0
        self.__selected_model_secondary = 0

    def post_render(self) -> None:
        """
        Draw the frame on the program.

        Returns: None
        """

        if self._begin_modal('Replace values with nan'):
            imgui.text_wrapped("Select a base model to modify and a second model to use to select the values. The "
                               "values of the height of the base model will be set to NaN in the place where the "
                               "second model has values defined.\n\n")
            imgui.text_wrapped("Select the maps to use in the transformation:")
            _, self.__selected_model_primary = imgui.combo("Base model", self.__selected_model_primary,
                                                           self.__model_name_list)
            _, self.__selected_model_secondary = imgui.combo("Secondary model", self.__selected_model_secondary,
                                                             self.__model_name_list)

            if imgui.button("Close", self.__button_width):
                self._close_modal()

            imgui.same_line()
            if imgui.button("Replace values", self.__button_width):
                map_transformation = ReplaceNanValuesInMap(self.__model_id_list[self.__selected_model_primary],
                                                           self.__model_id_list[self.__selected_model_secondary])
                self._GUI_manager.apply_map_transformation(map_transformation)
                self._close_modal()

            imgui.end_popup()
