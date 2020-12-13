"""
File that defines functions that controls the window generation
and the OpenGL rendering process.
"""
import OpenGL.GL as GL
import glfw
import logging as log
import sys
from src.engine.settings import Settings


class Render:

    def __init__(self):
        """
        Constructor od the render.
        """
        self.__window = None
        self.__GUI = None

    def init(self, window_name: str = "Relieve Creator", engine: 'Engine' = None) -> None:
        """Initialize OpenGL and glfw for the application.

        Args:
            engine: Engine to be used in the application.
            window_name (str, optional): Name of the window created.
                                         Defaults to "Relieve Creator".

        Returns:
            GLFWWindow: Window to use for the rendering process.
        """
        if not glfw.init():
            sys.exit()

        # set the gui for the app
        self.__GUI = engine.gui_manager

        log.info(f"Creating windows of size {Settings.WIDTH} x {Settings.HEIGHT}.")
        self.__window = glfw.create_window(
            Settings.WIDTH,
            Settings.HEIGHT,
            window_name,
            None,
            None,
        )

        if not self.__window:
            glfw.terminate()
            sys.exit()

        glfw.make_context_current(self.__window)

        GL.glClearColor(
            Settings.CLEAR_COLOR[0],
            Settings.CLEAR_COLOR[1],
            Settings.CLEAR_COLOR[2],
            Settings.CLEAR_COLOR[3],
        )

        # Indicate to openGL about the screen used in glfw to render.
        GL.glViewport(Settings.SCENE_BEGIN_X, Settings.SCENE_BEGIN_Y, Settings.SCENE_WIDTH_X, Settings.SCENE_HEIGHT_Y)

        return self.__window

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

        self.__GUI.process_input()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # drawing the model in the screen
        # -------------------------------
        for func in on_frame_tasks:
            func()

        self.__GUI.draw_frames()

        # Once the render is done, buffers are swapped, showing the complete scene.
        self.__GUI.render()
        glfw.swap_buffers(self.__window)
        glfw.poll_events()
