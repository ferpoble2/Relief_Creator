"""
File that contains the program class, class that will be the main class of the program.
"""

import glfw

from src.engine.GUI.guimanager import GUIManager
from src.engine.controller.controller import Controller
from src.engine.render.render import Render
from src.engine.scene.scene import Scene
from src.engine.settings import Settings
from src.utils import get_logger

log = get_logger(module='PROGRAM')


# TODO: ADD this class to the class diagram.
# TODO: Solve problem in code consistency related to the types in the definitions

class Engine:
    """
    Main class of the program, controls and connect every component of the program.
    """

    def __init__(self):
        """
        Constructor of the program.
        """
        self.render = Render()
        self.gui_manager = GUIManager()
        self.window = None
        self.scene = Scene()
        self.controller = Controller()

    def initialize(self, engine: 'Engine') -> None:
        """
        Initialize the components of the program.
        Returns: None

        Args:
            engine: Engine to initialize.
        """
        log.info('Starting Program')

        # GLFW CODE
        # ---------
        log.debug("Creating windows.")
        self.window = self.render.init("Relief Creator", engine)

        # GUI CODE
        # --------
        log.debug("Loading GUI")
        self.gui_manager.initialize(self.window, engine)
        self.gui_manager.add_frames(self.gui_manager.get_frames(self.gui_manager))

        # CONTROLLER CODE
        # ---------------
        self.controller.init(engine)
        glfw.set_key_callback(self.window, self.controller.get_on_key_callback())
        glfw.set_window_size_callback(self.window, self.controller.get_resize_callback())

        # SCENE CODE
        # ----------
        self.scene.initilize(engine)

    @staticmethod
    def get_scene_setting_data() -> dict:
        """
        Get the scene setting data.
        Returns: dict with the data
        """
        return {
            'SCENE_BEGIN_X': Settings.SCENE_BEGIN_X, 'SCENE_BEGIN_Y': Settings.SCENE_BEGIN_Y,
            'SCENE_WIDTH_X': Settings.SCENE_WIDTH_X, 'SCENE_HEIGHT_Y': Settings.SCENE_HEIGHT_Y
        }

    @staticmethod
    def get_clear_color() -> list:
        """
        Get the clear color to use.
        Returns:list with the clear color

        """
        return Settings.CLEAR_COLOR

    @staticmethod
    def get_gui_setting_data() -> dict:
        """
        Get the GUI setting data.
        Returns: dict with the data

        """
        return {
            'LEFT_FRAME_WIDTH': Settings.LEFT_FRAME_WIDTH,
            'TOP_FRAME_HEIGHT': Settings.TOP_FRAME_HEIGHT,
            'MAIN_MENU_BAR_HEIGHT': Settings.MAIN_MENU_BAR_HEIGHT
        }

    @staticmethod
    def get_font_size()-> int:
        """
        Get the font size to use in the program.
        Returns: font size
        """
        return Settings.FONT_SIZE

    @staticmethod
    def fix_frames(fix: bool) -> None:
        """
        Fixes/unfix the frames in the application.
        Args:
            fix: boolean indicating if fix or not the frames.

        Returns: None
        """
        Settings.fix_frames(fix)

    @staticmethod
    def are_frames_fixed() -> bool:
        """
        Return if the frames are fixed or not in the application.
        Returns: boolean indicating if the frames are fixed
        """
        return Settings.FIXED_FRAMES

    @staticmethod
    def get_window_setting_data() -> dict:
        """
        Get the window setting data.
        Returns: dict with the data
        """
        return {
            'HEIGHT': Settings.HEIGHT,
            'WIDTH': Settings.WIDTH
        }

    @staticmethod
    def change_height_window(height: int) -> None:
        """
        Change the engine settings height for the windows.
        Args:
            height: New height

        Returns: None
        """
        Settings.HEIGHT = height

    @staticmethod
    def change_width_window(width: int) -> None:
        """
        Change the engine settings width for the windows
        Args:
            width: New width

        Returns: None
        """
        Settings.WIDTH = width

    @staticmethod
    def update_scene_values() -> None:
        """
        Update the configuration values related to the scene.
        Returns: None
        """
        Settings.update_scene_values()

    def run(self) -> None:
        """
        Run the program
        Returns: None
        """
        log.debug("Starting main loop.")
        while not glfw.window_should_close(self.window):
            self.render.on_loop([lambda: self.scene.draw()])

        glfw.terminate()
