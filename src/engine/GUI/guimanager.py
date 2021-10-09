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
Module that defines the class GUIManager, class in charge of the UI of te application.

This module uses the implementation of IMGUI that uses GLFW, and thus, the callbacks defined by IMGUI must be passed
to the controller of the program to make sure they are called from within the real callbacks functions configured
on the program.

Before executing the callbacks of the program defined on GLFW, the method process_inputs from the GUIManager class
must be called. This method process the inputs that happened on the GUI so the callbacks functions defined by IMGUI
work correctly.
"""

# noinspection PyPep8Naming
from typing import Dict, List, TYPE_CHECKING, Union

import OpenGL.constant as OGLConstant
import imgui
from imgui.integrations.glfw import GlfwRenderer

from src.engine.GUI.frames.combine_map_modal import CombineMapModal
from src.engine.GUI.frames.confirmation_modal import ConfirmationModal
from src.engine.GUI.frames.debug import Debug
from src.engine.GUI.frames.loading import Loading
from src.engine.GUI.frames.main_menu_bar import MainMenuBar
from src.engine.GUI.frames.mouse_coordinates import MouseCoordinates
from src.engine.GUI.frames.polygon_information import PolygonInformation
from src.engine.GUI.frames.test_window import TestWindow
from src.engine.GUI.frames.text_modal import TextModal
from src.engine.GUI.frames.tools.tools import Tools
from src.engine.GUI.frames.tools_3D import Tools3D
from src.engine.GUI.icon import Icon
from src.engine.GUI.polygon_folder_manager import PolygonFolderManager
from src.program.view_mode import ViewMode
from src.utils import get_logger

if TYPE_CHECKING:
    from src.engine.engine import Engine
    from glfw import _GLFWwindow
    from src.program.tools import Tools
    from src.engine.scene.transformation.transformation import Transformation
    from src.engine.scene.interpolation.interpolation import Interpolation

# noinspection SpellCheckingInspection
log = get_logger(module='GUIMANAGER')


# noinspection PyMethodMayBeStatic
class GUIManager:
    """
    Class to manage all the UI configurations and functions.

    This class uses the IMGUI module that implements its logic using GLFW. Since the logic of this class and the logic
    of the controller collide with each other, the following must be done so this class can work correctly.

    The callbacks defined by IMGUI must be called within the real callbacks configured on the application (likely
    located on the controller), to do this, this class define methods that return the callbacks defined by IMGUI. Also,
    the method process_inputs must be called before executing the callbacks so IMGUI can process the inputs and execute
    the logic defined it its callbacks correctly.
    """

    def __init__(self,
                 engine: 'Engine',
                 window: '_GLFWwindow',
                 regular_font_size: int,
                 tool_title_font_size: int,
                 tool_sub_title_font_size: int,
                 debug_mode: bool = False):
        """
        Constructor of the class.

        Must receive the engine in which the class will be used to make calls.

        Args:
            engine: Engine to use to execute the logic of the class.
            debug_mode: Boolean indicating if the GUI should render debug frames.
            tool_sub_title_font_size: Font size to use for the sub_title text.
            tool_title_font_size: Font size to use for the tool_tile text.
            regular_font_size: Font size to use for the regular font.
            window: Window to use to draw the GUI.
        """

        # IMGUI parameters
        # ----------------
        self.__implementation = None
        self.__io = None
        self.__font_regular = None
        self.__font_bold = None
        self.__font_tool_title = None
        self.__font_tool_sub_title = None

        # GLFW parameters
        # ---------------
        self.__glfw_window = None

        # Class parameters
        # ----------------
        self.__engine = engine
        self.__polygon_folder_manager = PolygonFolderManager()
        self.__model_id_list = []
        self.__icons_dict = None

        # Frames used by the GUI
        # ----------------------
        self.__main_menu_bar = MainMenuBar(self)
        self.__text_modal = TextModal(self)
        self.__tools = Tools(self)
        self.__loading = Loading(self)
        self.__polygon_information = PolygonInformation(self)
        self.__confirmation_modal = ConfirmationModal(self)
        self.__tools_3d = Tools3D(self)
        self.__mouse_coordinates = MouseCoordinates(self)
        self.__combine_map_modal = CombineMapModal(self)

        self.__component_list_2D = [
            self.__main_menu_bar,
            self.__mouse_coordinates,
            self.__text_modal,
            self.__tools,
            self.__loading,
            self.__polygon_information,
            self.__confirmation_modal,
            self.__combine_map_modal
        ]

        self.__component_list_3D = [
            self.__main_menu_bar,
            self.__loading,
            self.__text_modal,
            self.__confirmation_modal,
            self.__tools_3d
        ]

        # Auxiliary parameters
        # --------------------
        self.__is_mouse_inside_frame = False

        self.__initialize_variables(window,
                                    regular_font_size,
                                    tool_title_font_size,
                                    tool_sub_title_font_size,
                                    debug_mode)

    def __add_polygon_to_polygon_folder(self, folder_id: str, polygon_id: str) -> None:
        """
        Add an already existent polygon to the specified folder.

        This methods change the polygon draw order so the polygons are draw in the order they are shown on the
        GUI.

        Args:
            folder_id: Folder to use
            polygon_id: Polygon to add to the folder

        Returns: None
        """

        # Add the polygon to the folder
        # -----------------------------
        self.__polygon_folder_manager.add_polygon_to_folder(folder_id, polygon_id)

        # Change the draw order of the polygon to match the showed folder on the GUI
        # --------------------------------------------------------------------------
        self.__engine.change_polygon_draw_priority(polygon_id,
                                                   self.__polygon_folder_manager.get_polygon_position(polygon_id))

    def __initialize_variables(self,
                               window,
                               regular_font_size: int,
                               tool_title_font_size: int,
                               tool_sub_title_font_size: int,
                               debug_mode: bool = False) -> None:
        """
        Set the initial configurations of the GUI.

        Args:
            debug_mode: Boolean indicating if the GUI should render debug frames.
            tool_sub_title_font_size: Font size to use for the sub_title text.
            tool_title_font_size: Font size to use for the tool_tile text.
            regular_font_size: Font size to use for the regular font.
            window: Window to use to draw the GUI

        Returns: None

        """
        log.info("Initializing GUI")
        imgui.create_context()
        self.__implementation = GlfwRenderer(window)
        self.__glfw_window = window

        # Style options
        style = imgui.get_style()
        style.frame_rounding = 5
        imgui.style_colors_light(style)

        # Font options
        self.__io = imgui.get_io()
        self.__font_regular = self.__io.fonts.add_font_from_file_ttf(
            'resources/fonts/open_sans/OpenSans-Regular.ttf', regular_font_size
        )
        self.__font_bold = self.__io.fonts.add_font_from_file_ttf(
            'resources/fonts/open_sans/OpenSans-Bold.ttf', regular_font_size
        )
        self.__font_tool_title = self.__io.fonts.add_font_from_file_ttf(
            'resources/fonts/open_sans/OpenSans-Regular.ttf', tool_title_font_size
        )
        self.__font_tool_sub_title = self.__io.fonts.add_font_from_file_ttf(
            'resources/fonts/open_sans/OpenSans-Regular.ttf', tool_sub_title_font_size
        )

        self.__implementation.refresh_font_texture()

        # load the icons on the GUI
        self.__load_icons()

        if debug_mode:
            debug = Debug(self)
            test_window = TestWindow(self)

            self.__component_list_2D += [debug, test_window]
            self.__component_list_3D += [debug, test_window]

    def __load_icons(self) -> None:
        """
        Load the icons of the application in the icons dictionary.

        Returns: None
        """
        self.__icons_dict = {
            'warning': Icon('resources/icons/warning.png')
        }

    def __update_frames_with_new_polygon(self, polygon_id: str) -> None:
        """
        Update the frames with the new polygon, calling the corresponding method by class.

        Args:
            polygon_id: ID of the new polygon.

        Returns: None
        """
        for frame in self.__component_list_2D + self.__component_list_3D:
            frame.add_new_polygon(polygon_id)

    def add_imported_polygon(self, polygon_id: str) -> None:
        """
        Add the polygon to the folder that stores the imported polygons and update all the frames with the new
        polygon.

        If the folder do not exist, then it is created by the polygon manager.

        All the frames are updated with the method add_new_polygon.

        Args:
            polygon_id: ID of the polygon to add.

        Returns: None
        """
        imported_polygon_id = self.__polygon_folder_manager.get_imported_polygon_folder_id()
        self.__add_polygon_to_polygon_folder(imported_polygon_id, polygon_id)

        # update gui
        self.__update_frames_with_new_polygon(polygon_id)

    def add_model_to_gui(self, model_id: str) -> None:
        """
        Add a new model to the list of models to show on the GUI.

        The model is added at the end of the list of models.

        Args:
            model_id: Name of the model to add.

        Returns: Add the model to the list of models to be showed on the GUI.
        """
        self.__model_id_list.append(model_id)

    def add_polygon_to_gui(self, polygon_id: str, polygon_folder_id: str = None) -> None:
        """
        Add a new polygon to the GUI and broadcast a method to all the frames that uses the information of the polygons.

        Args:
            polygon_folder_id: Polygon folder to add the polygon to.
            polygon_id: ID of the created polygon.

        Returns: None
        """
        if polygon_folder_id is None:
            folder_id = self.__polygon_folder_manager.create_new_folder('New Folder')
            self.__add_polygon_to_polygon_folder(folder_id, polygon_id)
        else:
            self.__add_polygon_to_polygon_folder(polygon_folder_id, polygon_id)

        # Update the frames on the gui
        self.__update_frames_with_new_polygon(polygon_id)

    def add_zoom(self) -> None:
        """
        Ask the engine to add more zoom to the maps. Only works on the 2D mode.

        Returns: None
        """
        self.__engine.add_zoom()

    def apply_interpolation(self, interpolation: 'Interpolation') -> None:
        """
        Call the engine to interpolate the points.

        Args:
            interpolation: Interpolation to use to modify the points of the model.

        Returns: None
        """
        self.__engine.apply_interpolation(interpolation)

    def apply_transformation(self, transformation: 'Transformation') -> None:
        """
        Call the engine to change the height of the points inside the specified polygon.

        Args:
            transformation: Transformation to apply.

        Returns: None
        """
        self.__engine.apply_transformation(transformation)

    def calculate_max_min_height(self, model_id: str, polygon_id: str, return_data: list) -> None:
        """
        Ask the engine for max and min values of the vertices that are inside the polygon.

        This method is executed asynchronously, returning immediately. When the asynchronous task end, the calculated
         values will be stored in the return_data variable. In case of error, [None, None] will be set in the
         return_data variable.

        Args:
            return_data: List with length 2 where to store the data.
            model_id: ID of the model to use.
            polygon_id: ID of the polygon to use.

        Returns: tuple with the max and min value.
        """
        return self.__engine.calculate_max_min_height(model_id, polygon_id, return_data)

    def change_color_file_with_dialog(self) -> None:
        """
        Ask the engine to open a dialog (file selector menu) and change the CPT file used to color the 2D and 3D models.

        This change all the models using the color file.

        Returns: None
        """
        self.__engine.change_color_file_with_dialog()

    def change_color_of_polygon(self, polygon_id: str, color: list) -> None:
        """
        Change the color of the polygon with the specified id.

        Only change the color of the lines of the polygon, the color of the dots must be changed with the method
        change_dot_color_of_polygon. The colors must be defined in the order RGBA and with values between 0 and 1.

        Examples:
            gui_manager.change_color_of_polygon('my_polygon', [1,0,0,1])

        Args:
            polygon_id: Id of the polygon to change the color.
            color: List-like object with the colors to use.

        Returns: None
        """
        self.__engine.change_color_of_polygon(polygon_id, color)

    def change_current_3D_model_normalization_factor(self, normalization_height_value: float) -> None:
        """
        Ask the engine to change the current normalization factor being used for the active 3d model.

        Args:
            normalization_height_value: new normalization factor

        Returns: None
        """
        self.__engine.change_current_3D_model_normalization_factor(normalization_height_value)

    def change_dot_color_of_polygon(self, polygon_id: str, color: list) -> None:
        """
        Change the color of the dots of the polygon with the specified id.

        Only change the color of the dots of the polygon.

        The colors must be defined in the order RGBA and with values between 0 and 1.

        Args:
            polygon_id: Id of the polygon to change the color.
            color: List-like object with the colors to use.

        Returns: None
        """
        self.__engine.change_dot_color_of_polygon(polygon_id, color)

    def change_height_unit_current_3D_model(self, measure_unit: str) -> None:
        """
        Ask the engine to change the measure unit of the heights of the 3D model.

        Args:
            measure_unit: String representing the measure unit to change.

        Returns: None
        """

        if measure_unit == 'Meters':
            self.__engine.change_3D_model_height_unit(self.get_active_model_id(), 'meters')
        elif measure_unit == 'Kilometers':
            self.__engine.change_3D_model_height_unit(self.get_active_model_id(), 'kilometers')
        else:
            raise NotImplementedError(f'Measure {measure_unit} not implemented.')

    def change_map_position_unit_current_3D_model(self, measure_unit: str) -> None:
        """
        Change the measure unit used for the points on the map on the current 3D model.

        Args:
            measure_unit: String representing the measure unit to change.

        Returns: None
        """

        if measure_unit == 'Degrees':
            self.__engine.change_3D_model_position_unit(self.get_active_model_id(), 'degrees')
        elif measure_unit == 'UTM':
            self.__engine.change_3D_model_position_unit(self.get_active_model_id(), 'utm')
        else:
            raise NotImplementedError(f'Measure {measure_unit} not implemented.')

    def change_map_quality(self, quality: int) -> None:
        """
        Change the quality used to render the maps.

        Args:
            quality: Quality to use in the rendering process

        Returns: None
        """
        self.__engine.change_quality(quality)

    def create_model_from_existent(self, base_model_id: str, second_model_id: str, model_name: str) -> None:
        """
        Ask the engine to merge two maps into a new one.

        Args:
            base_model_id: ID of the model to use as base for the merging of the maps.
            second_model_id: ID of the model to use as the second model (the one who goes behind the base model).
            model_name: Name of the generated model.

        Returns: None
        """
        self.__engine.create_model_from_existent(base_model_id, second_model_id, model_name)

    def create_new_polygon(self, folder_id: str = None) -> str:
        """
        Create a new polygon on the program and add it to a folder to be shown in the GUI.

        If no folder is specified, a new folder is created.

        Returns: the id of the new polygon
        """
        polygon_id = self.__engine.create_new_polygon()
        self.add_polygon_to_gui(polygon_id, folder_id)
        return polygon_id

    def create_polygon_folder(self, name: str = 'folder') -> str:
        """
        Create a new folder in the list of polygons folders.

        Args:
            name: Name fot the folder.

        Returns: The folder created.
        """
        return self.__polygon_folder_manager.create_new_folder(name)

    def draw_frames(self) -> None:
        """
        Draw the components of the GUI (This dont render them).

        Returns: None
        """

        if self.__engine.get_program_view_mode() == ViewMode.mode_2d:
            components_to_draw = self.__component_list_2D
        elif self.__engine.get_program_view_mode() == ViewMode.mode_3d:
            components_to_draw = self.__component_list_3D
        else:
            raise NotImplementedError('ViewMode not implemented on the GUI.')

        imgui.new_frame()
        with imgui.font(self.__font_regular):
            for frame in components_to_draw:
                frame.render()
            for frame in components_to_draw:
                frame.post_render()
        imgui.end_frame()

        # check for the mouse component
        self.__is_mouse_inside_frame = imgui.get_io().want_capture_mouse

    def export_model_as_netcdf(self, model_id: str) -> None:
        """
        Ask the engine to export the model with the specified ID as  a netcdf file.

        Args:
            model_id: ID of the model to export.

        Returns: None
        """
        self.__engine.export_model_as_netcdf(model_id)

    def export_polygon_with_id(self, polygon_id: str) -> None:
        """
        Ask the engine to export the polygon with the given ID

        Args:
            polygon_id: ID of the polygon to export

        Returns: None
        """
        self.__engine.export_polygon_with_id(polygon_id)

    def export_polygons_inside_folder(self, polygon_folder_id: str) -> None:
        """
        Ask the engine to export a list of polygons to a shapefile file.

        Args:
            polygon_folder_id: ID of the folder containing the polygons.

        Returns: None
        """
        self.__engine.export_polygon_list_id(self.__polygon_folder_manager.get_polygon_id_list(polygon_folder_id),
                                             self.__polygon_folder_manager.get_name_of_folder(polygon_folder_id))

    def fix_frames_position(self, value: bool) -> None:
        """
        Set if the windows will be fixed on the screen or if they will be floating.

        Args:
            value: Boolean indicating if the windows will be fixed or not.

        Returns: None
        """
        log.debug(f"Changing fixed positions: {value}")

        # Settings change depending if the frames are fixed or not
        if value:
            self.__engine.fix_frames(True)
            self.__engine.update_scene_viewport()

        else:
            self.__engine.fix_frames(False)
            self.__engine.update_scene_viewport()

    def get_3d_model_list(self) -> List[str]:
        """
        Get the list of all 3D models generated in the program.

        Returns: List with the ID of the 3D models in the program.
        """
        return self.__engine.get_3d_model_list()

    def get_active_model_id(self) -> str:
        """
        Get the active model being used in the program

        Returns: active model id
        """
        return self.__engine.get_active_model_id()

    def get_active_polygon_id(self) -> str:
        """
        Get the active polygon id being used by the program.

        Returns:  id of the active polygon
        """
        return self.__engine.get_active_polygon_id()

    def get_active_tool(self) -> Union[Tools, None]:
        """
        Get the active tool being used in the program.

        Returns: Active tool being used.

        """
        return self.__engine.get_active_tool()

    def get_camera_data(self) -> dict:
        """
        Ask the engine for the data related to the camera.

        Returns: Data related to the camera.
        """
        return self.__engine.get_camera_data()

    def get_controller_keyboard_callback_state(self) -> bool:
        """
        Returns True if the keyboard callback defined by the controller (different from the one used by the GUI) is
        enabled. Return false if the keyboard callback defined by the controller is disabled.

        Returns: Boolean indicating the state of the controller keyboard callback.
        """
        return self.__engine.get_controller_key_callback_state()

    def get_cpt_file(self) -> str:
        """
        Get the CTP file used by the program.
        Returns: string with the file to use.

        """
        return self.__engine.get_cpt_file()

    def get_frame_fixed_state(self) -> bool:
        """
        Return the state of the frames. True if they are fixed (position and size can not be changed),  False  if not.

        Returns: if frames are fixed or not.
        """
        return self.__engine.are_frames_fixed()

    def get_gui_key_callback(self) -> callable:
        """
        Get the key callback defined by IMGUI.

        This callback is the one configured by IMGUI on GLFW, and thus, receives the same arguments that the one
        that GLFW defines.

        In detail, the function returned receives 5 parameters:
            window: GLFW window used in the application.
            key: Keyboard key pressed
            scancode: Platform specific scancode of the key pressed
            action: Action. GLFW_PRESS, GLFW_REPEAT or GLFW_RELEASE
            mods: Modifier bits.

        Returns: Function used by imgui for the key callback
        """
        return self.__implementation.keyboard_callback

    def get_gui_mouse_scroll_callback(self) -> callable:
        """
        Get the mouse scroll callback used by imgui.

        This callback is the one configured by IMGUI on GLFW, and thus, receives the same arguments that the one
        that GLFW defines.

        The function returned receives 3 parameters:
            window: GLFW window used in the application.
            x-offset: Movement of the scroll in the x-axis.
            y-offset: Movement of the scroll in the y-axis.

        Returns: Function used by imgui for the mouse scroll callback
        """
        return self.__implementation.scroll_callback

    def get_height_normalization_factor_of_active_3D_model(self) -> float:
        """
        Ask the engine for the normalization factor being used for the active 3D model.

        Returns: Normalization height factor being used by the active model.
        """
        return self.__engine.get_height_normalization_factor_of_active_3D_model()

    def get_icon(self, icon_name: str) -> Icon:
        """
        Get the icon with the given name.

        Args:
            icon_name: Name of the icon to ask for the id.

        Returns: Icon stored in the dictionary.
        """
        return self.__icons_dict[icon_name]

    def get_left_frame_width(self) -> int:
        """
        Get the width of the tools frame. This frame is located by default at the left of the window and does not
        share the space with the elements on the scene.

        If the frames are unfixed (the become movable) and the width of the Tools frame changes, the value returned
        does not change, returning the default width of the Tools frame when the frame are fixed.

        Returns: width of the left frame
        """
        return self.__engine.get_gui_setting_data()['LEFT_FRAME_WIDTH']

    def get_main_menu_bar_height(self) -> int:
        """
        Get the main menu bar height frm the settings.

        Returns: main_menu_bar height
        """
        return self.__engine.get_gui_setting_data()['MAIN_MENU_BAR_HEIGHT']

    def get_map_coordinates_from_window_coordinates(self, x_coordinate: int, y_coordinate: int) -> (float, float):
        """
        Get the position of a point in the map given in screen coordinates.

        Screen coordinates have the origin of the system at the top-left of the window, being the x-axis positive to
        the right and the y-axis positive to the bottom.

        The returned tuple is the real coordinates (coordinates used in the map) of the point specified in screen
        coordinates.

        If there is no map loaded on the program, then (None, None) is returned.

        Args:
            x_coordinate: x-axis component of the screen coordinate to evaluate on the map.
            y_coordinate: y-axis component of the screen coordinate to evaluate on the map.

        Returns: (x, y) tuple with the coordinates of the point on the map.
        """
        return self.__engine.get_map_coordinates_from_window_coordinates(x_coordinate, y_coordinate)

    def get_map_height_on_coordinates(self, x_coordinate: float, y_coordinate: float) -> float:
        """
        Get the height of the current active map on the specified coordinates.

        If there is no map loaded or the coordinates are outside of the map, then None is returned.

        Args:
            x_coordinate: x-axis coordinate.
            y_coordinate: y-axis coordinate.

        Returns: Height of the active model on the specified location.
        """
        return self.__engine.get_map_height_on_coordinates(x_coordinate, y_coordinate)

    def get_map_position(self) -> list:
        """
        The the position of the map in the program.

        Returns: list with the position of the map.
        """
        return self.__engine.get_map_position()

    def get_model_list(self) -> List[str]:
        """
        Get a list with the ID of all the 2D models loaded into the program.

        Returns: List of models loaded into the program.
        """
        return self.__model_id_list

    def get_model_names_dict(self) -> Dict[str, Union[str, None]]:
        """
        Get a dictionary with the models on the program and their names.

        The dictionary uses the models ID as the key and the name as the values of the dictionary.

        Returns: Dictionary with the ID of the models and the name of each one.
        """
        model_dict = {}

        for model_id in self.__model_id_list:
            model_info = self.__engine.get_model_information(model_id)
            model_dict[model_id] = model_info.get('name', None)

        return model_dict

    def get_polygon_folder_id_list(self) -> list:
        """
        Get a list of the ID of the folders in the GUI

        Returns: List of ids of folders
        """
        return self.__polygon_folder_manager.get_folder_id_list()

    def get_polygon_folder_name(self, polygon_folder_id: str) -> str:
        """
        Return the name of a polygon folder.

        Args:
            polygon_folder_id: ID of the polygon folder.

        Returns: Name of the folder
        """
        return self.__polygon_folder_manager.get_name_of_folder(polygon_folder_id)

    def get_polygon_id_list(self) -> list:
        """
        Get a list with all the IDs of the polygons being used by the program.

        Returns: list with the polygons
        """
        return self.__polygon_folder_manager.get_polygon_id_list()

    def get_polygon_name(self, polygon_id: str) -> str:
        """
        Get the name of a polygon given its id

        Args:
            polygon_id: Id of the polygon

        Returns: Name of the polygon
        """
        return self.__engine.get_polygon_name(polygon_id)

    def get_polygon_parameters(self, polygon_id: str) -> list:
        """
        Get the list of parameters of certain polygon.

        Returns: List with the parameters.
        """
        return self.__engine.get_parameters_from_polygon(polygon_id)

    def get_polygons_id_from_polygon_folder(self, polygon_folder_id: str) -> list:
        """
        Get a list with the IDs of the polygons stored inside a folder.

        Args:
            polygon_folder_id: ID of the polygon folder.

        Returns: List with the id of the polygons inside the folder.
        """
        return self.__polygon_folder_manager.get_polygon_id_list(polygon_folder_id)

    def get_program_view_mode(self) -> ViewMode:
        """
        Ask the engine for the view mode being used for the program.

        Returns: view mode being used by the program.
        """
        return self.__engine.get_program_view_mode()

    def get_quality(self) -> int:
        """
        Get the render quality used in the engine.

        Returns: Quality used in the engine.
        """
        return self.__engine.get_quality()

    def get_window_height(self) -> int:
        """
        Get the window height.

        Returns: Window height
        """
        data = self.__engine.get_window_setting_data()
        return data['HEIGHT']

    def get_window_width(self) -> int:
        """
        Get the window width.

        Returns: Window width
        """
        data = self.__engine.get_window_setting_data()
        return data['WIDTH']

    def get_zoom_level(self) -> float:
        """
        Get the zoom level being used in the program.

        Returns: zoom level

        """
        return self.__engine.get_zoom_level()

    def is_mouse_inside_frame(self) -> bool:
        """
        Check if the mouse is hovering a frame.

        Returns: Boolean indicating if the mouse is hovering a frame.
        """
        return self.__is_mouse_inside_frame

    def is_polygon_planar(self, polygon_id: str) -> bool:
        """
        Ask the engine if the polygon with the specified id is planar or not.

        Args:
            polygon_id: Id of the polygon.

        Returns: Boolean indicating if the polygon is planar or not.
        """

        return self.__engine.is_polygon_planar(polygon_id)

    def is_program_loading(self) -> bool:
        """
        Return if the program is loading or not.

        Returns: Boolean representing if the program is running or not.
        """
        return self.__engine.is_program_loading()

    def less_zoom(self) -> None:
        """
        Reduce on 1 the level of zoom.

        Returns: None
        """
        self.__engine.less_zoom()

    def load_netcdf_file_with_dialog(self):
        """
        Call for the engine to open a dialog text to load a new netcdf file.

        Returns: None
        """
        self.__engine.load_netcdf_file_with_dialog()

    def load_preview_interpolation_area(self, distance: float) -> None:
        """
        Ask the engine to load the interpolation area.

        Args:
            distance: Distance to use to calculate the interpolation area.

        Returns: None
        """
        self.__engine.create_preview_interpolation_area(distance)

    def load_shapefile_file_with_dialog(self) -> None:
        """
        Calls the engine to load a polygon from a shapefile file opening the dialog to select file.

        Returns: None
        """
        self.__engine.load_shapefile_file_with_dialog()

    def move_folder_position(self, polygon_folder_id: str, movement_offset: int) -> None:
        """
        Move the order of the folders on the GUI.

        Example:
            If the folders are arranged as follows:

                Folder 1
                Folder 2
                Folder 3

            Then, using a movement_offset of -2 in the Folder 3 will result in this:

                Folder 3
                Folder 2
                Folder 1

        This method change the order on which the polygons are draw on the scene.

        Args:
            polygon_folder_id: ID of the folder to move.
            movement_offset: How much to move the folder.

        Returns: None
        """

        # Move the folder on the manager
        self.__polygon_folder_manager.move_folder_position(polygon_folder_id, movement_offset)

        # Change the draw order of the polygons inside the folder
        for polygon_id in self.get_polygons_id_from_polygon_folder(polygon_folder_id):
            self.__engine.change_polygon_draw_priority(polygon_id,
                                                       self.__polygon_folder_manager.get_polygon_position(polygon_id))

    def move_model_position(self, model_id: str, offset: int) -> None:
        """
        Change the priority of the selected model, making the rendering of the model before/after the others models.

        The offset specify how many elements to move the element in the list of models. Can be a positive or negative
        integer.

        Args:
            model_id: ID of the model to change.
            offset: How many elements to move the selected model.

        Returns: None
        """
        # Rearrange the models in the GUI
        index = self.__model_id_list.index(model_id)
        self.__model_id_list.pop(index)
        self.__model_id_list.insert(index + offset, model_id)

        # Change the drawing priority on the Engine
        self.__engine.change_model_draw_priority(model_id, index + offset)

    def move_polygon_position(self, polygon_id: str, polygon_folder_id: str, movement_offset: int) -> None:
        """
        Move the polygon position inside the folder where it is located.

        If movement_offset is negative, then the polygon will be moved to the beginning of the folder, if it is
        positive, then it will be moved to the end of the folder.

        Examples:

            If the folder contains the following polygons:

                [polygon_1, polygon_2, polygon_3, polygon_4]

            then using movement_offset equal to -2 to move the polygon_4 will result in the folder containing the
            polygons in the following order:

                [polygon_1, polygon_4, polygon_2, polygon_3]

        This method change the draw order of the polygons.

        Args:
            polygon_id: ID of the polygon to move.
            polygon_folder_id: ID of the folder where the polygon is located.
            movement_offset: How many positions to move the polygon.

        Returns: None
        """

        # Move the position of the polygon in the respective folder
        self.__polygon_folder_manager.move_polygon_position(polygon_folder_id, polygon_id, movement_offset)

        # Update the draw order of the polygons
        self.__engine.change_polygon_draw_priority(polygon_id,
                                                   self.__polygon_folder_manager.get_polygon_position(polygon_id))

    def move_polygon_to_polygon_folder(self, old_folder_id: str, polygon_id: str, folder_id: str) -> None:
        """
        Move the polygon from one folder to another.

        This method also change the order in which the polygons are draw to match the ones showed in the GUI.

        Args:
            old_folder_id: ID of the folder where the polygon is
            polygon_id: Polygon to move
            folder_id: ID of the folder to move the polygon to

        Returns: None
        """

        # Move the polygon from one folder to the other
        # ---------------------------------------------
        self.__polygon_folder_manager.move_polygon_to_folder(old_folder_id, polygon_id, folder_id)

        # Change the draw order of the polygon to match the showed folder on the GUI
        # --------------------------------------------------------------------------
        self.__engine.change_polygon_draw_priority(polygon_id,
                                                   self.__polygon_folder_manager.get_polygon_position(polygon_id))

    def open_combine_map_modal(self) -> None:
        """
        Open the modal to merge two maps into one.

        Returns:  None
        """
        self.__combine_map_modal.should_show = True

    def open_confirmation_modal(self, modal_title: str, msg: str, yes_function: callable,
                                no_function: callable) -> None:
        """
        Opens a confirmation modal in the screen with two options (yes and no), after clicking each one execute the
        functions given.

        Args:
            modal_title: Title of the modal.
            msg: Message to use in the modal.
            yes_function: Function to execute when pressed yes.
            no_function: Function to execute when pressed no.

        Returns: None
        """
        log.debug('Setting confirmation modal')

        for frame in self.__component_list_2D:
            if isinstance(frame, ConfirmationModal):
                frame.set_confirmation_text(modal_title, msg, yes_function, no_function)
                return

        raise AssertionError('There is not a frame of class ConfirmationModal in the program.')

    def open_text_modal(self, modal_title: str, msg: str) -> None:
        """
        Set the text of the modal frame and set it to show in the next frame.

        Returns: None

        Args:
            modal_title:  title to use in the modal
            msg: message to show in the modal
        """
        log.debug("Setting modal text")

        for frame in self.__component_list_2D:
            if isinstance(frame, TextModal):
                frame.set_modal_text(modal_title, msg)
                return

        raise AssertionError('There is not a frame from the TextModal class to set a modal message.')

    def optimize_gpu_memory(self) -> None:
        """
        Calls the engine to optimize the memory on the GPU.

        Returns: None
        """
        self.__engine.optimize_gpu_memory()

    def process_input(self) -> None:
        """
        Process the input (events) that happened in the GUI.

        Returns: None
        """
        self.__implementation.process_inputs()

    def reload_models(self):
        """
        Ask the Engine to reload the models into a better definition.

        NOTE:
            This method will create a loading frame on the application while the models are being reloaded.

        IMPORTANT:
            This method is asynchronous, this is, the logic that make the reload of the models run in another thread
            while the main thread will still render the program in real time.

        Returns: None
        """
        self.__engine.reload_models()

    def remove_all_polygons_inside_folder(self, polygon_folder_id: str) -> None:
        """
        Remove all the polygons that are inside a folder from the system and from the folder.

        If the polygon is on two folders at the same time (should not happen), this also deletes
        the polygon from the other folder.

        Args:
            polygon_folder_id: PolygonFolder ID of the folder to use.

        Returns: None
        """

        polygons_inside = self.__polygon_folder_manager.get_polygon_id_list(polygon_folder_id).copy()
        for polygon_id in polygons_inside:
            self.remove_polygon_by_id(polygon_id)

    def remove_interpolation_preview(self, polygon_id: str) -> None:
        """
        Ask the engine to remove the interpolation preview of the specified polygon.

        Do nothing if there is no interpolation area being showed.

        Args:
            polygon_id: Polygon id to delete the area.

        Returns: None
        """
        self.__engine.remove_interpolation_preview(polygon_id)

    def remove_model(self, model_id: str) -> None:
        """
        Ask the engine to remove the model with the specified ID.

        This method removes the 2D model and the 3D model if ti exists.

        Args:
            model_id: ID of the model to remove.

        Returns: None
        """
        self.__model_id_list.remove(model_id)
        self.__engine.remove_model(model_id)

    def remove_polygon_by_id(self, polygon_id: str) -> None:
        """
        Remove the polygon with the specified id from the scene and the GUIManager.

        Args:
            polygon_id: Id of the polygon to delete

        Returns: None
        """
        # delete it from the folders
        self.__polygon_folder_manager.delete_polygon_from_all_folders(polygon_id)

        # delete the polygon from the engine
        self.__engine.remove_polygon_by_id(polygon_id)

    def remove_polygon_folder(self, folder_id: str) -> None:
        """
        Remove a polygon folder from the list of folders.

        Args:
            folder_id: ID of the folder to delete.

        Returns: None
        """
        self.remove_all_polygons_inside_folder(folder_id)
        self.__polygon_folder_manager.delete_folder(folder_id)

    def remove_polygon_parameter(self, polygon_id: str, key: str) -> None:
        """
        Remove a parameter from a polygon.

        Args:
            polygon_id: ID of the polygon.
            key: key to delete.

        Returns: None
        """
        self.__engine.remove_parameter_from_polygon(polygon_id, key)

    def render(self) -> None:
        """
        Render the GUI (Components must be drew first).

        Returns: None
        """
        imgui.render()
        self.__implementation.render(imgui.get_draw_data())

    def reset_camera_values(self) -> None:
        """
        Ask the engine to reset the values of the camera to it's initial values.

        Returns: None
        """
        self.__engine.reset_camera_values()

    def set_active_model(self, model_id: str) -> None:
        """
        Change the active model being used by the program.

        Args:
            model_id: ID of the model to set as active.

        Returns: None
        """
        self.__engine.set_active_model(model_id)

    def set_active_polygon(self, polygon_id: Union[str, None]) -> None:
        """
        Set a new active polygon on the program.

        Args:
            polygon_id: Polygon ID to set as the active polygon.

        Returns: None
        """
        self.__engine.set_active_polygon(polygon_id)

    def set_active_tool(self, tool: Union[Tools, None]) -> None:
        """
        Set the active tool on the engine.

        Args:
            tool: String representing the new tool too be active.

        Returns: None
        """
        self.__engine.set_active_tool(tool)

    def set_bold_font(self) -> None:
        """
        Set a bold font to use in the render on the GUI.

        Returns: Set the font to bold.
        """
        imgui.pop_font()
        imgui.push_font(self.__font_bold)

    def set_controller_keyboard_callback_state(self, new_state: bool) -> None:
        """
        Enable/Disable the logic defined on the controller keyboard callback.

        This method should be called after disable_controller_keyboard_callback to return the keyboard callbacks to its
        normal state.

        Args:
            new_state: New state of the keyboard callback used by the controller.

        Returns: None
        """
        self.__engine.set_controller_key_callback(new_state)

    def set_loading_message(self, new_msg: str) -> None:
        """
        Set a new loading message in the loading frame.

        Args:
            new_msg: New message to show in the frame.

        Returns: None
        """
        for frame in self.__component_list_2D:
            if isinstance(frame, Loading):
                frame.set_loading_message(new_msg)
                return

        raise AssertionError('There is not a frame from the Loading class on the list of frames '
                             'handled by the GUIManager.')

    def set_models_polygon_mode(self, polygon_mode: OGLConstant.IntConstant) -> None:
        """
        Call the scene to change the polygon mode used by the models.

        The polygon mode must be one of the following constants defined in the opengl library:
            - GL_POINT
            - GL_LINE
            - GL_FILL

        Args:
            polygon_mode: Polygon mode to use.

        Returns:
        """
        self.__engine.set_models_polygon_mode(polygon_mode)

    def set_polygon_folder_name(self, polygon_folder_id: str, new_name: str) -> None:
        """
        Change the name of a polygon folder.

        Args:
            new_name: New name of the folder.
            polygon_folder_id: ID of the polygon folder to change the name to.

        Returns: None
        """
        self.__polygon_folder_manager.set_name_of_folder(polygon_folder_id, new_name)

    def set_polygon_name(self, polygon_id: str, new_name: str) -> None:
        """
        Change the name of a polygon.

        Args:
            polygon_id: Old polygon id
            new_name: New polygon id

        Returns: None
        """
        self.__engine.set_polygon_name(polygon_id, new_name)

    def set_polygon_parameter(self, polygon_id: str, key: str, value: any) -> None:
        """
        Set a new parameter to the polygon.

        Args:
            polygon_id: ID of the polygon.
            value: Value of the new polygon.
            key: Key to the new polygon.

        Returns: None
        """
        self.__engine.set_new_parameter_to_polygon(polygon_id, key, value)

    def set_program_view_mode(self, mode: 'ViewMode') -> None:
        """
        Ask the engine to change the view mode to the selected mode.

        Args:
            mode: New mode to use in the program.

        Returns: None
        """
        self.__engine.set_program_view_mode(mode)

    def set_regular_font(self) -> None:
        """
        Set the regular font too use in the render.

        Returns: Set the font to bold.
        """
        imgui.pop_font()
        imgui.push_font(self.__font_regular)

    def set_tool_sub_title_font(self) -> None:
        """
        Set the font to use of the type sub_title.

        The font will be smaller than the title font but bigger than the regular text.

        Returns: None
        """
        imgui.pop_font()
        imgui.push_font(self.__font_tool_sub_title)

    def set_tool_title_font(self) -> None:
        """
        Set the font to use for the tool titles.

        Returns: None
        """
        imgui.pop_font()
        imgui.push_font(self.__font_tool_title)

    def undo_action(self) -> None:
        """
        Call the engine to undo the most recent action made on the program.

        Returns: None
        """
        self.__engine.undo_action()

    def update_current_3D_model(self) -> None:
        """
        Ask the engine to update the current 3D model.

        Returns: None
        """
        self.__engine.update_current_3D_model()
