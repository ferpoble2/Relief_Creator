#  BEGIN GPL LICENSE BLOCK
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  END GPL LICENSE BLOCK

"""
File that defines functions that controls the window generation
and the OpenGL rendering process.
"""
import logging as log
import sys
from typing import Dict

import OpenGL.GL as GL
import glfw


class Render:
    """
    Class in charge of executing the render process on the application.

    The render process is the one in charge of generating a 2D image using OpenGL to be showed on the program.
    """

    def __init__(self,
                 window_settings: Dict[str, int],
                 scene_settings_data: Dict[str, int],
                 clear_color: list,
                 window_name: str = "Relieve Creator"):
        """
        Constructor of the class.

        The window_settings variable must have the keys: WIDTH, HEIGHT, MIN_HEIGHT, MAX_HEIGHT, MIN_WIDTH and
        MAX_WIDTH.

        The scene_settings_data variable must have the keys: SCENE_BEGIN_X, SCENE_BEGIN_Y, SCENE_WIDTH_X and
        SCENE_HEIGHT_Y .

        Args:
            window_settings: Dictionary with the settings of the window to use by the render.
            scene_settings_data: Dictionary with the settings of the scene to use by the render.
            clear_color: Clear color to use for the clear of the models.
            window_name (str, optional): Name of the window created.
                                         Defaults to "Relieve Creator".
        """
        self.__window = None

        self.__show_framerate = False
        self.__previous_time = 0
        self.__frame_count = 0
        self.__current_time = None

        self.__init_variables(window_settings,
                              scene_settings_data,
                              clear_color,
                              window_name)

    def __init_variables(self,
                         window_settings: Dict[str, int],
                         scene_settings_data: Dict[str, int],
                         clear_color: list,
                         window_name: str = "Relieve Creator"):
        """Initialize the variables of the render.

        The window_settings variable must have the keys: WIDTH, HEIGHT, MIN_HEIGHT, MAX_HEIGHT, MIN_WIDTH and
        MAX_WIDTH.

        The scene_settings_data variable must have the keys: SCENE_BEGIN_X, SCENE_BEGIN_Y, SCENE_WIDTH_X and
        SCENE_HEIGHT_Y .

        Args:
            window_settings: Dictionary with the settings of the window to use by the render.
            scene_settings_data: Dictionary with the settings of the scene to use by the render.
            clear_color: Clear color to use for the clear of the models.
            window_name (str, optional): Name of the window created.
                                         Defaults to "Relieve Creator".
        """
        if not glfw.init():
            sys.exit()

        # set the gui for the app
        window_data = window_settings

        log.info(f"Creating windows of size {window_data['WIDTH']} x {window_data['HEIGHT']}.")
        self.__window = glfw.create_window(
            window_data['WIDTH'],
            window_data['HEIGHT'],
            window_name,
            None,
            None,
        )

        if not self.__window:
            glfw.terminate()
            sys.exit()

        glfw.make_context_current(self.__window)
        glfw.set_window_size_limits(self.__window,
                                    window_settings['MIN_WIDTH'],
                                    window_settings['MIN_HEIGHT'],
                                    window_settings['MAX_WIDTH'],
                                    window_settings['MAX_WIDTH'])

        clear_color = clear_color
        GL.glClearColor(
            clear_color[0],
            clear_color[1],
            clear_color[2],
            clear_color[3],
        )
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        # Indicate to openGL about the screen used in glfw to render.
        scene_data = scene_settings_data
        GL.glViewport(scene_data['SCENE_BEGIN_X'],
                      scene_data['SCENE_BEGIN_Y'],
                      scene_data['SCENE_WIDTH_X'],
                      scene_data['SCENE_HEIGHT_Y'])

    @property
    def window(self):
        """
        Get the window object used by the render to draw the models.

        Returns: Window used by the render
        """
        return self.__window

    def enable_depth_buffer(self, enable_buffer: bool) -> None:
        """
        Set if enable the depth buffer or not.

        When Depth Buffer is enabled, the depth of the points is considered when rendering the models on the screen.
        Otherwise, the last drown model is the one who is drawn in front of all the other models.

        It is recommended to enable the depth buffer when rendering 3D scenes and to disable it when rendering 2D
        scenes.

        Args:
            enable_buffer: Boolean indicating if to enable or not the depth buffer on the rendering process.

        Returns: None
        """
        if enable_buffer:
            GL.glEnable(GL.GL_DEPTH_TEST)
        else:
            GL.glDisable(GL.GL_DEPTH_TEST)

    def on_loop(self, on_frame_tasks: list = None) -> None:
        """
        Function to be called in every frame of he application.

        This should be the one who renders the program.
        Args:
            on_frame_tasks: List of functions without parameters to be called in the main loop.
                            These should be the ones who renders the objects and call others routines.

        Returns: None

        """
        if on_frame_tasks is None:
            on_frame_tasks = []

        # Clear the screen with the preloaded color
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Draw and render models and the GUI on the screen.
        for func in on_frame_tasks:
            func()

        # Show the framerate of the application in the windows name if the variable __show_framerate is set to True.
        if self.__show_framerate:
            self.__current_time = glfw.get_time()
            self.__frame_count += 1
            if self.__current_time - self.__previous_time >= 1:
                glfw.set_window_title(self.__window, f'Relief Creator - {self.__frame_count}')
                self.__frame_count = 0
                self.__previous_time = self.__current_time

        # Once the render is done, buffers are swapped, showing the complete scene.
        glfw.swap_buffers(self.__window)
        glfw.poll_events()
