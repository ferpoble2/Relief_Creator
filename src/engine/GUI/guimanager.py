"""
File with the class that will manage the state of the GUI.
"""
import OpenGL.constant as OGLConstant
import imgui
from imgui.integrations.glfw import GlfwRenderer

from src.engine.GUI.frames.main_menu_bar import MainMenuBar
from src.engine.GUI.frames.tools import Tools
from src.engine.GUI.frames.debug import Debug
from src.engine.GUI.frames.loading import Loading
from src.engine.GUI.frames.text_modal import TextModal
from src.engine.GUI.frames.test_window import TestWindow
from src.utils import get_logger
from src.engine.GUI.icon import Icon
from src.engine.GUI.polygon_folder import PolygonFolder

from src.error.polygon_folder_not_found_error import PolygonFolderNotFoundError

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

        self.__polygon_folder_list = []
        self.__folder_id_counter = 0

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

    def __get_polygon_folder_list(self) -> list:
        """
        Get the  list of polygon folders.

        Returns: List of polygon folders.
        """
        return self.__polygon_folder_list

    def add_frames(self, component_list: list) -> None:
        """
        Add frames to render in the application.

        Receive a list of components that must inherit from the Frame class.

        Args:
            component_list: List of frames to render.

        Returns: None
        """
        for frame in component_list:
            self.__component_list.append(frame)

    def add_polygon_to_gui(self, polygon_id) -> None:
        """
        Tells the frames that make use of the polygon information that a new polygon was created.

        Args:
            polygon_id: Id of the created polygon

        Returns: None
        """

        for frame in self.__component_list:
            if isinstance(frame, Tools):
                frame.add_new_polygon(polygon_id)

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

    def create_polygon_folder(self, name: str = 'folder') -> PolygonFolder:
        """
        Create a new folder in the list of polygons folders.

        Args:
            name: Name fot the folder.

        Returns: The folder created.
        """
        new_polygon_folder = PolygonFolder(str(self.__folder_id_counter))
        self.__folder_id_counter += 1

        new_polygon_folder.set_name(name)

        self.__polygon_folder_list.append(new_polygon_folder)

        return new_polygon_folder

    def delete_all_polygons_inside_folder(self, polygon_folder_id: str) -> None:
        """
        Delete all the polygons that are inside a folder from the system and from the folder.

        Args:
            polygon_folder_id: PolygonFolder ID of the folder to use.

        Returns: None
        """
        for folder in self.__get_polygon_folder_list():
            if folder.get_id() == polygon_folder_id:
                for polygon_id in folder.get_polygon_list():
                    self.delete_polygon_by_id(polygon_id)
                return

        raise PolygonFolderNotFoundError(f'Folder {polygon_folder_id} not found in the program.')

    def delete_polygon_by_id(self, polygon_id: str) -> None:
        """
        Delete the polygon with the specified id from the scene

        Args:
            polygon_id: Id of the polygon to delete

        Returns: None
        """
        # search for the polygon on the folders and delete it
        for folder in self.__get_polygon_folder_list():
            if polygon_id in folder.get_polygon_list():
                folder.delete_polygon(polygon_id)

        # delete the polygon from the engine
        self.__engine.delete_polygon_by_id(polygon_id)

    def delete_polygon_folder(self, folder_id: str) -> None:
        """
        Delete a polygon folder from the list of folders.

        Args:
            folder_id: ID of the folder to delete.

        Returns: None
        """
        for folder in self.__polygon_folder_list:
            if folder.get_id() == folder_id:
                self.__polygon_folder_list.remove(folder)
                return

        raise PolygonFolderNotFoundError('Folder is not in the list of folders...')

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

    def export_polygon_with_id(self, polygon_id: str) -> None:
        """
        Ask the engine to export the polygon with the given ID

        Args:
            polygon_id: ID of the polygon to export

        Returns: None
        """
        self.__engine.export_polygon_with_id(polygon_id)

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

    def get_frames(self, gui_manager: 'GUIManager') -> list:
        """
        Return the frame object to use in the application.

        Args:
            gui_manager: GUIManager to use to initialize the frames.

        Returns: list with the frame objects.
        """
        return [
            MainMenuBar(gui_manager),
            # TestWindow(gui_manager),
            TextModal(gui_manager),
            Tools(gui_manager),
            Debug(gui_manager),
            Loading(gui_manager),
        ]

    def get_gui_key_callback(self) -> callable:
        """
        Get the key callback used by imgui.

        Returns: Function used by imgui for the key callback
        """
        return self.__implementation.keyboard_callback

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
        Get the main menu bar heigh frm the settings.

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
        return [folder.get_id() for folder in self.__get_polygon_folder_list()]

    def get_polygons_id_from_polygon_folder(self, polygon_folder_id: str) -> list:
        """
        Get the list of polygons id that a folder contains.

        Args:
            polygon_folder_id: ID of the polygon folder.

        Returns: List with the id of the polygons inside the folder.
        """
        for folder in self.__get_polygon_folder_list():
            if folder.get_id() == polygon_folder_id:
                return folder.get_polygon_list()

        raise PolygonFolderNotFoundError(f'Folder {polygon_folder_id} not found in the program.')

    def get_polygon_folder_name(self, polygon_folder_id: str) -> None:
        """
        Return the name of a polygon folder.

        Args:
            polygon_folder_id: ID of the polygon folder.

        Returns: Name of the folder
        """
        for folder in self.__get_polygon_folder_list():
            if folder.get_id() == polygon_folder_id:
                return folder.get_name()

        raise PolygonFolderNotFoundError('Polygon folder not found')

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

    def initialize(self, window, engine: 'Engine') -> None:
        """
        Set the initial configurations of the GUI.

        Args:
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
        self.__implementation.refresh_font_texture()

        # load the icons on the GUI
        self.__load_icons()

        self.__engine = engine

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

    def set_models_polygon_mode(self, polygon_mode: OGLConstant.IntConstant) -> None:
        """
        Call the scene to change the polygon mode used by the models.

        Args:
            polygon_mode: Polygon mode to use.

        Returns:
        """
        self.__engine.set_models_polygon_mode(polygon_mode)

    def set_polygon_name(self, polygon_id: str, new_name: str) -> None:
        """
        Change the name of a polygon.

        Args:
            polygon_id: Old polygon id
            new_name: New polygon id

        Returns: None
        """
        self.__engine.set_polygon_name(polygon_id, new_name)

    def set_regular_font(self) -> None:
        """
        Set the regular font too use in the render.

        Returns: Set the font to bold.
        """
        imgui.pop_font()
        imgui.push_font(self.__font_regular)

    def set_polygon_folder_name(self, polygon_folder_id: str, new_name: str) -> None:
        """
        Change the name of a polygon folder.

        Args:
            new_name: New name of the folder.
            polygon_folder_id: ID of the polygon folder to change the name to.

        Returns: None
        """
        for folder in self.__get_polygon_folder_list():
            if folder.get_id() == polygon_folder_id:
                folder.set_name(new_name)
                return

        raise PolygonFolderNotFoundError(f'Can not find folder {polygon_folder_id} in the program.')

    def undo_action(self) -> None:
        """
        Call the engine to undo the most recent action made on the program.

        Returns: None
        """
        self.__engine.undo_action()
