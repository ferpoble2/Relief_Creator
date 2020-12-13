"""
Controller of the application. Manage all the glfw events that happens in the application.
"""
import sys
from typing import Callable

import glfw
# from src.engine.engine import Engine
from src.engine.settings import Settings
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
        self.__scene = None

    def init(self, engine: 'Engine') -> None:
        """
        Initialize the Controller component.

        Args:
            engine: Engine used in the application

        Returns: None
        """
        self.__render = engine.render
        self.__scene = engine.scene

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
            Settings.HEIGHT = height
            Settings.WIDTH = width
            Settings.update_scene_values()
            self.__scene.update_viewport()

        return on_resize
