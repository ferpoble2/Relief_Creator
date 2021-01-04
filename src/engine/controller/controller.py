"""
Controller of the application. Manage all the glfw events that happens in the application.
"""
import sys
from typing import Callable

import glfw

from src.utils import get_logger

log = get_logger(module="CONTROLLER")


# noinspection PyMethodMayBeStatic
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
        self.__engine = None

    def init(self, engine: 'Engine') -> None:
        """
        Initialize the Controller component.

        Args:
            engine: Engine used in the application

        Returns: None
        """
        self.__render = engine.render
        self.__scene = engine.scene
        self.__engine = engine

    def get_on_key_callback(self) -> Callable:
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

            # In case window was minimized, do nothing
            if width == 0 and height == 0:
                return

            self.__engine.change_height_window(height)
            self.__engine.change_width_window(width)
            self.__engine.update_scene_values()
            self.__scene.update_viewport()

        return on_resize
