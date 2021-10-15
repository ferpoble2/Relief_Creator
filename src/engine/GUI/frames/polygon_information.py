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

from src.engine.GUI.font import Font
from src.engine.GUI.frames.frame import Frame
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

        # auxiliary variables
        self.__key_string_value = 'Name of parameter'
        self.__value_string_value = 'Value of parameter'

        self.__should_open_edit_dialog = False
        self.__parameter_to_edit = None

        self.__should_open_add_dialog = False

        self.__parameters_type_list = ['Text', 'Number', 'Boolean']  # these are the variable types 0, 1 and 2
        self.__current_variable_type = 0

        self.__current_bool_selected = 0

        self.__input_text_maximum_character_number = 1000

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
                        self.__should_open_edit_dialog = True
                        self.__parameter_to_edit = (parameter[0], parameter[1])

                    # Delete parameter option
                    imgui.selectable('Delete')
                    if imgui.is_item_clicked():
                        # Set a confirmation modal before deleting the parameter
                        # ------------------------------------------------------
                        self._GUI_manager.open_confirmation_modal(
                            'Delete parameter',
                            f'Are you sure you want to delete {parameter[0]}?',
                            lambda: self._GUI_manager.remove_polygon_parameter(
                                self._GUI_manager.get_active_polygon_id(),
                                parameter[0]),
                            lambda: None)

                    imgui.end_popup()

            # Show a button to add a new parameter to the polygon at the end of the table
            # ---------------------------------------------------------------------------
            imgui.columns(1)
            if imgui.button("Add New", -1):
                self.__should_open_add_dialog = True

            self._end_frame()

    def post_render(self) -> None:
        """
        Method executed after the rendering process of all components.

        This methods define all the logic related to the popups that can be raised due to the logic of the frame.

        Returns: None
        """

        # Popup to add a new parameter
        # ----------------------------
        self.__add_parameter_popup()

        # Popup to edit a parameter
        # -------------------------
        self.__edit_parameter_popup()

    def __add_parameter_popup(self):

        # Configure the window in case the popup should open
        # --------------------------------------------------
        imgui.set_next_window_size(-1, -1)
        imgui.set_next_window_position(imgui.get_io().display_size.x * 0.5,
                                       imgui.get_io().display_size.y * 0.5,
                                       imgui.ALWAYS,
                                       0.5,
                                       0.5)

        # Open the popup and configure it in case the variable to open it is set to True
        # ------------------------------------------------------------------------------
        if self.__should_open_add_dialog:
            # Ask IMGUI to open the popup and change the variable that is used to check if the popup should open
            imgui.open_popup('Add new parameter')
            self.__should_open_add_dialog = False

            # Configure the information of the popup
            self.__key_string_value = 'Name'
            self.__value_string_value = 'Value of parameter'
            self.__current_variable_type = 0
            self.__current_bool_selected = 0

            # Disable keyboard input for glfw
            self._GUI_manager.set_controller_keyboard_callback_state(False)

        # Render the popup if it was opened
        # ---------------------------------
        if imgui.begin_popup_modal('Add new parameter')[0]:

            # Get the data of the polygon and the parameters of the polygon
            polygon_id = self._GUI_manager.get_active_polygon_id()
            dict_parameters = dict(self._GUI_manager.get_polygon_parameters(polygon_id))

            # Render an input for the name of the parameter
            # Note: Fields stored in a shapefile file can not have name with more than 10 characters
            imgui.text('Name of the parameter:')
            imgui.same_line()
            _, self.__key_string_value = imgui.input_text('',
                                                          self.__key_string_value,
                                                          10)  # shapefile fields name can not exceed 10 characters

            # Check if name already exist on polygon, if it already exists, then show an error message
            repeated_name = True if self.__key_string_value in dict_parameters else False
            if repeated_name:
                imgui.text_colored('*Name can not be repeated', 1, 0, 0, 1)

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

                # Close the popup and reactivate the glfw keyboard callback
                imgui.close_current_popup()
                self._GUI_manager.set_controller_keyboard_callback_state(True)

            imgui.end_popup()

    def __edit_parameter_popup(self):

        # popup modal to edit
        imgui.set_next_window_size(-1, -1)
        imgui.set_next_window_position(imgui.get_io().display_size.x * 0.5,
                                       imgui.get_io().display_size.y * 0.5,
                                       imgui.ALWAYS,
                                       0.5,
                                       0.5)

        # ask if open it
        if self.__should_open_edit_dialog:
            imgui.open_popup('Edit parameter')
            self._GUI_manager.set_controller_keyboard_callback_state(True)

            # once open this variable should be changed to false
            self.__should_open_edit_dialog = False

            # change default values for the fields
            self.__key_string_value = self.__parameter_to_edit[0]
            self.__value_string_value = ''
            self.__current_bool_selected = 0

            if type(self.__parameter_to_edit[1]) == str:
                self.__current_variable_type = 0
                self.__value_string_value = self.__parameter_to_edit[1]
            elif type(self.__parameter_to_edit[1]) == float:
                self.__current_variable_type = 1
                self.__value_string_value = str(self.__parameter_to_edit[1])
            elif type(self.__parameter_to_edit[1]) == bool:
                self.__current_variable_type = 2
                self.__current_bool_selected = 0 if self.__parameter_to_edit[1] else 1

            # disable the input
            self._GUI_manager.set_controller_keyboard_callback_state(False)

        # popup to edit a parameter
        if imgui.begin_popup_modal('Edit parameter')[0]:

            # should not modify the key of the parameter
            imgui.text(f'Parameter: {self.__key_string_value}')

            # variable type
            imgui.text('Variable type: ')
            imgui.same_line()
            clicked, self.__current_variable_type = imgui.listbox(
                "  ", self.__current_variable_type, self.__parameters_type_list
            )

            # new value
            imgui.text('New value of the parameter:')
            imgui.same_line()

            data_errors = self.__render_parameter_value_input()

            # Button Logic
            if imgui.button('Done', -1) and not data_errors:

                if self.__current_variable_type == 2:  # boolean
                    value = self.__convert_value_to_exportable_variable_type(self.__current_bool_selected,
                                                                             self.__current_variable_type)
                else:
                    value = self.__convert_value_to_exportable_variable_type(self.__value_string_value,
                                                                             self.__current_variable_type)

                # set the new parameter
                self._GUI_manager.set_polygon_parameter(self._GUI_manager.get_active_polygon_id(),
                                                        self.__key_string_value,
                                                        value)

                # close the popup and reactivate the glfw callback
                imgui.close_current_popup()
                self._GUI_manager.set_controller_keyboard_callback_state(True)

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
