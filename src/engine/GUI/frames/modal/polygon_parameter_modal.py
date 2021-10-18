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
File Description.
"""
from typing import TYPE_CHECKING, Tuple, Union

import imgui

from src.engine.GUI.frames.modal.modal import Modal

if TYPE_CHECKING:
    from src.engine.GUI.guimanager import GUIManager


class PolygonParameterModal(Modal):
    """
    Modal in charge of adding or editing parameters defined in the polygons.
    """

    def __init__(self, gui_manager: 'GUIManager',
                 polygon_id: Union[str, None],
                 parameter_name_value: Union[Tuple[str, any], None] = None):
        """
        Constructor of the class.

        Args:
            gui_manager: GUIManager to use to get the information.
            polygon_id: ID of the polygon to modify.
            parameter_name_value: Name and value of the parameter to modify. None for creating a new parameter.
        """
        super().__init__(gui_manager)
        self.size = (500, 300)

        # auxiliary variables
        self.__key_string_value = 'Name'
        self.__value_string_value = 'Value'

        self.__parameters_type_list = ['Text', 'Number', 'Boolean']  # these are the variable types 0, 1 and 2
        self.__current_variable_type = 0
        self.__current_bool_selected = 0

        self.__input_text_maximum_character_number = 1000

        self.__polygon_to_edit = polygon_id
        self.__parameter_to_edit = parameter_name_value
        self.__title = 'Add new parameter' if self.__parameter_to_edit is None else 'Edit parameter'

        if self.__parameter_to_edit is not None:
            # Update the data showed on the modal given the parameter
            # -------------------------------------------------------
            if type(self.__parameter_to_edit[1]) == str:
                self.__current_variable_type = 0
                self.__value_string_value = str(self.__parameter_to_edit[1])
            elif type(self.__parameter_to_edit[1]) == float:
                self.__current_variable_type = 1
                self.__value_string_value = str(self.__parameter_to_edit[1])
            elif type(self.__parameter_to_edit[1]) == bool:
                self.__current_variable_type = 2
                self.__current_bool_selected = 0 if self.__parameter_to_edit[1] else 1

            self.__key_string_value = str(self.__parameter_to_edit[0])
            self.__value_string_value = str(self.__parameter_to_edit[1])

    def post_render(self) -> None:
        """
        Draw the modal to add/edit parameters from the polygons.

        Returns: None
        """
        if self._begin_modal(self.__title):

            # Get the data of the polygon and the parameters of the polygon
            polygon_id = self.__polygon_to_edit
            dict_parameters = dict(self._GUI_manager.get_polygon_parameters(polygon_id))

            # Render an input for the name of the parameter
            # Note: Fields stored in a shapefile file can not have name with more than 10 characters
            if self.__parameter_to_edit is None:
                imgui.text('Name of the parameter:')
                imgui.same_line()
                _, self.__key_string_value = imgui.input_text('',
                                                              self.__key_string_value,
                                                              10)  # shapefile fields name can not exceed 10 characters

                # Check if name already exist on polygon, if it already exists, then show an error message
                repeated_name = True if self.__key_string_value in dict_parameters else False
                if repeated_name:
                    imgui.text_colored('*Name can not be repeated', 1, 0, 0, 1)
            else:
                imgui.text(f'Parameter: {self.__key_string_value}')
                repeated_name = False

            # Render a selectable for the type of variable to create
            imgui.text('Variable type: ')
            imgui.same_line()
            clicked, self.__current_variable_type = imgui.listbox(
                "  ", self.__current_variable_type, self.__parameters_type_list
            )

            # Render an input for the value of the parameter. The type of input depends on the type of the variable
            # that is selected
            imgui.text('Value of the parameter:')
            imgui.same_line()
            data_errors = self.__render_parameter_value_input()

            # Render a button to save the parameter into the polygon. If there is error in the data written on the
            # input value or the name is an already existent name, then do not save the parameter into the polygon.
            if imgui.button('Done', -1) and not data_errors and not repeated_name:  # do nothing if there is data errors

                if self.__current_variable_type == 2:  # boolean
                    value = self.__convert_value_to_exportable_variable_type(self.__current_bool_selected,
                                                                             self.__current_variable_type)
                else:
                    value = self.__convert_value_to_exportable_variable_type(self.__value_string_value,
                                                                             self.__current_variable_type)

                # Store the value
                self._GUI_manager.set_polygon_parameter(self._GUI_manager.get_active_polygon_id(),
                                                        self.__key_string_value,
                                                        value)

                # Close the modal
                self._close_modal()

            imgui.end_popup()

    def __render_parameter_value_input(self) -> bool:
        """
        Render the correct input for the type of data selected depending on the current variable type
        (__current_variable_type).

        The value inserted by the user is stored in the __value_string_value variable. In case of boolean the value
        is stored in the __current_bool_selected variable.

        Returns: Boolean indicating if there were data errors in the input.
        """

        data_errors = False
        # Process the input to not accept invalid data
        # --------------------------------------------
        # text data
        if self.__current_variable_type == 0:
            _, self.__value_string_value = imgui.input_text(' ',
                                                            self.__value_string_value,
                                                            self.__input_text_maximum_character_number)

        # numeric data
        elif self.__current_variable_type == 1:
            _, self.__value_string_value = imgui.input_text(' ',
                                                            self.__value_string_value,
                                                            self.__input_text_maximum_character_number)
            if not self.__check_numeric(self.__value_string_value):
                imgui.text_colored('*Value is not a number', 1, 0, 0)
                data_errors = True

        # boolean data
        elif self.__current_variable_type == 2:
            _, self.__current_bool_selected = imgui.listbox(
                "   ", self.__current_bool_selected, ['True', 'False']
            )

        return data_errors

    def __convert_value_to_exportable_variable_type(self, value_to_convert: any, variable_type: int) -> any:
        """
        Convert the value to an exportable variable type depending on the current variable type selected.

        Can cause exceptions if used with a bad argument.

        If the type is text, then convert to str.
        If the type is number, then convert to float.
        If the type is boolean, then convert to boolean.

        Args:
            variable_type: Type to convert the variable to. 0 for text, 1 for number and 2 for boolean.
            value_to_convert: Value to convert.

        Returns: Value converted. None if current_variable_type has an invalid value.
        """
        value = None
        if variable_type == 0:
            value = str(value_to_convert)
        elif variable_type == 1:
            value = float(value_to_convert)
        elif variable_type == 2:
            value = True if value_to_convert == 0 else False

        return value

    def __check_numeric(self, value: str) -> bool:
        """
        Check if a string is numerical.

        Args:
            value: String to analyze.

        Returns: Boolean indicating if the value is numerical or not
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
