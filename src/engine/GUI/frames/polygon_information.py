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
Frame that indicate the parameters of the polygons.

Frame contains tuples with the name and values of the parameters of the polygon that will be stored in the
shapefile file if they are exported.
"""

from typing import TYPE_CHECKING

import imgui

from engine.GUI.frames.modal.polygon_parameter_modal import PolygonParameterModal
from src.engine.GUI.font import Font
from src.engine.GUI.frames.frame import Frame
from src.engine.GUI.frames.modal.confirmation_modal import ConfirmationModal
from src.utils import get_logger

if TYPE_CHECKING:
    from engine.GUI.guimanager import GUIManager
log = get_logger(module="Polygon Information")


class PolygonInformation(Frame):
    """
    Class that render a frame to store the parameters of the active polygon.

    Frame is fixed on the bottom-right corner when fixed, and shows a table with the name and value
    of the parameters stored in the polygon.
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.

        Args:
            gui_manager (src.engine.GUI.GUIManager):
        """
        super().__init__(gui_manager)
        self.size = (300, 300)

    def render(self) -> None:
        """
        Render the frame.

        Do not render anything if there is not an active polygon on the application.

        Returns: None
        """

        # Do not draw the screen if there is no active polygon.
        if self._GUI_manager.get_active_polygon_id() is not None:

            # -----------
            # Begin frame
            # -----------
            self.position = (self._GUI_manager.get_window_width() - self.size[0],
                             self._GUI_manager.get_window_height() - self.size[1])
            self._begin_frame('Polygon Information')

            # --------------------------------------------
            # First row, show the data titles in bold font
            # --------------------------------------------
            self._GUI_manager.set_font(Font.BOLD)
            imgui.columns(2, 'Data List')
            imgui.separator()
            imgui.text("Field Name")
            imgui.next_column()
            imgui.text("Value")
            imgui.separator()
            self._GUI_manager.set_font(Font.REGULAR)

            # ---------------------------------------------------------------------------------------------------------
            # For each parameter defined in the polygon, show a new row on the frame with the name of the parameter and
            # the value stored in the parameter. Also, configure the popup modal that will open in case that the
            # parameter is clicked.
            # ---------------------------------------------------------------------------------------------------------
            for parameter in self._GUI_manager.get_polygon_parameters(self._GUI_manager.get_active_polygon_id()):

                # Render the key of the parameter
                imgui.next_column()
                imgui.text(parameter[0])
                if imgui.is_item_hovered() and imgui.is_mouse_clicked(1):
                    imgui.open_popup(f'options for parameter {parameter[0]}')

                # Render the value of the parameter
                imgui.next_column()
                imgui.text(str(parameter[1]))
                if imgui.is_item_hovered() and imgui.is_mouse_clicked(1):
                    imgui.open_popup(f'options for parameter {parameter[0]}')
                imgui.separator()

                # Configure the popup options when the right click is pressed on the parameters
                if imgui.begin_popup(f'options for parameter {parameter[0]}'):

                    # Edit parameter option
                    imgui.selectable('Edit')
                    if imgui.is_item_clicked():
                        polygon_parameter_modal = PolygonParameterModal(self._GUI_manager,
                                                                        self._GUI_manager.get_active_polygon_id(),
                                                                        parameter)
                        self._GUI_manager.open_modal(polygon_parameter_modal)

                    # Delete parameter option
                    imgui.selectable('Delete')
                    if imgui.is_item_clicked():
                        # Set a confirmation modal before deleting the parameter
                        # ------------------------------------------------------
                        confirmation_modal = ConfirmationModal(self._GUI_manager)
                        confirmation_modal.set_confirmation_text(
                            'Delete parameter',
                            f'Are you sure you want to delete {parameter[0]}?',
                            lambda: self._GUI_manager.remove_polygon_parameter(
                                self._GUI_manager.get_active_polygon_id(),
                                parameter[0]),
                            lambda: None)
                        self._GUI_manager.open_modal(confirmation_modal)

                    imgui.end_popup()

            # Show a button to add a new parameter to the polygon at the end of the table
            # ---------------------------------------------------------------------------
            imgui.columns(1)
            if imgui.button("Add New", -1):
                polygon_parameter_modal = PolygonParameterModal(self._GUI_manager,
                                                                self._GUI_manager.get_active_polygon_id())
                self._GUI_manager.open_modal(polygon_parameter_modal)
            self._end_frame()
