"""
File with the class that will manage the state of the GUI.
"""
import imgui
from imgui.integrations.glfw import GlfwRenderer

from src.utils import get_logger
from src.engine.GUI.frames import test_window
from src.engine.GUI.frames import sample_text

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

    def initialize(self, window, mode='debug') -> None:
        """
        Set the initial configurations of the GUI.
        Args:
            window: Window to use to draw the GUI
            mode: Mode in which to draw the GUI (debug or production)

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
            './engine/GUI/fonts/open_sans/OpenSans-Regular.ttf', 15
        )
        self.__implementation.refresh_font_texture()

        if mode == 'debug':
            self.debug_mode()

        if mode == 'production':
            self.production_mode()

    def debug_mode(self) -> None:
        """
        Set the gui in debug mode
        Returns: None
        """
        self.__component_list.append(test_window)
        self.__component_list.append(sample_text)

    def production_mode(self) -> None:
        """
        Set the GUI in production mode.
        Returns: None

        """
        pass

    def process_input(self) -> None:
        """
        Process the input (events) that happened in the GUI.
        Returns: None
        """
        self.__implementation.process_inputs()

    def draw_components(self) -> None:
        """
        Draw the components of the GUI (This dont render them).
        Returns: None
        """
        imgui.new_frame()
        with imgui.font(self.__font):
            for func in self.__component_list:
                func()
        imgui.end_frame()

    def render(self) -> None:
        """
        Render the GUI (Components must be drew first).
        Returns: None
        """
        imgui.render()
        self.__implementation.render(imgui.get_draw_data())
