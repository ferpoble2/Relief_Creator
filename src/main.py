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

from src.engine.render import init
from src.engine.render import on_loop


def get_logger(log_level: int) -> logging.Logger:
    """
    Get the logger of the application to use in the main program.
    Args:
        log_level: Level too show in the logs (logging.DEBUG, logging.INFO, ...)

    Returns: Logger to use to makes logs.

    """
    log = logging.getLogger(__name__)
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    log.setLevel(log_level)

    return log


if __name__ == '__main__':

    logger = get_logger(logging.DEBUG)
    logger.debug("Starting mock program.")

    window = init("Relief Creator")

    while not glfw.window_should_close(window):
        on_loop(window)

    glfw.terminate()
