"""
File with the class PolygonTools, class in charge of rendering the tools for the polygon management in the GUI.
"""

import imgui

from src.utils import get_logger

from src.error.not_enought_points_error import NotEnoughPointsError

log = get_logger(module="POLYGON_TOOLS")


class PolygonTools:
    """
    Class that render the PolygonTools inside another frame.
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, gui_manager: 'GUIManager', button_margin_width=17):
        """
        Constructor of the class.
        """
        self.__GUI_manager = gui_manager

        self.__button_margin_width = button_margin_width

        self.__color_pick_window_size_x = 300
        self.__color_pick_window_size_y = -1
        self.__color_pick_should_open = False
        self.__color_selected_default = (1, 1, 0, 1)
        self.__dot_color_selected_default = (1, 1, 0, 1)
        self.__color_selected_dict = {}

        self.__rename_size_x = 300
        self.__rename_size_y = -1
        self.__rename_padding_x = 20

        self.__opened_action_popup_dict = {}

        self.__tool_before_pop_up = None
        self.__input_text_value = ''
        self.__rename_folder_input_text_value = ''

        self.__open_rename_folder_popup = False

    def __change_folder_selectable(self, current_folder_id: str, polygon_id: str) -> bool:
        """
        Render the selectable for changing folders.

        Returns: If the element was clicked or not.
        """
        clicked_selectable = False

        if imgui.begin_menu("Change Folder"):
            for folder_id in self.__GUI_manager.get_polygon_folder_id_list():
                imgui.menu_item(self.__GUI_manager.get_polygon_folder_name(folder_id))
                if imgui.is_item_clicked():
                    self.__GUI_manager.move_polygon_to_polygon_folder(current_folder_id,
                                                                      polygon_id,
                                                                      folder_id)

            imgui.end_menu()

        return clicked_selectable

    def __color_button(self, polygon_id: str) -> None:
        """
        Define the modal to show if the color pick is selected.

        Returns: None

        Args:
            polygon_id: id of the polygon to render the button to

        Returns: None
        """

        # Generate button to change the color of the polygon
        # ---------------------------------------------------
        if imgui.color_button("Color",
                              self.__color_selected_dict[polygon_id]['polygon'][0],
                              self.__color_selected_dict[polygon_id]['polygon'][1],
                              self.__color_selected_dict[polygon_id]['polygon'][2],
                              self.__color_selected_dict[polygon_id]['polygon'][3]):
            log.debug("Changing color pick selected to true")

            # deactivate the tool and store it to return it later
            # ---------------------------------------------------
            self.__tool_before_pop_up = self.__GUI_manager.get_active_tool()
            self.__GUI_manager.set_active_tool(None)

            # activate the pop up
            # -------------------
            self.__color_pick_should_open = True

        # Define the modal to show
        # ------------------------
        if imgui.begin_popup_modal(f'Select a color for {polygon_id}')[0]:
            imgui.set_window_size(self.__color_pick_window_size_x, self.__color_pick_window_size_y)

            color_selected_data = self.__color_selected_dict[polygon_id]

            imgui.text("Pick a color to use for the lines:")
            color_changed, color_selected_data['polygon'] = imgui.color_edit4("Lines color",
                                                                              color_selected_data['polygon'][0],
                                                                              color_selected_data['polygon'][1],
                                                                              color_selected_data['polygon'][2],
                                                                              color_selected_data['polygon'][3])

            imgui.text("Pick a color to use for the dots:")
            dot_color_changed, color_selected_data['dot'] = imgui.color_edit4("Dots color",
                                                                              color_selected_data['dot'][0],
                                                                              color_selected_data['dot'][1],
                                                                              color_selected_data['dot'][2],
                                                                              color_selected_data['dot'][3])

            if color_changed:
                log.debug(f"Changing colors of lines of polygon with id {polygon_id}")
                self.__GUI_manager.change_color_of_polygon(polygon_id, color_selected_data['polygon'])

            if dot_color_changed:
                log.debug(f"Changing colors of dots of polygon with id {polygon_id}")
                self.__GUI_manager.change_dot_color_of_polygon(polygon_id, color_selected_data['dot'])

            if imgui.button("Close"):
                # return the normal tool and close the pop up
                # -------------------------------------------
                self.__GUI_manager.set_active_tool(self.__tool_before_pop_up)
                imgui.close_current_popup()

            imgui.end_popup()

        # Open the modal if the condition to show is fulfilled
        # ----------------------------------------------------
        if self.__color_pick_should_open:
            imgui.open_popup(f'Select a color for {polygon_id}')
            self.__color_pick_should_open = False

    def __create_new_polygon(self, folder_id: str = None) -> None:
        """
        Calls the GUIManager to create a new polygon in the selected folder.
        If folder_name is None, then a new folder is created.

        Args:
            folder_id: Folder in which create the polygon.

        Returns: None
        """
        # change the tool to create polygon
        # ---------------------------------
        self.__GUI_manager.set_active_tool('create_polygon')
        # create the polygon and add it to a folder
        # -----------------------------------------
        new_polygon_id = self.__GUI_manager.create_new_polygon()
        if folder_id is None:
            folder_id = self.__GUI_manager.create_polygon_folder('New Folder')
            self.__GUI_manager.add_polygon_to_polygon_folder(folder_id, new_polygon_id)
        else:
            self.__GUI_manager.add_polygon_to_polygon_folder(folder_id, new_polygon_id)
        # add the colors to the list of colors data
        # -----------------------------------------
        self.__color_selected_dict[new_polygon_id] = {
            'polygon': self.__color_selected_default,
            'dot': self.__dot_color_selected_default
        }
        # set it as the active polygon
        # ----------------------------
        log.debug("Setting polygon as the active polygon")
        self.__GUI_manager.set_active_polygon(new_polygon_id)

    def __delete_selectable(self, active_polygon: str, polygon_id: str) -> bool:
        """
        Define a button for the action of deleting a polygon.

        Args:
            active_polygon: id of the active polygon of the program.
            polygon_id: id of the polygon to render the button to.

        Returns: Boolean indicating if selectable
        """
        clicked_selectable = False

        imgui.selectable('Delete')
        if imgui.is_item_clicked():
            log.debug(f"Delete polygon with id: {polygon_id}")
            clicked_selectable = True

            # noinspection PyMissingOrEmptyDocstring
            def yes_function():
                # delete the polygon from the program
                self.__GUI_manager.delete_polygon_by_id(polygon_id)

                # if the deleted polygon is the active, change the program status no None (deprecated code)
                if active_polygon == polygon_id:
                    self.__GUI_manager.set_active_polygon(None)

            self.__GUI_manager.set_confirmation_modal(
                'Confirmation',
                f'Do you want to delete the polygon {self.__GUI_manager.get_polygon_name(polygon_id)}?',
                yes_function,
                lambda: None
            )

        return clicked_selectable

    def __export_selectable(self, polygon_id) -> bool:
        """
        Shows a button that let the user export the current polygon in a shapefile file.

        Args:
            polygon_id: Id of the polygon to render the button to

        Returns: Boolean representing if the selectable was clicked.
        """
        clicked_selectable = False

        imgui.selectable('Export to shapefile')
        if imgui.is_item_clicked():
            log.debug(f"Exporting polygon with id: {polygon_id}")
            clicked_selectable = True

            try:
                self.__GUI_manager.export_polygon_with_id(polygon_id)

            except NotEnoughPointsError as e:
                log.exception(e)
                self.__GUI_manager.set_modal_text("Error", "The polygon does not have enough points.")

        return clicked_selectable

    def __folder_popup_menu(self, folder_id: str) -> None:
        """
        Folder popup menu that shows the name of the folder and configure the actions that happens when a second
        click is pressed.

        Args:
            folder_id: ID of the folder to show

        Returns: None
        """
        imgui.text(self.__GUI_manager.get_polygon_folder_name(folder_id))
        if imgui.is_item_hovered() and imgui.is_mouse_clicked(1):
            imgui.open_popup(f'Second click options folder {folder_id}')

        # button to create a new polygon in the folder
        imgui.same_line()

        imgui.push_id(folder_id)
        if imgui.button('+'):
            self.__create_new_polygon(folder_id)
        imgui.pop_id()

        # menu option for second click on the folder
        if imgui.begin_popup(f'Second click options folder {folder_id}'):
            imgui.text("Select an action")

            imgui.separator()
            imgui.selectable('Export Polygons')
            if imgui.is_item_clicked():
                try:
                    self.__GUI_manager.export_polygons_inside_folder(folder_id)

                except NotEnoughPointsError:
                    self.__GUI_manager.set_modal_text('Error', 'One or more polygons does not have enough '
                                                               'points to be exported.')
                    self.__GUI_manager.set_modal_text('Information', 'Polygons exported successfully.')
                    imgui.close_current_popup()

            imgui.separator()
            imgui.selectable('Rename')
            if imgui.is_item_clicked():
                self.__open_rename_folder_popup = True

            imgui.selectable('Delete folder')
            if imgui.is_item_clicked():

                # noinspection PyMissingOrEmptyDocstring
                def yes_function():
                    # get list of polygons on the folder
                    polygon_id_list = self.__GUI_manager.get_polygons_id_from_polygon_folder(folder_id)

                    # change the active polygon only if it was deleted
                    if self.__GUI_manager.get_active_polygon_id() in polygon_id_list:
                        self.__GUI_manager.set_active_polygon(None)

                    # delete all the polygons in the folder
                    self.__GUI_manager.delete_all_polygons_inside_folder(folder_id)

                    # delete the folder from the list of folders and don't render it's polygons
                    self.__GUI_manager.delete_polygon_folder(folder_id)

                # ask for the confirmation of the action
                self.__GUI_manager.set_confirmation_modal(
                    'Confirmation',
                    f'Do you want to delete the folder {self.__GUI_manager.get_polygon_folder_name(folder_id)}?',
                    yes_function,
                    lambda: None
                )

            imgui.end_popup()

        # popup modal for renaming the folders
        if self.__open_rename_folder_popup:
            # open the popup
            imgui.open_popup(f'Rename folder {folder_id}')

            # store the folder name as initial input of the popup
            self.__rename_folder_input_text_value = self.__GUI_manager.get_polygon_folder_name(folder_id)

            # store the last tool used
            self.__tool_before_pop_up = self.__GUI_manager.get_active_tool()
            self.__GUI_manager.set_active_tool(None)

            # tell the object to not open again
            self.__open_rename_folder_popup = False

        imgui.set_next_window_size(self.__rename_size_x, -1)
        if imgui.begin_popup_modal(f'Rename folder {folder_id}')[0]:
            imgui.text('Change the name of the folder:')
            changed, self.__rename_folder_input_text_value = imgui.input_text('New name',
                                                                              self.__rename_folder_input_text_value,
                                                                              25)

            if imgui.button('Change name', self.__rename_size_x - self.__button_margin_width):
                self.__GUI_manager.set_polygon_folder_name(folder_id, self.__rename_folder_input_text_value)
                imgui.close_current_popup()

            imgui.end_popup()

    def __generate_polygon_list(self) -> None:
        """
        Generate the list of polygons to show to the user.

        Returns: None
        """

        active_polygon = self.__GUI_manager.get_active_polygon_id()

        for folder_id in self.__GUI_manager.get_polygon_folder_id_list():
            self.__folder_popup_menu(folder_id)

            # list of polygons to render to each folder
            if folder_id in self.__GUI_manager.get_polygon_folder_id_list():
                for polygon_id in self.__GUI_manager.get_polygons_id_from_polygon_folder(folder_id):
                    # push id so the buttons doesnt have conflicts with names
                    imgui.push_id(polygon_id)

                    # show a checkbox with the id of the polygon and show it market if the polygon is active
                    clicked, current_state = imgui.checkbox(self.__GUI_manager.get_polygon_name(polygon_id),
                                                            True if polygon_id == active_polygon else False)
                    self.__polygon_action_logic(active_polygon, polygon_id, folder_id)

                    imgui.same_line()
                    self.__color_button(polygon_id)

                    if not self.__GUI_manager.is_polygon_planar(polygon_id):
                        imgui.same_line()
                        imgui.image(self.__GUI_manager.get_icon('warning').get_texture_id(), 25, 25)
                        if imgui.is_item_hovered():
                            imgui.set_tooltip("Polygon is not planar!")

                    # pop the id to continue rendering the others elements
                    imgui.pop_id()

                    if clicked:

                        # change or deselect the active polygon.
                        if self.__GUI_manager.get_active_polygon_id() == polygon_id:
                            self.__GUI_manager.set_active_polygon(None)
                        else:
                            self.__GUI_manager.set_active_polygon(polygon_id)

                        # Activate the create_polygon tool when clicked the polygon
                        self.__GUI_manager.set_active_tool('create_polygon')

    def __polygon_action_logic(self, active_polygon, polygon_id, polygon_folder_id) -> None:
        """
        Generate the button [Actions] in the tools windows.

        The button contains a list of actions to do in the polygon specified.

        Args:
            active_polygon: active polygon on the engine
            polygon_id: id of the polygon to render the button

        Returns: None
        """

        # configure the button to use to open the actions on the polygon
        if imgui.is_item_clicked(1):
            # store the old tool and change the tool to none
            self.__tool_before_pop_up = self.__GUI_manager.get_active_tool()
            self.__GUI_manager.set_active_tool(None)

            # open the popup
            imgui.open_popup(f"action pop up {polygon_id}")

        # open the popup showing the actions for the polygon
        if imgui.begin_popup(f"action pop up {polygon_id}"):

            # store in an external variable that the popup was open (to check when its closed)
            self.__opened_action_popup_dict[polygon_id] = True

            # small text giving instructions
            imgui.text("Select an action")
            imgui.separator()

            # what happens when the export option is pressed (all logic is done in the calling)
            if self.__export_selectable(polygon_id):
                # once the rename is completed, go back to the original tool
                self.__GUI_manager.set_active_tool(self.__tool_before_pop_up)

                # tell the external variable that the popup was closed
                self.__opened_action_popup_dict[polygon_id] = False

                # close the popup
                imgui.close_current_popup()
            imgui.separator()

            # what happens when changing the polygon from one folder to another
            if self.__change_folder_selectable(polygon_folder_id, polygon_id):
                # once the rename is completed, go back to the original tool
                self.__GUI_manager.set_active_tool(self.__tool_before_pop_up)

                # tell the external variable that the popup was closed
                self.__opened_action_popup_dict[polygon_id] = False

                # close the popup
                imgui.close_current_popup()

            # what happens when rename option is pressed (all logic is inside the calling)
            if self.__rename_polygon_selectable(polygon_id):
                # once the rename is completed, go back to the original tool
                self.__GUI_manager.set_active_tool(self.__tool_before_pop_up)

                # tell the external variable that the popup was closed
                self.__opened_action_popup_dict[polygon_id] = False

                # close the popup
                imgui.close_current_popup()

            # what happens when delete option is pressed (all logic is inside the calling)
            if self.__delete_selectable(active_polygon, polygon_id):
                # once the rename is completed, go back to the original tool
                self.__GUI_manager.set_active_tool(self.__tool_before_pop_up)

                # tell the external variable that the popup was closed
                self.__opened_action_popup_dict[polygon_id] = False

                # close the popup
                imgui.close_current_popup()

            imgui.end_popup()

        # If the popup does not open but the external variable says that it is open, then that
        # means that the popup was closed from external methods (usually a click outside the popup)
        elif self.__opened_action_popup_dict.get(polygon_id, False):
            log.debug('Pop up closed using external methods...')

            # tell the external variable that the popup is closed (this makes this code to execute only once)
            self.__opened_action_popup_dict[polygon_id] = False

            # go back to the last tool used
            self.__GUI_manager.set_active_tool(self.__tool_before_pop_up)

    def __rename_polygon_selectable(self, polygon_id: str) -> bool:
        """
        Button to rename the polygon.

        Args:
            polygon_id: Id of the polygon to rename.

        Returns: Boolean indicating if button was pressed
        """
        clicked_selectable = False

        imgui.selectable('Rename')
        if imgui.is_item_clicked():
            log.debug("Rename Button")

            # set the name of the polygon as initial text
            self.__input_text_value = self.__GUI_manager.get_polygon_name(polygon_id)

            # open the pop up
            imgui.open_popup(f'Rename {polygon_id}')

        if imgui.begin_popup_modal(f'Rename {polygon_id}')[0]:

            # resize the window
            imgui.set_window_size(self.__rename_size_x, self.__rename_size_y)

            # write a text for the user
            imgui.text("Write the new name of the polygon:")

            # open the text input box
            changed, self.__input_text_value = imgui.input_text('New Name', self.__input_text_value, 15)
            self.__GUI_manager.set_polygon_name(polygon_id, str(self.__input_text_value))

            # close the pop up
            if imgui.button("Save and close", self.__rename_size_x - self.__rename_padding_x):
                clicked_selectable = True

                # reset the input text
                self.__input_text_value = ''

                imgui.close_current_popup()

            imgui.end_popup()

        return clicked_selectable

    def __show_polygon_tools(self, left_frame_width: int) -> None:
        """
        Show the polygon tools on the frame

        Args:
            left_frame_width: width of the frame.
        """
        self.__GUI_manager.set_tool_title_font()
        imgui.text("Polygon Tools")
        self.__GUI_manager.set_regular_font()
        if imgui.button("Create folder", width=left_frame_width - self.__button_margin_width):
            self.__create_new_polygon()

        self.__generate_polygon_list()

    def add_new_polygon(self, polygon_id: str) -> None:
        """
        Add a polygon (externally generated, already existent in the program) to the GUI.
        Polygon must be already in some folder.

        Args:
            polygon_id: Id of the polygon externally generated.

        Returns: None
        """
        self.__color_selected_dict[polygon_id] = {
            'polygon': self.__color_selected_default,
            'dot': self.__dot_color_selected_default
        }

    def render(self, frame_width: int) -> None:
        """
        Render the polygon tools to manage the polygons in the program.
        Returns: None
        """
        self.__show_polygon_tools(frame_width)