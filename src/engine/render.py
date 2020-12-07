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
from src.engine.settings import SCENE_BEGIN_X, SCENE_BEGIN_Y, SCENE_END_X, SCENE_END_Y
from src.engine.GUI.guimanager import GUIManager


class Render:

    def __init__(self):
        """
        Constructor od the render.
        """
        self.__window = None
        self.__GUI = None

    def init(self, window_name: str = "Relieve Creator", gui: GUIManager = None) -> None:
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
        GL.glViewport(SCENE_BEGIN_X, SCENE_BEGIN_Y, SCENE_END_X, SCENE_END_Y)

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

    @staticmethod
    def change_viewport(init_x: int, init_y: int, final_x: int, final_y: int) -> None:
        """
        Change the coordinates used in the viewport.

        Args:
            init_x: Position of the left border of the viewport.
            init_y: Position of the top border of the viewport.
            final_x: Position of the right border of the viewport.
            final_y: Position of the bottom border of the viewport.

        Returns: None
        """
        GL.glViewport(init_x, init_y, final_x, final_y)
