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
Module that define the MapTools class. Class in charge of showing the loaded maps on the GUI.
"""
from typing import TYPE_CHECKING

import imgui

from src.engine.GUI.font import Font

if TYPE_CHECKING:
    from src.engine.GUI.guimanager import GUIManager


class MapTools:
    """
    Class in charge of showing the maps on the Tools frame of the GUI.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.

        Args:
            gui_manager: GUIManager of the application.
        """
        self.__gui_manager = gui_manager

    def render(self) -> None:
        """
        Render the information of the maps.

        This method should be called by another frame to render the information of the maps inside that frame.

        Examples:
            imgui.begin(...)
            ...
            map_tool.render()
            ...
            imgui.end()

        Returns: Render the information of the maps inside some frame.
        """

        # Render title of the tools
        # -------------------------
        self.__gui_manager.set_font(Font.TOOL_TITLE)
        imgui.text('Map Tools')
        self.__gui_manager.set_font(Font.REGULAR)

        # Render maps names
        # -----------------
        model_name_dict = self.__gui_manager.get_model_names_dict()
        active_model_id = self.__gui_manager.get_active_model_id()

        for key, value in model_name_dict.items():

            # Render the checkbox for the model
            clicked, current_state = imgui.checkbox(value,
                                                    True if active_model_id == key else False)
            if imgui.is_item_clicked(1):
                imgui.open_popup(f'popup_model_{key}')

            # Set the model as active if checkbox is clicked
            if clicked:
                self.__gui_manager.set_active_model(key)

        # Set the logic for the popups
        # ----------------------------
        self.popup_logic()

    def popup_logic(self) -> None:
        """
        Render the popup for each model.

        The id of the popup to open is as follows: popup_model_{model_id}, where {model_id} is the id of the model
        selected.

        Returns: None
        """
        model_id_list = self.__gui_manager.get_model_list()

        for model_id in model_id_list:
            if imgui.begin_popup(f'popup_model_{model_id}'):
                imgui.text("Select an action")
                imgui.separator()

                # Move up the map
                # ---------------
                imgui.selectable("Move up")
                if imgui.is_item_clicked():
                    self.__gui_manager.move_model_position(str(model_id), -1)

                # Move down the map
                # -----------------
                imgui.selectable("Move down")
                if imgui.is_item_clicked():
                    self.__gui_manager.move_model_position(str(model_id), 1)

                # Delete the map
                # --------------
                imgui.separator()
                imgui.selectable("Delete")
                if imgui.is_item_clicked():
                    self.__gui_manager.remove_model(model_id)

                imgui.end_popup()
