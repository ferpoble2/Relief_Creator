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
Module in charge of the rendering of the modal that gives options to the user when merging two maps into one.
"""
from typing import List, TYPE_CHECKING

import imgui

from src.engine.GUI.frames.modal.modal import Modal
from src.engine.scene.map_transformation.merge_maps_transformation import MergeMapsTransformation

if TYPE_CHECKING:
    from src.engine.GUI.guimanager import GUIManager


class CombineMapModal(Modal):
    """
    Class in charge of the rendering of the modal that gives options to the user when merging two maps into a new one.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        super().__init__(gui_manager)
        self.__model_id_list: List[str] = []
        self.__model_name_list: List[str] = []

        self.size = (400, -1)
        self.__modal_title: str = "Merge maps"
        self.__button_width: float = self.size[0] / 2 - 12

        self.__selected_map_1: int = 0
        self.__selected_map_2: int = 0

    def open_modal(self) -> None:
        """
        Execute the logic to initialize the frame when opening it.

        Returns: None
        """
        super().open_modal()

        # Get the information of the maps
        self.__model_id_list = list(self._GUI_manager.get_model_names_dict().keys())
        self.__model_name_list = list(self._GUI_manager.get_model_names_dict().values())

        # Configure the options selected in the frame
        self.__selected_map_1 = 0
        self.__selected_map_2 = 0

    def post_render(self) -> None:
        """
        Define and show the modal if the modal was set to show.

        Returns: None
        """
        if self._begin_modal(self.__modal_title):
            imgui.text("Select the maps to merge:")
            _, self.__selected_map_1 = imgui.combo("Base model", self.__selected_map_1, self.__model_name_list)
            _, self.__selected_map_2 = imgui.combo("Secondary model", self.__selected_map_2, self.__model_name_list)

            if imgui.button("Close", self.__button_width):
                self._GUI_manager.set_controller_keyboard_callback_state(True)
                imgui.close_current_popup()

            imgui.same_line()
            if imgui.button("Merge Maps", self.__button_width):
                map_transformation = MergeMapsTransformation(self.__model_id_list[self.__selected_map_1],
                                                             self.__model_id_list[self.__selected_map_2])
                self._GUI_manager.apply_map_transformation(map_transformation)
                self._close_modal()

            imgui.end_popup()
