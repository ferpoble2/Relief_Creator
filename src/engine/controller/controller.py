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

        # Auxiliary methods
        self.__mouse_old_pos = (0, 0)
        self.__is_left_ctrl_pressed = False
        self.__is_left_alt_pressed = False

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

    def is_inside_scene(self, mouse_x_pos: int, mouse_y_pos: int) -> bool:
        """
        Check if the mouse is inside the scene or not.

        Args:
            mouse_x_pos: X position of the mouse given by glfw
            mouse_y_pos: Y position of the mouse given by glfw

        Returns: Boolean indicating if mouse is inside the scene
        """
        scene_data = self.__engine.get_scene_setting_data()
        is_inside = True

        # invert the mouse position given by glfw to start at the bottom of the screen
        mouse_y_pos = self.__engine.get_window_setting_data()['HEIGHT'] - mouse_y_pos

        # check if mouse is inside the scene
        if mouse_x_pos < scene_data['SCENE_BEGIN_X'] or \
                mouse_x_pos > scene_data['SCENE_BEGIN_X'] + scene_data['SCENE_WIDTH_X'] or \
                mouse_y_pos < scene_data['SCENE_BEGIN_Y'] or \
                mouse_y_pos > scene_data['SCENE_BEGIN_Y'] + scene_data['SCENE_HEIGHT_Y']:
            is_inside = False

        return is_inside

    def set_mouse_pos(self, new_x: int, new_y: int) -> None:
        """
        Change the mouse position.

        Args:
            new_x: New x coordinate
            new_y: New y coordinate

        Returns: None
        """
        self.__mouse_old_pos = (new_x, new_y)

    def get_cursor_position_callback(self):
        """
        Get the mouse movement callback function.

        Returns: Function to use as callback
        """

        def cursor_position_callback(window, xpos, ypos):

            # check if mouse is inside the scene
            if self.is_inside_scene(xpos, ypos):

                # check if the mouse button is pressed
                if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:

                    # get the active tool being used in the program
                    active_tool = self.__engine.get_active_tool()

                    # if the active tool is to move a map
                    if active_tool == 'move_map':
                        log.debug(
                            f"Cursor movement: {xpos - self.__mouse_old_pos[0]}, {self.__mouse_old_pos[1] - ypos}")
                        self.__engine.move_scene(xpos - self.__mouse_old_pos[0], self.__mouse_old_pos[1] - ypos)

            # update the move position at the end
            self.set_mouse_pos(xpos, ypos)

        return cursor_position_callback

    def get_mouse_button_callback(self):
        """
        Get the mouse callback function to use when a mouse button is pressed.

        Returns: Function to use as callback
        """

        def mouse_button_callback(window, button, action, mods):
            if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
                log.debug("Left mouse button pressed")

        return mouse_button_callback

    def get_on_key_callback(self) -> Callable:
        """
        Get the callback function to use when a key is pressed.

        Returns: Function to use as callback.
        """

        # define the on_key callback
        def on_key(window, key, scancode, action, mods):

            # Check what to do if a key is pressed
            if action == glfw.PRESS:

                # Do the logic
                if key == glfw.KEY_LEFT_CONTROL:
                    log.debug("Left control pressed")
                    self.__is_left_ctrl_pressed = True

                if key == glfw.KEY_LEFT_ALT:
                    log.debug("Left alt pressed")
                    self.__is_left_alt_pressed = True

                # Shortcuts of the platform
                # -------------------------
                if key == glfw.KEY_O and self.__is_left_ctrl_pressed:
                    log.debug("Shortcut open file")
                    try:
                        self.__engine.load_netcdf_file_with_dialog()

                    except KeyError:
                        log.debug("Error reading files, KeyError")
                        self.__engine.set_modal_text("Error", "Error reading the selected files (KeyError)")

                    except OSError:
                        log.debug("Error reading files, OSError")
                        self.__engine.set_modal_text("Error", "Error reading the selected files (OSError)")

            # Check for keys released
            if action == glfw.RELEASE:

                # Do the logic
                if key == glfw.KEY_LEFT_CONTROL:
                    log.debug("Left control released")
                    self.__is_left_ctrl_pressed = False

                if key == glfw.KEY_LEFT_ALT:
                    log.debug("Left alt released")
                    self.__is_left_alt_pressed = False

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
