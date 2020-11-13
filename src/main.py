"""
Main file of the relief application.

Starts the main program, calling the engine and the logic.
"""

# TODO: Write docs for this file
# TODO: Make a program and load a file
# TODO: Render more tha just a square in the screen
# TODO: Generate a triangulation from the points
# TODO: Search for an interfave for the app (IMGUI related)

import logging
import glfw
import os

from src.engine.render import init
from src.engine.render import on_loop
from src.utils import get_logger
from src.utils import LOG_LEVEL
from src.input.NetCDF import read_info



if __name__ == '__main__':

    logger = get_logger(LOG_LEVEL)
    logger.debug("Starting mock program.")

    logger.debug("Creating windows.")
    window = init("Relief Creator")

    logger.debug("Reading information from file.")
    x, y, z = read_info(os.path.join('input', 'test_inputs', 'IF_60Ma_AHS_ET.nc'))

    logger.debug("Starting main loop.")
    while not glfw.window_should_close(window):
        on_loop(window)

    glfw.terminate()
