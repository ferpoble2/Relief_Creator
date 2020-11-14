"""
File with the class that will manage the state of the GUI.
"""
import imgui
from imgui.integrations.glfw import GlfwRenderer

from src.utils import get_logger
from src.engine.GUI.frames import test_window

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

    def initialize(self, window, mode='debug') -> None:
        """
        Set the initial configurations of the GUI.
        Args:
            window: Window to use to draw the GUI
            mode: Mode in wich to draw the GUI (debug or production)

        Returns: None

        """
        log.info("Initializing GUI")
        imgui.create_context()
        self.__implementation = GlfwRenderer(window)
        self.__glfw_window = window

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
        for funct in self.__component_list:
            funct()

    def render(self) -> None:
        """
        Render the GUI (Componentes must be drew first).
        Returns: None
        """
        imgui.render()
        self.__implementation.render(imgui.get_draw_data())
