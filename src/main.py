"""
Main file of the relief application.

Starts the main program, calling the engine and the logic.
"""

# TODO: Write docs for this file
# TODO: Make a program and load a file
# TODO: Render more tha just a square in the screen
# TODO: Generate a triangulation from the points
# TODO: Search for an interface for the app (IMGUI related)

import glfw


from src.engine.render import Render
from src.engine.model.map2dmodel import Map2DModel
from src.utils import get_logger
from src.input.NetCDF import read_info
from src.engine.GUI.guimanager import GUIManager

log = get_logger(module='MAIN')


if __name__ == '__main__':

    log.info('Starting Program')

    filename = "./input/test_inputs/IF_60Ma_AHS_ET.nc"
    color_file = "./input/test_colors/Ocean_Land_3.cpt"
    log.debug('Using file %s for terrain.', filename)
    log.debug('Using file %s for colors.', color_file)

    X, Y, Z = read_info(filename)

    # Create main components of the engine
    # ------------------------------------
    render = Render()
    gui_manager = GUIManager()

    # GLFW CODE
    # ---------
    log.debug("Creating windows.")
    window = render.init("Relief Creator", gui_manager)

    # GUI CODE
    # --------
    log.debug("Loading GUI")
    gui_manager.initialize(window)

    # MODEL CODE
    # ----------
    log.debug("Reading information from file.")
    model = Map2DModel()

    log.debug("Setting vertices from grid.")
    model.set_vertices_from_grid(X, Y, Z, 3)

    log.debug("Settings colors from file.")
    model.set_color_file(color_file)
    model.wireframes = False

    log.debug("Starting main loop.")
    while not glfw.window_should_close(window):
        render.on_loop([lambda: model.draw()])

    glfw.terminate()
