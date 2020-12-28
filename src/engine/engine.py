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

log = get_logger(module='ENGINE')


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
        self.program = None

    def initialize(self, engine: 'Engine', program: 'Program') -> None:
        """
        Initialize the components of the program.
        Returns: None

        Args:
            engine: Engine to initialize.
        """
        log.info('Starting Program')
        self.program = program

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
        self.scene.initialize(engine)

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
        Get the clear color used.
        Returns:list with the clear color

        """
        return Settings.CLEAR_COLOR

    def change_quality(self, quality: int) -> None:
        """
        Change the quality used to render the maps.

        Args:
            quality: Quality to use in the rendering process

        Returns: None
        """
        Settings.QUALITY = quality

    @staticmethod
    def get_quality() -> int:
        """
        Get the quality value stored in the settings.

        Returns: Quality setting
        """
        return Settings.QUALITY

    def refresh_with_model_2d(self, path_color_file: str, path_model: str, model_id: str = 'main') -> None:
        """
        Refresh the scene creating a 2D model with the parameters given.

        Args:
            model_id: Model id to use in the new model.
            path_color_file: Path to the color file to use.
            path_model: Path to the model file (NetCDF) to use.

        Returns: none
        """
        self.program.set_loading(True)
        self.scene.refresh_with_model_2d(path_color_file, path_model, model_id)
        self.program.set_model_id(model_id)

    def is_program_loading(self) -> bool:
        """
        Return if the program is loading or not.

        Returns: Boolean representing if the program is running or not.
        """
        return self.program.is_loading()

    def change_color_file(self, path_color_file: str) -> None:
        """
        Change the color file to the one selected.
        This change all the models using the color file.

        Args:
            path_color_file: Path to the color file to use.

        Returns: None
        """
        self.program.set_cpt_file(path_color_file)
        self.scene.update_models_colors()

    def get_CPT_file(self) -> None:
        """
        Get the CPT file used by the program.

        Returns: String with the CPT file used.
        """
        return self.program.get_cpt_file()

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
    def get_font_size() -> int:
        """
        Get the font size to use in the program.
        Returns: font size
        """
        return Settings.FONT_SIZE

    def get_cpt_file(self) -> str:
        """
        Get the CTP file currently being used in the program
        Returns: String with the path to the file

        """
        return self.program.get_cpt_file()

    @staticmethod
    def get_view_mode() -> str:
        """
        Get the view mode stored in the settings.

        Returns: View mode
        """
        return Settings.VIEW_MODE

    def reset_zoom_level(self) -> None:
        """
        Reset the zoom level of the program.

        Returns: None
        """
        self.program.reset_zoom_level()

    def add_zoom(self) -> None:
        """
        Add zoom to the current map being watched.

        Returns: None
        """
        self.program.add_zoom()
        self.scene.update_models_projection_matrix()

    def less_zoom(self) -> None:
        """
        Reduce on 1 the level of zoom.

        Returns: None
        """
        self.program.less_zoom()
        self.scene.update_models_projection_matrix()

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

    def get_map_position(self) -> list:
        """
        Get the map position on the program.

        Returns: List with the position of the map.
        """
        return self.program.get_map_position()

    def get_active_tool(self) -> str:
        """
        Get the active tool in the program.

        Returns: String with the active tool being used.
        """
        return self.program.get_active_tool()

    def reload_models(self) -> None:
        """
        Ask the Scene to reload the models to better the definitions.

        Returns: None
        """
        self.scene.reload_models()

    def get_zoom_level(self) -> float:
        """
        Get the zoom level currently being used in the program.

        Returns: Zoom level

        """
        return self.program.get_zoom_level()

    def run(self) -> None:
        """
        Run the program
        Returns: None
        """
        log.debug("Starting main loop.")
        while not glfw.window_should_close(self.window):
            self.render.on_loop([lambda: self.scene.draw()])

        glfw.terminate()
