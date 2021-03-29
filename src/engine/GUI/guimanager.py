"""
File with the class that will manage the state of the GUI.
"""
# noinspection PyPep8Naming
import OpenGL.constant as OGLConstant
import imgui
from imgui.integrations.glfw import GlfwRenderer

from src.error.WrongInterpolationTypeError import WrongInterpolationTypeError

from src.engine.GUI.frames.main_menu_bar import MainMenuBar
from src.engine.GUI.frames.tools.tools import Tools
from src.engine.GUI.frames.debug import Debug
from src.engine.GUI.frames.loading import Loading
from src.engine.GUI.frames.text_modal import TextModal
from src.engine.GUI.frames.test_window import TestWindow
from src.engine.GUI.frames.polygon_information import PolygonInformation
from src.engine.GUI.frames.confirmation_modal import ConfirmationModal
from src.utils import get_logger
from src.engine.GUI.icon import Icon
from src.engine.GUI.polygon_folder_manager import PolygonFolderManager

# noinspection SpellCheckingInspection
log = get_logger(module='GUIMANAGER')


# noinspection PyMethodMayBeStatic
class GUIManager:
    """
    Class to manage all the UI configurations and functions.
    """

    def __init__(self):
        """
        Constructor of the class.

        """
        self.__implementation = None
        self.__glfw_window = None
        self.__component_list = []
        self.__io = None
        self.__font_regular = None
        self.__font_bold = None
        self.__font_tool_title = None

        self.__is_mouse_inside_frame = False

        self.__polygon_folder_manager = PolygonFolderManager()

        self.__icons_dict = None

        self.__engine = None

    def __load_icons(self) -> None:
        """
        Load the icons in the icons dictionary.

        Returns: None
        """
        self.__icons_dict = {
            'warning': Icon('./engine/GUI/icons/warning.png')
        }

    def __update_frames_with_new_polygon(self, polygon_id: str) -> None:
        """
        Update the frames with the new polygon, calling the corresponding method by class.

        Args:
            polygon_id: ID of the new polygon.

        Returns: None
        """
        for frame in self.__component_list:
            frame.add_new_polygon(polygon_id)

    def add_imported_polygon(self, polygon_id: str) -> None:
        """
        Add the polygon to the folder that stores the imported polygons and update all the frames with the new
        polygon.

        If the folder do not exist, then it is created.

        Args:
            polygon_id: ID of the polygon to add.

        Returns: None
        """
        self.__polygon_folder_manager.add_polygon_to_imported_polygon_folder(polygon_id)

        # update gui
        self.__update_frames_with_new_polygon(polygon_id)

    def add_polygon_to_gui(self, polygon_id: str) -> None:
        """
        Tells the frames that make use of the polygon information that a new polygon was created.

        Args:
            polygon_id: Id of the created polygon

        Returns: None
        """
        folder_id = self.__polygon_folder_manager.create_new_folder('New Folder')
        self.__polygon_folder_manager.add_polygon_to_folder(folder_id, polygon_id)

        # update gui
        self.__update_frames_with_new_polygon(polygon_id)

    def add_polygon_to_polygon_folder(self, folder_id: str, polygon_id: str) -> None:
        """
        Add an already existent polygon to the specified folder.

        Args:
            folder_id: Folder to use
            polygon_id: Polygon to add to the folder

        Returns: None
        """
        self.__polygon_folder_manager.add_polygon_to_folder(folder_id, polygon_id)

    def add_zoom(self) -> None:
        """
        Add zoom to the current map being watched.

        Returns: None
        """
        self.__engine.add_zoom()

    def are_frame_fixed(self) -> bool:
        """
        Check if the frames are fixed or not.

        Returns: if frames are fixed or not.
        """
        return self.__engine.are_frames_fixed()

    def calculate_max_min_height(self, model_id: str, polygon_id: str) -> tuple:
        """
        Ask the engine for max and min values of the vertices that are inside the polygon.

        Args:
            model_id: ID of the model to use.
            polygon_id: ID of the polygon to use.

        Returns: tuple with the max and min value.
        """
        return self.__engine.calculate_max_min_height(model_id, polygon_id)

    def change_color_file_with_dialog(self) -> None:
        """
        Change the color file to the one selected.
        This change all the models using the color file.

        Returns: None
        """
        self.__engine.change_color_file_with_dialog()

    def change_color_of_polygon(self, polygon_id: str, color: list) -> None:
        """
        Change the color of the polygon with the specified id.

        Only change the color of the lines of the polygon.

        The colors must be defined in the order RGBA and with values between 0 and 1.

        Args:
            polygon_id: Id of the polygon to change the color.
            color: List-like object with the colors to use.

        Returns: None
        """
        self.__engine.change_color_of_polygon(polygon_id, color)

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

    def change_points_height(self, polygon_id: str, model_id: str, min_height: float, max_height: float,
                             interpolation_type: 'str' = 'linear') -> None:
        """
        Call the engine to change the height of the points inside the specified polygon.

        Call a different function depending on the type of interpolation.
        Types can have the following values:
            - linear


        Args:
            model_id: ID of the model to use for the interpolation.
            polygon_id: ID of the polygon to use for interpolation.
            min_height: Min height of the points after the interpolation.
            max_height: Max height of the points after the interpolation.
            interpolation_type: Type of interpolation to use.

        Returns: None
        """

        if interpolation_type == 'linear':
            self.__engine.transform_points_using_linear_transformation(polygon_id, model_id, min_height, max_height)
            return

        raise WrongInterpolationTypeError(
            f'Interpolation of type {interpolation_type} is not admitted by the program.')

    def change_quality(self, quality: int) -> None:
        """
        Change the quality used to render the maps.

        Args:
            quality: Quality to use in the rendering process

        Returns: None
        """
        self.__engine.change_quality(quality)

    def create_new_polygon(self) -> str:
        """
        Create a new polygon on the scene

        Returns: the id of the new polygon
        """
        return self.__engine.create_new_polygon()

    def create_polygon_folder(self, name: str = 'folder') -> str:
        """
        Create a new folder in the list of polygons folders.

        Args:
            name: Name fot the folder.

        Returns: The folder created.
        """
        return self.__polygon_folder_manager.create_new_folder(name)

    def delete_all_polygons_inside_folder(self, polygon_folder_id: str) -> None:
        """
        Delete all the polygons that are inside a folder from the system and from the folder.

        If the polygon is on two folders at the same time (should not happen), this also deletes
        the polygon from the other folder.

        Args:
            polygon_folder_id: PolygonFolder ID of the folder to use.

        Returns: None
        """

        polygons_inside = self.__polygon_folder_manager.get_polygon_id_list(polygon_folder_id).copy()
        for polygon_id in polygons_inside:
            self.delete_polygon_by_id(polygon_id)

    def delete_polygon_by_id(self, polygon_id: str) -> None:
        """
        Delete the polygon with the specified id from the scene

        Args:
            polygon_id: Id of the polygon to delete

        Returns: None
        """
        # delete it from the folders
        self.__polygon_folder_manager.delete_polygon_from_all_folders(polygon_id)

        # delete the polygon from the engine
        self.__engine.delete_polygon_by_id(polygon_id)

    def delete_polygon_folder(self, folder_id: str) -> None:
        """
        Delete a polygon folder from the list of folders.

        Args:
            folder_id: ID of the folder to delete.

        Returns: None
        """
        self.__polygon_folder_manager.delete_folder(folder_id)

    def delete_polygon_parameter(self, polygon_id: str, key: str) -> None:
        """
        Delete a parameter from a polygon.

        Args:
            polygon_id: ID of the polygon.
            key: key to delete.

        Returns: None
        """
        self.__engine.delete_parameter_from_polygon(polygon_id, key)

    def draw_frames(self) -> None:
        """
        Draw the components of the GUI (This dont render them).

        Returns: None
        """
        imgui.new_frame()
        with imgui.font(self.__font_regular):
            for frame in self.__component_list:
                frame.render()
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

    def get_active_tool(self) -> str:
        """
        Get the active tool being used in the program.

        Returns: Active tool being used.

        """
        return self.__engine.get_active_tool()

    def get_cpt_file(self) -> str:
        """
        Get the CTP file used by the program.
        Returns: string with the file to use.

        """
        return self.__engine.get_cpt_file()

    def get_gui_key_callback(self) -> callable:
        """
        Get the key callback used by imgui.

        Returns: Function used by imgui for the key callback
        """
        return self.__implementation.keyboard_callback

    def get_gui_mouse_scroll_callback(self) -> callable:
        """
        Get the mouse scroll callback used by imgui.

        Returns: Function used by imgui for the mouse scroll callback
        """
        return self.__implementation.scroll_callback

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
        Get the width of the left frame.

        Returns: width of the left frame
        """
        return self.__engine.get_gui_setting_data()['LEFT_FRAME_WIDTH']

    def get_main_menu_bar_height(self) -> int:
        """
        Get the main menu bar height frm the settings.

        Returns: main_menu_bar height
        """
        return self.__engine.get_gui_setting_data()['MAIN_MENU_BAR_HEIGHT']

    def get_map_position(self) -> list:
        """
        The the position of the map in the program.

        Returns: list with the position of the map.
        """
        return self.__engine.get_map_position()

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
        Get the full list of polygon ids currently being used on the program.

        Returns: list with the polygons
        """
        return self.__engine.get_polygon_id_list()

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
        Get the list of polygons id that a folder contains.

        Args:
            polygon_folder_id: ID of the polygon folder.

        Returns: List with the id of the polygons inside the folder.
        """
        return self.__polygon_folder_manager.get_polygon_id_list(polygon_folder_id)

    def get_quality(self) -> int:
        """
        Get the render quality used in the engine.

        Returns: Quality used in the engine.
        """
        return self.__engine.get_quality()

    def get_view_mode(self) -> str:
        """
        Get the view mode being used in the platform.

        Returns: View mode being used.
        """
        return self.__engine.get_view_mode()

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

    # noinspection PyUnresolvedReferences
    def initialize(self, window, engine: 'Engine', gui_manager: 'GUIManager') -> None:
        """
        Set the initial configurations of the GUI.

        Args:
            gui_manager: The object used to make this call.
            engine: Engine used in the application
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
            './engine/GUI/fonts/open_sans/OpenSans-Regular.ttf', engine.get_font_size()
        )
        self.__font_bold = self.__io.fonts.add_font_from_file_ttf(
            './engine/GUI/fonts/open_sans/OpenSans-Bold.ttf', engine.get_font_size()
        )
        self.__font_tool_title = self.__io.fonts.add_font_from_file_ttf(
            './engine/GUI/fonts/open_sans/OpenSans-Regular.ttf', engine.get_tool_title_font_size()
        )

        self.__implementation.refresh_font_texture()

        # load the icons on the GUI
        self.__load_icons()
        self.get_gui_mouse_scroll_callback()

        # set the engine
        self.__engine = engine

        # initialize the components of the manager
        # ----------------------------------------
        self.__component_list = [
            MainMenuBar(gui_manager),
            TestWindow(gui_manager),
            TextModal(gui_manager),
            Tools(gui_manager),
            Debug(gui_manager),
            Loading(gui_manager),
            PolygonInformation(gui_manager),
            ConfirmationModal(gui_manager)
        ]

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

    def load_shapefile_file_with_dialog(self) -> None:
        """
        Calls the engine to load a polygon from a shapefile file opening the dialog to select file.

        Returns: None
        """
        self.__engine.load_shapefile_file_with_dialog()

    def move_polygon_to_polygon_folder(self, old_folder_id: str, polygon_id: str, folder_id: str) -> None:
        """
        Move the polygon from one folder to another.

        Args:
            old_folder_id: ID of the folder where the polygon is
            polygon_id: Polygon to move
            folder_id: ID of the folder to move the polygon to

        Returns: None
        """
        self.__polygon_folder_manager.move_polygon_to_folder(old_folder_id, polygon_id, folder_id)

    def optimize_gpu_memory(self) -> None:
        """
        Calls the engine to optimize the memory on the GPU

        Returns: None
        """
        self.__engine.optimize_gpu_memory()

    def process_input(self) -> None:
        """
        Process the input (events) that happened in the GUI.

        Returns: None
        """
        self.__implementation.process_inputs()

    def refresh_scene_with_model_2d(self, path_color_file: str, path_model: str, model_id: str = 'main') -> None:
        """
        Refresh the scene with the model 2D specified.

        Args:
            model_id: Id to use in the model.
            path_color_file: Path to CTP file.
            path_model: Path to the netCDF with the info of the model

        Returns: None

        """
        self.__engine.refresh_with_model_2d(path_color_file, path_model, model_id)

    def reload_models(self):
        """
        Ask the Scene to reload the models to better the definitions.

        Returns: None
        """
        self.__engine.reload_models()

    def render(self) -> None:
        """
        Render the GUI (Components must be drew first).

        Returns: None
        """
        imgui.render()
        self.__implementation.render(imgui.get_draw_data())

    def set_active_polygon(self, polygon_id: str) -> None:
        """
        Set a new active polygon on the program.

        Args:
            polygon_id: Polygon ID to set as the active polygon.

        Returns: None
        """
        self.__engine.set_active_polygon(polygon_id)

    def set_active_tool(self, tool: str) -> None:
        """
        Set the active tool on the engine.

        Args:
            tool: String representing the new tool too be active.

        Returns: None
        """
        self.__engine.set_active_tool(tool)

    def set_bold_font(self) -> None:
        """
        Set a bold font too use in the render.

        Returns: Set the font to bold.
        """
        imgui.pop_font()
        imgui.push_font(self.__font_bold)

    def set_confirmation_modal(self, modal_title: str, msg: str, yes_function: callable, no_function: callable) -> None:
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

        for frame in self.__component_list:
            if isinstance(frame, ConfirmationModal):
                frame.set_confirmation_text(modal_title, msg, yes_function, no_function)
                return

        raise AssertionError('There is not a frame of class ConfirmationModal in the program.')

    def set_loading_message(self, new_msg: str) -> None:
        """
        Set a new loading message in the loading frame.

        Args:
            new_msg: New message to show in the frame.

        Returns: None
        """
        for frame in self.__component_list:
            if isinstance(frame, Loading):
                frame.set_loading_message(new_msg)
                return

        raise AssertionError('There is not a frame from the Loading class to set a loading message.')

    def set_modal_text(self, modal_title: str, msg: str) -> None:
        """
        Set the text of the modal frame and set it to show in the next frame.

        Returns: None

        Args:
            modal_title:  title to use in the modal
            msg: message to show in the modal
        """
        log.debug("Setting modal text")

        for frame in self.__component_list:
            if isinstance(frame, TextModal):
                frame.set_modal_text(modal_title, msg)
                return

        raise AssertionError('There is not a frame from the TextModal class to set a modal message.')

    def set_models_polygon_mode(self, polygon_mode: OGLConstant.IntConstant) -> None:
        """
        Call the scene to change the polygon mode used by the models.

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

    def set_regular_font(self) -> None:
        """
        Set the regular font too use in the render.

        Returns: Set the font to bold.
        """
        imgui.pop_font()
        imgui.push_font(self.__font_regular)

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

    def interpolate_points(self, polygon_id: str, model_id: str, distance: str) -> None:
        """
        Call the engine to interpolate the points using the specified polygons and the specified distance.

        Args:
            model_id: ID of the model to use.
            polygon_id: ID of the polygon.
            distance: Distance to use for the interpolation.

        Returns: None
        """
        self.__engine.interpolate_points(polygon_id, model_id, distance)
