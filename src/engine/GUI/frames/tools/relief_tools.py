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
File with the class ReliefTools. Class in charge of render the Relief tools inside another frame.
"""

from typing import List, TYPE_CHECKING, Union

import imgui

from src.engine.GUI.font import Font
from src.engine.scene.filter.filter import Filter
from src.engine.scene.filter.height_greater_than import HeightGreaterThan
from src.engine.scene.filter.height_less_than import HeightLessThan
from src.engine.scene.filter.is_in import IsIn
from src.engine.scene.filter.is_not_in import IsNotIn
from src.engine.scene.transformation.fill_nan_transformation import FillNanTransformation
from src.engine.scene.transformation.linear_transformation import LinearTransformation
from src.utils import get_logger

if TYPE_CHECKING:
    from engine.GUI.guimanager import GUIManager

log = get_logger(module="RELIEF_TOOLS")


class ReliefTools:
    """
    Class that render the ReliefTools inside another frame.
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        self.__gui_manager: 'GUIManager' = gui_manager

        self.__transformation_options = ["Fill with nan", "Linear"]
        self.__selected_transformation_option = 0

        self.__max_height_value = 0
        self.__min_height_value = 0

        self.__polygon_data: Dict[str, Dict[str, Union[str, float]]] = {}

        # Filter data
        # -----------
        self.__filter_options: List[any] = [HeightLessThan, HeightGreaterThan, IsIn, IsNotIn]
        self.__filters: List[Filter] = []  # filters to apply on the polygon if the interpolation is triggered

        # Auxiliary variables
        # ------------------
        # Variable used to store the maximum and minimum height values calculated of the points inside the selected
        # polygon.
        self.__max_min_data_values: List[float] = [0, 0]
        # Variable used to store the values returned by the asynchronous method calculate_max_min_height.
        self.__return_array_values: List[Union[float, None]] = [None, None]

    def __render_input_value_height_filters(self, filter_obj: Union[HeightLessThan, HeightGreaterThan]):
        """
        Render the input value for filters that use a height value as an argument. Filters height_greater_than and
        height_less_than should use this input value.

        Args:
            filter_obj: Filter to which the input is rendered for.

        Returns: None
        """
        _, filter_obj.height_limit = imgui.input_float('Value', filter_obj.height_limit)

    def __render_input_value_polygon_filters(self, filter_obj: Union[IsIn, IsNotIn]):
        """
        Render the input values for the filters that use a polygon as an argument. Filters is_in and is_not_in
        should use this input value.

        Args:
            filter_obj: Filter to which the input is rendered for.

        Returns: None
        """
        # Get list with the polygons on the program and remove the active one
        # -------------------------------------------------------------------
        polygon_list = self.__gui_manager.get_polygon_id_list()

        # Remove the active polygon and add the None option
        # -------------------------------------------------
        polygon_list.remove(self.__gui_manager.get_active_polygon_id())
        polygon_list_names = list(map(lambda x: self.__gui_manager.get_polygon_name(x), polygon_list))

        polygon_list.insert(0, None)
        polygon_list_names.insert(0, 'None')

        # If polygon for filter no longer in the list, replace the values as None
        # -----------------------------------------------------------------------
        if filter_obj.polygon_id not in polygon_list:
            filter_obj.polygon_id = None

        # Show the combo options for the rendering
        # ----------------------------------------
        _, selected_polygon = imgui.combo('Value',
                                          polygon_list.index(filter_obj.polygon_id),
                                          polygon_list_names)
        filter_obj.polygon_id = polygon_list[selected_polygon]

    def current_height_information(self, active_model_id, active_polygon_id) -> None:
        """
        Render the current maximum and minimum height of the points inside the active polygon.

        Args:
            active_model_id: ID of the active model.
            active_polygon_id: ID of the active polygon.

        Returns: None
        """

        # Create the value in the dictionary of values if it does not exists
        # ------------------------------------------------------------------
        if active_polygon_id not in self.__polygon_data:
            self.__polygon_data[active_polygon_id] = {
                'max_height': 'Not Calculated',
                'min_height': 'Not Calculated'
            }

        # Update the values of the minimum and maximum height if they were calculated
        # ---------------------------------------------------------------------------
        if self.__return_array_values != [None, None]:
            self.__max_min_data_values[:] = self.__return_array_values[:]

            self.__polygon_data[active_polygon_id]['max_height'] = max(self.__max_min_data_values)
            self.__polygon_data[active_polygon_id]['min_height'] = min(self.__max_min_data_values)

            self.__return_array_values = [None, None]

        # Render the menu
        # ---------------
        self.__gui_manager.set_font(Font.TOOL_SUB_TITLE)
        imgui.text('Polygon Information')
        self.__gui_manager.set_font(Font.REGULAR)
        imgui.columns(2, None, False)
        imgui.text(f'Max height:')
        imgui.next_column()
        imgui.text(str(self.__polygon_data[active_polygon_id]['max_height']))
        imgui.next_column()
        imgui.text(f'Min height:')
        imgui.next_column()
        imgui.text(str(self.__polygon_data[active_polygon_id]['min_height']))
        imgui.columns(1)

        if imgui.button('Recalculate Information', -1):
            log.debug('Recalculate polygon information')
            self.__gui_manager.calculate_max_min_height(active_model_id,
                                                        active_polygon_id,
                                                        self.__return_array_values)

    def filter_menu(self):
        """
        Method with the logic to render the filter menu.

        Returns: None
        """

        # Variable to store if it is necessary to delete a filter
        # -------------------------------------------------------
        filter_to_remove = None

        # Title of the section
        # --------------------
        self.__gui_manager.set_font(Font.TOOL_SUB_TITLE)
        imgui.text_wrapped('Filters')
        self.__gui_manager.set_font(Font.REGULAR)

        # Render the filters on the GUI
        # -----------------------------
        for ind, filter_obj in enumerate(self.__filters):
            # Push the ID since the elements of the filter will all have the same ID
            # ----------------------------------------------------------------------
            imgui.push_id(f"relief_tools_filter_{ind}")

            # Selection of the filter
            # -----------------------
            filter_selected = -1
            for option_index, filter_option in enumerate(self.__filter_options):
                filter_selected = option_index if isinstance(filter_obj, filter_option) else filter_selected

            changed, selected_index = imgui.combo('Filter',
                                                  filter_selected,
                                                  [filter_class.name for filter_class in self.__filter_options])
            if changed:
                if self.__filter_options[selected_index] == HeightGreaterThan:
                    self.__filters[ind] = HeightGreaterThan(0)
                elif self.__filter_options[selected_index] == HeightLessThan:
                    self.__filters[ind] = HeightLessThan(0)
                elif self.__filter_options[selected_index] == IsIn:
                    self.__filters[ind] = IsIn(None)
                elif self.__filter_options[selected_index] == IsNotIn:
                    self.__filters[ind] = IsNotIn(None)
                else:
                    raise NotImplementedError(f'Creation of filter of class {self.__filter_options[selected_index]}'
                                              f' not implemented on the frame.')

            # Selection of the argument for the filter.
            # this vary depending on the filter selected
            # ------------------------------------------
            if isinstance(filter_obj, (HeightLessThan, HeightGreaterThan)):
                self.__render_input_value_height_filters(filter_obj)
            elif isinstance(filter_obj, (IsNotIn, IsIn)):
                self.__render_input_value_polygon_filters(filter_obj)

            # Button to remove the filter
            # ---------------------------
            if imgui.button('Remove Filter'):
                filter_to_remove = filter_obj

            imgui.pop_id()

        # Remove the filter if the button to remove was pressed
        # -----------------------------------------------------
        if filter_to_remove is not None:
            self.__filters.remove(filter_to_remove)

        # Button to add more filters
        # --------------------------
        if imgui.button('Add Filter', -1):
            self.__filters.append(HeightLessThan(0))

    def transformation_menu(self, active_model_id, active_polygon_id):
        """
        Method with the logic to render the menu that applies the interpolation on the maps.

        Args:
            active_model_id: Model id to use.
            active_polygon_id: Active polygon ID.

        Returns: None
        """

        # Title of the section
        # --------------------
        self.__gui_manager.set_font(Font.TOOL_SUB_TITLE)
        imgui.text('Transformation')
        self.__gui_manager.set_font(Font.REGULAR)

        # Type  of transformation
        # -----------------------
        clicked, self.__selected_transformation_option = imgui.combo(
            "Transformation", self.__selected_transformation_option, self.__transformation_options
        )

        # Parameters for the transformation
        # ---------------------------------
        if self.__selected_transformation_option == 1:
            _, self.__min_height_value = imgui.input_float('Min Height', self.__min_height_value)
            _, self.__max_height_value = imgui.input_float('Max Height', self.__max_height_value)

        # Apply transformation button
        # ---------------------------
        if imgui.button('Change Height', -1):
            if self.__selected_transformation_option == 0:
                transformation = FillNanTransformation(active_model_id,
                                                       active_polygon_id,
                                                       self.__filters)
                self.__gui_manager.apply_transformation(transformation)

            if self.__selected_transformation_option == 1:
                transformation = LinearTransformation(active_model_id,
                                                      active_polygon_id,
                                                      self.__min_height_value,
                                                      self.__max_height_value,
                                                      self.__filters)
                self.__gui_manager.apply_transformation(transformation)

    def render(self) -> None:
        """
        Render the relief tools to modify the relief of the model.
        Returns: None
        """
        # get all the data necessary
        active_polygon_id = self.__gui_manager.get_active_polygon_id()
        active_model_id = self.__gui_manager.get_active_model_id()

        self.__gui_manager.set_font(Font.TOOL_TITLE)
        imgui.text('Relief Tools')
        self.__gui_manager.set_font(Font.REGULAR)

        # Current Height Information
        # --------------------------
        self.current_height_information(active_model_id, active_polygon_id)

        # Filter Logic
        # ------------
        self.filter_menu()

        # Transformation Menu
        # -------------------
        self.transformation_menu(active_model_id, active_polygon_id)
