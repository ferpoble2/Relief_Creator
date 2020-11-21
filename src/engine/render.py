"""
File that defines functions that controls the window generation
and the OpenGL rendering process.
"""
import OpenGL.GL as GL
import glfw
import logging as log
import sys
from src.engine.settings import HEIGHT
from src.engine.settings import WIDTH
from src.engine.settings import CLEAR_COLOR
from src.engine.GUI.guimanager import GUIManager


class Render:

    def __init__(self):
        """
        Constructor od the render.
        """
        self.__window = None
        self.__GUI = None

    def init(self, window_name: str = "Relieve Creator", gui: GUIManager = None):
        """Initialize OpenGL and glfw for the application.

        Args:
            gui: Gui to use to render in the app.
            window_name (str, optional): Name of the window created.
                                         Defaults to "Relieve Creator".

        Returns:
            GLFWWindow: Window to use for the rendering process.
        """
        if not glfw.init():
            sys.exit()

        # set the gui for the app
        self.__GUI = gui

        log.info(f"Creating windows of size {WIDTH} x {HEIGHT}.")
        self.__window = glfw.create_window(
            WIDTH,
            HEIGHT,
            window_name,
            None,
            None,
        )

        if not self.__window:
            glfw.terminate()
            sys.exit()

        glfw.make_context_current(self.__window)

        GL.glClearColor(
            CLEAR_COLOR[0],
            CLEAR_COLOR[1],
            CLEAR_COLOR[2],
            CLEAR_COLOR[3],
        )

        # Indicate to openGL about the screen used in glfw to render.
        GL.glViewport(0, 0, WIDTH, HEIGHT)

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

        glfw.poll_events()
        self.__GUI.process_input()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # drawing the model in the screen
        # -------------------------------
        for func in on_frame_tasks:
            func()

        self.__GUI.draw_components()

        # Once the render is done, buffers are swapped, showing the complete scene.
        self.__GUI.render()
        glfw.swap_buffers(self.__window)
