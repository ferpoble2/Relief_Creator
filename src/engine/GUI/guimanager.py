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
from src.engine.GUI.frames.test_window import TestWindow
from src.utils import get_logger

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
        self.__font = None

        self.__scene = None
        self.__engine = None

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

    def are_frame_fixed(self) -> bool:
        """
        Check if the frames are fixed or not.

        Returns: if frames are fixed or not.
        """
        return self.__engine.are_frames_fixed()

    def draw_frames(self) -> None:
        """
        Draw the components of the GUI (This dont render them).

        Returns: None
        """
        imgui.new_frame()
        with imgui.font(self.__font):
            for frame in self.__component_list:
                frame.render()
        imgui.end_frame()

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
            self.__scene.update_viewport()

        else:
            self.__engine.fix_frames(False)
            self.__scene.update_viewport()

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
            Tools(gui_manager),
            Debug(gui_manager),
            Loading(gui_manager)
        ]

    def is_program_loading(self) -> bool:
        """
        Return if the program is loading or not.

        Returns: Boolean representing if the program is running or not.
        """
        return self.__engine.is_program_loading()

    def change_quality(self, quality: int) -> None:
        """
        Change the quality used to render the maps.

        Args:
            quality: Quality to use in the rendering process

        Returns: None
        """
        self.__engine.change_quality(quality)

    def get_quality(self) -> int:
        """
        Get the render quality used in the engine.

        Returns: Quality used in the engine.
        """
        return self.__engine.get_quality()

    def get_window_width(self) -> int:
        """
        Get the window width.

        Returns: Window width
        """
        data = self.__engine.get_window_setting_data()
        return data['WIDTH']

    def get_window_height(self) -> int:
        """
        Get the window height.

        Returns: Window height
        """
        data = self.__engine.get_window_setting_data()
        return data['HEIGHT']

    def get_active_tool(self) -> str:
        """
        Get the active tool being used in the program.

        Returns: Active tool being used.

        """
        return self.__engine.get_active_tool()

    def get_zoom_level(self) -> float:
        """
        Get the zoom level being used in the program.

        Returns: zoom level

        """
        return self.__engine.get_zoom_level()

    def get_map_position(self) -> list:
        """
        The the position of the map in the program.

        Returns: list with the position of the map.
        """
        return self.__engine.get_map_position()

    def get_view_mode(self) -> str:
        """
        Get the view mode being used in the platform.

        Returns: View mode being used.
        """
        return self.__engine.get_view_mode()

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

    def get_cpt_file(self) -> str:
        """
        Get the CTP file used by the program.
        Returns: string with the file to use.

        """
        return self.__engine.get_cpt_file()

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
        self.__font = self.__io.fonts.add_font_from_file_ttf(
            './engine/GUI/fonts/open_sans/OpenSans-Regular.ttf', engine.get_font_size()
        )
        self.__implementation.refresh_font_texture()

        self.__scene = engine.scene
        self.__engine = engine

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

    def add_zoom(self) -> None:
        """
        Add zoom to the current map being watched.

        Returns: None
        """
        self.__engine.add_zoom()

    def less_zoom(self) -> None:
        """
        Reduce on 1 the level of zoom.

        Returns: None
        """
        self.__engine.less_zoom()

    def change_color_file(self, path_color_file: str) -> None:
        """
        Change the color file to the one selected.
        This change all the models using the color file.

        Args:
            path_color_file: Path to the color file to use.

        Returns: None
        """
        self.__engine.change_color_file(path_color_file)

    def render(self) -> None:
        """
        Render the GUI (Components must be drew first).

        Returns: None
        """
        imgui.render()
        self.__implementation.render(imgui.get_draw_data())

    def reload_models(self):
        """
        Ask the Scene to reload the models to better the definitions.

        Returns: None
        """
        self.__engine.reload_models()

    def set_polygon_mode(self, polygon_mode: OGLConstant.IntConstant) -> None:
        """
        Call the scene to change the polygon mode used.

        Args:
            polygon_mode: Polygon mode to use.

        Returns:
        """
        self.__scene.set_polygon_mode(polygon_mode)
