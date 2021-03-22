"""
Frame that indicate the parameters of the polygons
"""

import imgui
import psutil
import os

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

log = get_logger(module="Polygon Information")


class PolygonInformation(Frame):
    """
    Class that render a frame to store the parameters of the active polygon.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        super().__init__(gui_manager)
        self.__height = 300
        self.__width = 300

        # auxiliary variables
        self.__key_string_value = 'Name of parameter'
        self.__value_string_value = 'Value of parameter'

        self.__should_open_edit_dialog = False
        self.__parameter_to_edit = None

        self.__should_open_add_dialog = False

        self.__parameters_type_list = ['Text', 'Number', 'Boolean']  # these are the variable types 0, 1 and 2
        self.__current_variable_type = 0

        self.__current_bool_selected = 0

    def render(self) -> None:
        """
        Render the frame.
        Returns: None
        """
        # Do not draw the screen if there is no active polygon.
        if self._GUI_manager.get_active_polygon_id() is not None:

            # set the flags if the windows should be collapsable or not
            if self._GUI_manager.are_frame_fixed():
                imgui.begin('Polygon Information', False,
                            imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE)
                self.change_position([self._GUI_manager.get_window_width() - self.__width,
                                      self._GUI_manager.get_window_height() - self.__height])
                imgui.set_window_position(self.get_position()[0], self.get_position()[1])
                imgui.set_window_size(self.__width, self.__height, 0)

            else:
                imgui.begin('Polygon Information')

            # First row
            self._GUI_manager.set_bold_font()
            imgui.columns(2, 'Data List')
            imgui.separator()
            imgui.text("Field Name")
            imgui.next_column()
            imgui.text("Value")
            imgui.separator()
            self._GUI_manager.set_regular_font()

            # parameters
            for parameter in self._GUI_manager.get_polygon_parameters(self._GUI_manager.get_active_polygon_id()):

                # key
                imgui.next_column()
                imgui.text(parameter[0])
                if imgui.is_item_hovered() and imgui.is_mouse_clicked(1):
                    imgui.open_popup(f'options for parameter {parameter[0]}')

                # value
                imgui.next_column()
                imgui.text(str(parameter[1]))
                if imgui.is_item_hovered() and imgui.is_mouse_clicked(1):
                    imgui.open_popup(f'options for parameter {parameter[0]}')
                imgui.separator()

                # popup with the options
                if imgui.begin_popup(f'options for parameter {parameter[0]}'):

                    # edit option
                    imgui.selectable('Edit')
                    if imgui.is_item_clicked():
                        self.__should_open_edit_dialog = True
                        self.__parameter_to_edit = (parameter[0], parameter[1])

                    # delete option
                    imgui.selectable('Delete')
                    if imgui.is_item_clicked():
                        # Set a confirmation modal before deleting the parameter
                        # ------------------------------------------------------
                        self._GUI_manager.set_confirmation_modal(
                            'Delete parameter',
                            f'Are you sure you want to delete {parameter[0]}?',
                            lambda: self._GUI_manager.delete_polygon_parameter(
                                self._GUI_manager.get_active_polygon_id(),
                                parameter[0]),
                            lambda: None)

                    imgui.end_popup()

            # return to one column
            imgui.columns(1)

            # button to add a new parameter.
            if imgui.button("Add new", -1):
                self.__should_open_add_dialog = True

            # popup to add a new parameter
            self.__add_parameter_popup()

            # popup to edit a parameter
            self.__edit_parameter_popup()

            imgui.end()

    def __add_parameter_popup(self):
        # popup modal to add
        imgui.set_next_window_size(-1, -1)
        imgui.set_next_window_position(imgui.get_io().display_size.x * 0.5,
                                       imgui.get_io().display_size.y * 0.5,
                                       imgui.ALWAYS,
                                       0.5,
                                       0.5)

        # in case of opening
        if self.__should_open_add_dialog:
            imgui.open_popup('Add new parameter')

            # once open this variable should be changed to false
            self.__key_string_value = 'Name of parameter'
            self.__value_string_value = 'Value of parameter'
            self.__should_open_add_dialog = False

            # set initial variable values
            self.__current_variable_type = 0
            self.__current_bool_selected = 0

        # popup to add a new parameter
        if imgui.begin_popup_modal('Add new parameter')[0]:

            # name
            # note: the input item text is the id and should be different from the ones that shows at the same time
            imgui.text('Name of the parameter:')
            imgui.same_line()
            _, self.__key_string_value = imgui.input_text('',
                                                          self.__key_string_value,
                                                          20)

            # variable type selectable
            imgui.text('Variable type: ')
            imgui.same_line()
            clicked, self.__current_variable_type = imgui.listbox(
                "  ", self.__current_variable_type, self.__parameters_type_list
            )

            # value
            # note: the input item text is the id and should be different from the ones that shows at the same time
            imgui.text('Value of the parameter:')
            imgui.same_line()

            data_errors = self.__render_parameter_value_input()

            # logic of the button
            # -------------------
            if imgui.button('Done', -1) and not data_errors:  # do nothing if there is data errors
                polygon_id = self._GUI_manager.get_active_polygon_id()
                dict_parameters = dict(self._GUI_manager.get_polygon_parameters(polygon_id))

                # case parameter already exist
                if self.__key_string_value in dict_parameters:

                    # close the popup
                    imgui.close_current_popup()

                    # open a modal
                    self._GUI_manager.set_modal_text('Error',
                                                     f'{self._GUI_manager.get_polygon_name(polygon_id)} '
                                                     f'already has a parameter named:'
                                                     f' {self.__key_string_value}')
                # case new parameter
                else:
                    if self.__current_variable_type == 2:  # boolean
                        value = self.__convert_value_to_exportable_variable_type(self.__current_bool_selected,
                                                                                 self.__current_variable_type)
                    else:
                        value = self.__convert_value_to_exportable_variable_type(self.__value_string_value,
                                                                                 self.__current_variable_type)

                    # store the value
                    self._GUI_manager.set_polygon_parameter(self._GUI_manager.get_active_polygon_id(),
                                                            self.__key_string_value,
                                                            value)

                    # close the popup
                    imgui.close_current_popup()

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

                # reset the variables
                imgui.close_current_popup()

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
                                                            50)

        # numeric data
        elif self.__current_variable_type == 1:
            _, self.__value_string_value = imgui.input_text(' ',
                                                            self.__value_string_value,
                                                            50)
            if not self.__check_numeric(self.__value_string_value):
                imgui.text_colored('Value is not a number', 1, 0, 0)
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
