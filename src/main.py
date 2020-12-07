"""
Main file of the relief application.

Starts the main program, calling the engine and the logic. Also defines
the Program class, the main class of the program that runs everything.
"""

import glfw

from src.engine.render import Render
from src.engine.model.map2dmodel import Map2DModel
from src.utils import get_logger
from src.input.NetCDF import read_info
from src.engine.GUI.guimanager import GUIManager

from src.engine.GUI.frames.sample_text import SampleText
from src.engine.GUI.frames.main_menu_bar import MainMenuBar
from src.engine.scene.scene import Scene
from src.engine.controller.controller import Controller

log = get_logger(module='MAIN')

# TODO: ADD this class to the class diagram.
# TODO: Solve problem in code consistency related to the types in the definitions

class Program:
    """
    Main class of the program, controls and connect every component of the program.
    """

    def __init__(self):
        """
        Constructor of the program.
        """
        self.render: Render = Render()
        self.gui_manager: GUIManager = GUIManager()
        self.window = None
        self.scene: Scene = Scene()
        self.controller: Controller = Controller()

    def initialize(self) -> None:
        """
        Initialize the components of the program.
        Returns: None
        """
        log.info('Starting Program')

        filename = "./input/test_inputs/ETOPO_IceSurfacec_6m.nc"
        color_file = "./input/test_colors/Ocean_Land_3.cpt"
        log.debug('Using file %s for terrain.', filename)
        log.debug('Using file %s for colors.', color_file)
        X, Y, Z = read_info(filename)

        # GLFW CODE
        # ---------
        log.debug("Creating windows.")
        self.window = self.render.init("Relief Creator", self.gui_manager)

        # GUI CODE
        # --------
        log.debug("Loading GUI")
        self.gui_manager.initialize(self.window)
        self.gui_manager.add_frames(
            [
                MainMenuBar(self.gui_manager, self.scene),
                # TestWindow(),
                SampleText()
            ]
        )

        # CONTROLLER CODE
        # ---------------
        self.controller.init(self.render)
        glfw.set_key_callback(self.window, self.controller.get_on_key_callback())
        glfw.set_window_size_callback(self.window, self.controller.get_resize_callback())

        # MODEL CODE
        # ----------
        log.debug("Reading information from file.")
        model = Map2DModel()

        log.debug("Setting vertices from grid.")
        model.set_vertices_from_grid(X, Y, Z, 3)

        log.debug("Settings colors from file.")
        model.set_color_file(color_file)
        model.wireframes = False

        # SCENE CODE
        # ----------
        self.scene.add_model(model)

    def run(self) -> None:
        """
        Run the program
        Returns: None
        """
        log.debug("Starting main loop.")
        while not glfw.window_should_close(self.window):
            self.render.on_loop([lambda: self.scene.draw()])

        glfw.terminate()


if __name__ == '__main__':
    program = Program()
    program.initialize()
    program.run()
