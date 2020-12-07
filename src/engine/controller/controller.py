"""
Controller of the application. Manage all the glfw events that happens in the application.
"""
import sys
from typing import Callable

import glfw
from src.engine.settings import SCENE_BEGIN_X, SCENE_BEGIN_Y
from src.engine.render import Render
from src.utils import get_logger

log = get_logger(module="CONTROLLER")


class Controller:
    """
    Controller of the engine, controls all things related to the input of the program.
    """

    def __init__(self):
        """
        Constructor of the class.
        """
        self.__render = None

    def init(self, render: Render) -> None:
        """
        Initialize the Controller component.

        Args:
            render: Render to be used by the application.

        Returns: None
        """
        self.__render = render

    @staticmethod
    def get_on_key_callback() -> Callable:
        """
        Get the callback function to use when a key is pressed.

        Returns: Function to use as callback.
        """

        # define the on_key callback
        def on_key(window, key, scancode, action, mods):
            if action != glfw.PRESS:
                return

            if key == glfw.KEY_SPACE:
                log.debug("Pressing Space")

            elif key == glfw.KEY_ESCAPE:
                sys.exit()

        return on_key

    def get_resize_callback(self) -> Callable:
        """
        Get the callback for when the resizing is done.
        Returns: Function to use as a callback.
        """

        def on_resize(window, width, height):
            log.debug(f"Windows resized to {width}x{height}")
            self.__render.change_viewport(SCENE_BEGIN_X, SCENE_BEGIN_Y, width, height)

        return on_resize
