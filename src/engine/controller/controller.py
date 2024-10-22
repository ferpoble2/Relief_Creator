# BEGIN GPL LICENSE BLOCK
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# END GPL LICENSE BLOCK

"""
Controller of the application.

Generate all the GLFW callbacks functions that manage the events of the application. The callbacks define the
logic to execute depending on the events happening, but also call the callback functions defined on the GUI of the
application.

All the events captured by the GUI must be processed so GLFW must be able to capture them for this module to
work correctly.
"""
from typing import Callable, Dict, TYPE_CHECKING

import glfw

from src.program.tools import Tools
from src.program.view_mode import ViewMode
from src.utils import get_logger

if TYPE_CHECKING:
    from src.engine.engine import Engine

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
        self.__keyboard_callback_enabled = True

        # Auxiliary variables
        self.__mouse_old_pos = (0, 0)
        self.__is_left_ctrl_pressed = False
        self.__is_left_alt_pressed = False

        self.__is_left_mouse_being_pressed = False
        self.__is_mouse_middle_being_pressed = False

        self.__is_w_pressed = False
        self.__is_s_pressed = False
        self.__is_a_pressed = False
        self.__is_d_pressed = False

        self.__is_left_key_pressed = False
        self.__is_right_key_pressed = False
        self.__is_up_key_pressed = False
        self.__is_down_key_pressed = False

        self.__map_movement_velocity = -20
        self.__radius_movement_velocity = 3
        self.__elevation_movement_velocity = 0.01
        self.__azimuthal_movement_velocity = 0.01
        self.__camera_movement_velocity = 1
        self.__camera_mouse_movement_factor = 0.01

        self.__move_map_tool_activated = False

    def __is_inside_scene(self, mouse_x_pos: int, mouse_y_pos: int, scene_settings_data: Dict[str, int],
                          window_setting_data: Dict[str, int]) -> bool:
        """
        Check if the mouse is inside the scene or not.

        Args:
            scene_settings_data: Dictionary with the settings of the scene.
            window_setting_data: Dictionary with the settings of the window.
            mouse_x_pos: X position of the mouse given by glfw
            mouse_y_pos: Y position of the mouse given by glfw

        Returns: Boolean indicating if mouse is inside the scene
        """
        scene_data = scene_settings_data
        is_inside = True

        # invert the mouse position given by glfw to start at the bottom of the screen
        mouse_y_pos = window_setting_data['HEIGHT'] - mouse_y_pos

        # check if mouse is inside the scene
        if mouse_x_pos < scene_data['SCENE_BEGIN_X'] or \
                mouse_x_pos > scene_data['SCENE_BEGIN_X'] + scene_data['SCENE_WIDTH_X'] or \
                mouse_y_pos < scene_data['SCENE_BEGIN_Y'] or \
                mouse_y_pos > scene_data['SCENE_BEGIN_Y'] + scene_data['SCENE_HEIGHT_Y']:
            is_inside = False

        return is_inside

    def __set_mouse_pos(self, new_x: int, new_y: int) -> None:
        """
        Change the mouse position.

        Args:
            new_x: New x coordinate
            new_y: New y coordinate

        Returns: None
        """
        self.__mouse_old_pos = (new_x, new_y)

    def get_keyboard_callback_state(self) -> bool:
        """
        Get the state of the keyboard callback defined by this class.

        Return True if the keyboard callback defined by this class is working correctly, return False if the keyboard
        callback defined by this class is not being considered when polling events.

        Returns: Boolean indicating the state of the keyboard callback function.
        """
        return self.__keyboard_callback_enabled

    def get_cursor_position_callback(self, engine: 'Engine'):
        """
        Get the mouse movement callback function.

        Returns: Function to use as callback

        Args:
            engine: Engine to use to execute the logic defined by the callback.
        """

        # noinspection PyMissingOrEmptyDocstring
        def cursor_position_callback(_, x_pos, y_pos):

            # get the active tool being used in the program
            active_tool = engine.get_active_tool()

            if engine.get_program_view_mode() == ViewMode.mode_2d:

                if active_tool == Tools.move_map and self.__move_map_tool_activated:
                    if self.__is_left_mouse_being_pressed:
                        engine.move_map_position(x_pos - self.__mouse_old_pos[0],
                                                 self.__mouse_old_pos[1] - y_pos)

            if engine.get_program_view_mode() == ViewMode.mode_3d:

                if self.__is_mouse_middle_being_pressed:
                    engine.change_camera_elevation(
                        (self.__mouse_old_pos[1] - y_pos) * self.__camera_mouse_movement_factor)
                    engine.change_camera_xy_angle(
                        (self.__mouse_old_pos[0] - x_pos) * self.__camera_mouse_movement_factor)

            # update the move position at the end
            self.__set_mouse_pos(x_pos, y_pos)

        return cursor_position_callback

    def get_mouse_button_callback(self, engine: 'Engine'):
        """
        Get the mouse callback function to use when a mouse button is pressed.

        Args:
            engine: Engine to use to execute the logic defined by the callback.

        Returns: Function to use as callback
        """

        # noinspection PyMissingOrEmptyDocstring
        def mouse_button_callback(window, button, action, _):

            # state of the controller
            if action == glfw.PRESS:
                if button == glfw.MOUSE_BUTTON_LEFT:
                    self.__is_left_mouse_being_pressed = True

                if button == glfw.MOUSE_BUTTON_MIDDLE:
                    self.__is_mouse_middle_being_pressed = True

            if action == glfw.RELEASE:
                if button == glfw.MOUSE_BUTTON_LEFT:
                    self.__is_left_mouse_being_pressed = False

                if button == glfw.MOUSE_BUTTON_MIDDLE:
                    self.__is_mouse_middle_being_pressed = False

            # logic of the controller.
            if not engine.is_mouse_hovering_frame():

                if engine.get_program_view_mode() == ViewMode.mode_2d:

                    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
                        active_tool = engine.get_active_tool()

                        if active_tool == Tools.move_map:
                            self.__move_map_tool_activated = True

                        if active_tool == Tools.create_polygon:
                            pos_x, pos_y = glfw.get_cursor_pos(window)

                            if self.__is_inside_scene(pos_x, pos_y, engine.get_scene_setting_data(),
                                                      engine.get_window_setting_data()):
                                log.debug(f"Creating points for active polygon at: {pos_x} {pos_y}")

                                engine.add_new_vertex_to_active_polygon_using_window_coords(pos_x, pos_y)

                    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE:
                        active_tool = engine.get_active_tool()

                        if active_tool == Tools.move_map:
                            self.__move_map_tool_activated = False

                elif engine.get_program_view_mode() == ViewMode.mode_3d:
                    pass

        return mouse_button_callback

    def get_mouse_scroll_callback(self, engine: 'Engine') -> Callable:
        """
        Get the callback for the mouse wheel.

        Args:
            engine: Engine to use to execute the logic defined by the callback.

        Returns: Function to call for the mouse wheel.
        """

        # noinspection PyMissingOrEmptyDocstring
        def mouse_wheel_callback(window, x_offset, y_offset):

            # do something only if not hovering frames
            if not engine.is_mouse_hovering_frame():

                if engine.get_program_view_mode() == ViewMode.mode_2d:
                    if y_offset > 0:
                        engine.add_zoom()

                    if y_offset < 0:
                        engine.less_zoom()

                elif engine.get_program_view_mode() == ViewMode.mode_3d:
                    if y_offset > 0:
                        engine.modify_camera_radius(-1 * self.__radius_movement_velocity)

                    if y_offset < 0:
                        engine.modify_camera_radius(1 * self.__radius_movement_velocity)

            engine.get_gui_scroll_callback()(window, x_offset, y_offset)

        return mouse_wheel_callback

    def get_on_key_callback(self, engine: 'Engine') -> Callable:
        """
        Get the callback function to use when a key is pressed.

        This function also calls the key_callback defined by the GUI, executing the logic defined inside after the
        logic defined in the controller.

        Args:
            engine: Engine to use to execute the logic defined by the callback.

        Returns: Function to use as callback.
        """

        # define the on_key callback
        def on_key(window, key, scancode, action, mods):
            """
            Function used for the on_key callback. This function will be called every time that a key is pressed on
            the application.

            Update the state of the keys in the internal variables of the controller class and do the logic on the
            program depending on the key pressed.

            Does nothing but keep track of the keys pressed and released if the variable only_gui_keyboard_callback
            is set to True.
            """

            # update the state of the controller variables
            # work even when glfw callback is disabled
            if action == glfw.PRESS:

                if key == glfw.KEY_LEFT_CONTROL:
                    self.__is_left_ctrl_pressed = True

                if key == glfw.KEY_LEFT_ALT:
                    self.__is_left_alt_pressed = True

                if key == glfw.KEY_W:
                    self.__is_w_pressed = True

                if key == glfw.KEY_S:
                    self.__is_s_pressed = True

                if key == glfw.KEY_A:
                    self.__is_a_pressed = True

                if key == glfw.KEY_D:
                    self.__is_d_pressed = True

                if key == glfw.KEY_LEFT:
                    self.__is_left_key_pressed = True

                if key == glfw.KEY_RIGHT:
                    self.__is_right_key_pressed = True

                if key == glfw.KEY_UP:
                    self.__is_up_key_pressed = True

                if key == glfw.KEY_DOWN:
                    self.__is_down_key_pressed = True

            if action == glfw.RELEASE:

                # Do the logic
                if key == glfw.KEY_LEFT_CONTROL:
                    self.__is_left_ctrl_pressed = False

                if key == glfw.KEY_LEFT_ALT:
                    self.__is_left_alt_pressed = False

                # map movement
                if key == glfw.KEY_W:
                    self.__is_w_pressed = False

                if key == glfw.KEY_S:
                    self.__is_s_pressed = False

                if key == glfw.KEY_A:
                    self.__is_a_pressed = False

                if key == glfw.KEY_D:
                    self.__is_d_pressed = False

                if key == glfw.KEY_LEFT:
                    self.__is_left_key_pressed = False

                if key == glfw.KEY_RIGHT:
                    self.__is_right_key_pressed = False

                if key == glfw.KEY_UP:
                    self.__is_up_key_pressed = False

                if key == glfw.KEY_DOWN:
                    self.__is_down_key_pressed = False

            # logic: only work if the glfw functionality is enabled
            # -----------------------------------------------------
            if self.__keyboard_callback_enabled:

                # shortcuts shared between 2D and 3D modes
                # ----------------------------------------
                if action == glfw.PRESS:
                    if key == glfw.KEY_O and self.__is_left_ctrl_pressed:
                        log.debug("Shortcut open file")
                        engine.load_netcdf_file_with_dialog()

                    if key == glfw.KEY_T and self.__is_left_ctrl_pressed:
                        log.debug("Pressed shortcut to change color file")
                        engine.change_color_file_with_dialog()

                    if key == glfw.KEY_L:
                        if self.__is_left_ctrl_pressed:
                            engine.load_shapefile_file_with_dialog()

                if engine.get_program_view_mode() == ViewMode.mode_2d:

                    # Check what to do if a key is pressed
                    if action == glfw.PRESS:

                        # Shortcuts of the platform
                        # -------------------------
                        if key == glfw.KEY_M:
                            log.debug("Pressed shortcut to move map")
                            engine.set_active_tool(Tools.move_map)

                        if key == glfw.KEY_Z:
                            if self.__is_left_ctrl_pressed:
                                log.debug("Pressed ctrl+z")
                                engine.undo_action()

                        if key == glfw.KEY_R:
                            engine.reload_models()

                    # Check for in-frame actions
                    if self.__is_w_pressed:
                        engine.move_map_position(0, self.__map_movement_velocity)
                    if self.__is_s_pressed:
                        engine.move_map_position(0, -1 * self.__map_movement_velocity)
                    if self.__is_a_pressed:
                        engine.move_map_position(-1 * self.__map_movement_velocity, 0)
                    if self.__is_d_pressed:
                        engine.move_map_position(self.__map_movement_velocity, 0)

                elif engine.get_program_view_mode() == ViewMode.mode_3d:
                    if self.__is_w_pressed:
                        engine.change_camera_elevation(self.__elevation_movement_velocity)
                    if self.__is_s_pressed:
                        engine.change_camera_elevation(-1 * self.__elevation_movement_velocity)
                    if self.__is_a_pressed:
                        engine.change_camera_xy_angle(-1 * self.__azimuthal_movement_velocity)
                    if self.__is_d_pressed:
                        engine.change_camera_xy_angle(self.__azimuthal_movement_velocity)

                    if self.__is_up_key_pressed:
                        engine.move_camera_position((0, self.__camera_movement_velocity, 0))
                    if self.__is_down_key_pressed:
                        engine.move_camera_position((0, -1 * self.__camera_movement_velocity, 0))
                    if self.__is_left_key_pressed:
                        engine.move_camera_position((-1 * self.__camera_movement_velocity, 0, 0))
                    if self.__is_right_key_pressed:
                        engine.move_camera_position((self.__camera_movement_velocity, 0, 0))

            # call the others callbacks defined in the program.
            engine.get_gui_key_callback()(window, key, scancode, action, mods)

        return on_key

    def get_resize_callback(self, engine: 'Engine') -> Callable:
        """
        Get the callback for when the resizing is done.

        Args:
            engine: Engine to use to execute the logic defined by the callback.

        Returns: Function to use as a callback.
        """

        def on_resize(_, width, height):
            """
            Function used for the resizing callback. This function will be called every time the window of the
            application is resized.

            Update the height and width settings and also update the scene values and viewport.
            """
            log.debug(f"Windows resized to {width}x{height}")

            # In case window was minimized, do nothing
            if width == 0 and height == 0:
                return

            engine.change_height_window(height)
            engine.change_width_window(width)
            engine.update_scene_values()
            engine.update_scene_viewport()

        return on_resize

    def set_keyboard_callback(self, new_state: bool) -> None:
        """
        Enable/Disable the functionality of the keyboard callback function defined in the glfw call.

        Does not affect to the keyboard callback from imgui.

        Returns: None

        Args:
            new_state: New state of the keyboard callback used by the controller.
        """
        self.__keyboard_callback_enabled = new_state
