"""
Controller of the application. Manage all the glfw events that happens in the application.
"""
import sys
from typing import Callable

import glfw

from src.utils import get_logger
from src.error.line_intersection_error import LineIntersectionError
from src.error.repeated_point_error import RepeatedPointError

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

            # get the active tool being used in the program
            active_tool = self.__engine.get_active_tool()

            if active_tool == 'move_map':
                if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
                    if self.is_inside_scene(xpos, ypos):
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
                active_tool = self.__engine.get_active_tool()

                if active_tool == 'create_polygon':
                    pos_x, pos_y = glfw.get_cursor_pos(window)

                    if self.is_inside_scene(pos_x, pos_y):
                        log.debug(f"Creating points for active polygon at: {pos_x} {pos_y}")

                        # add a point to the polygon or show an error modal if there is errors.
                        try:
                            self.__engine.add_new_vertex_to_active_polygon_using_window_coords(pos_x, pos_y)

                        except RepeatedPointError as e:
                            log.error(e)
                            self.__engine.set_modal_text('Error', 'Point already exist in polygon.')

                        except LineIntersectionError as e:
                            log.error(e)
                            self.__engine.set_modal_text('Error', 'Line intersect another one already in the polygon.')

        return mouse_button_callback

    def change_color_file_with_dialog(self) -> None:
        """
        Change the color file opening a dialog to select the file.

        Returns: None
        """
        try:
            self.__engine.change_color_file_with_dialog()

        except KeyError as e:
            log.exception(f"Error reading files: {e}")
            self.__engine.set_modal_text("Error", "Error reading color file (KeyError)")

        except IOError as e:
            log.exception(f"Error reading files: {e}")
            self.__engine.set_modal_text("Error", "Error reading color file (IOError)")

        except TypeError as e:
            log.exception(f"Error reading files: {e}")
            self.__engine.set_modal_text("Error", "Error reading color file (TypeError)")

        except OSError as e:
            log.exception(f"Error reading files: {e}")
            self.__engine.set_modal_text("Error", "Error reading color file (OSError)")

    def load_netcdf_file_with_dialog(self) -> None:
        """
        Load a netcdf file opening a dialog to select the file.

        Returns: None
        """
        try:
            self.__engine.load_netcdf_file_with_dialog()

        except KeyError as e:
            log.exception(f"Error reading files, {e}")
            self.__engine.set_modal_text("Error", "Error reading the selected files (KeyError)")

        except OSError as e:
            log.exception(f"Error reading files,{e}")
            self.__engine.set_modal_text("Error", "Error reading the selected files (OSError)")

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
                    self.load_netcdf_file_with_dialog()

                if key == glfw.KEY_T and self.__is_left_ctrl_pressed:
                    log.debug("Pressed shortcut to change color file")
                    self.change_color_file_with_dialog()

                if key == glfw.KEY_M:
                    log.debug("Pressed shortcut to move map")
                    self.__engine.set_active_tool('move_map')

                if key == glfw.KEY_Z:

                    if self.__is_left_ctrl_pressed:
                        log.debug("Pressed ctrl+z")
                        self.__engine.undo_action()

            # Check for keys released
            if action == glfw.RELEASE:

                # Do the logic
                if key == glfw.KEY_LEFT_CONTROL:
                    log.debug("Left control released")
                    self.__is_left_ctrl_pressed = False

                if key == glfw.KEY_LEFT_ALT:
                    log.debug("Left alt released")
                    self.__is_left_alt_pressed = False

            # call the others callbacks defined in the program.
            self.__engine.get_gui_key_callback()(window, key, scancode, action, mods)

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
