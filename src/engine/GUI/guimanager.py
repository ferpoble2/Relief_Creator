"""
File with the class that will manage the state of the GUI.
"""
import imgui
import OpenGL.constant as OGLConstant

from imgui.integrations.glfw import GlfwRenderer
from src.utils import get_logger

log = get_logger(module='GUIMANAGER')


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
        style.frame_rounding = 12
        imgui.style_colors_light(style)

        # Font options
        self.__io = imgui.get_io()
        self.__font = self.__io.fonts.add_font_from_file_ttf(
            './engine/GUI/fonts/open_sans/OpenSans-Regular.ttf', engine.get_font_size()
        )
        self.__implementation.refresh_font_texture()

        self.__scene = engine.scene
        self.__engine = engine

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

    def process_input(self) -> None:
        """
        Process the input (events) that happened in the GUI.
        Returns: None
        """
        self.__implementation.process_inputs()

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

    def render(self) -> None:
        """
        Render the GUI (Components must be drew first).
        Returns: None
        """
        imgui.render()
        self.__implementation.render(imgui.get_draw_data())

    def are_frame_fixed(self) -> bool:
        """
        Check if the frames are fixed or not.
        Returns: if frames are fixed or not.
        """
        return self.__engine.are_frames_fixed()

    def refresh_scene_with_model_2d(self, path_color_file: str, path_model: str) -> None:
        """
        Refresh the scene with the model 2D specified.

        Args:
            path_color_file: Path to CTP file.
            path_model: Path to the netCDF with the info of the model

        Returns: None

        """
        self.__scene.refresh_with_model_2d(path_color_file, path_model)

    def get_main_menu_bar_height(self):
        return self.__engine.get_gui_setting_data()['MAIN_MENU_BAR_HEIGHT']

    def get_left_frame_width(self):
        return self.__engine.get_gui_setting_data()['LEFT_FRAME_WIDTH']

    def get_window_height(self):
        return self.__engine.get_window_setting_data()['HEIGHT']

    def set_polygon_mode(self, polygon_mode: OGLConstant.IntConstant) -> None:
        """
        Call the scene to change the polygon mode used.

        Args:
            polygon_mode: Polygon mode to use.

        Returns:
        """
        self.__scene.set_polygon_mode(polygon_mode)
