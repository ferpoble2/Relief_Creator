"""
File that defines functions that controls the window generation
and the OpenGL rendering process.
"""
import OpenGL.GL as GL
import glfw
import logging as log
import numpy as np
import sys
from src.engine.model import Model
from src.engine.settings import HEIGHT
from src.engine.settings import WIDTH
from src.engine.settings import clear_color


def init(window_name: str = "Relieve Creator"):
    """Initialize OpenGL and glfw for the application.

    Args:
        window_name (str, optional): Name of the window created.
                                     Defaults to "Relieve Creator".

    Returns:
        GLFWWindow: Window to use for the rendering process.
    """
    if not glfw.init():
        sys.exit()

    log.info(f"Creating windows of size {WIDTH} x {HEIGHT}.")
    render_window = glfw.create_window(
        WIDTH,
        HEIGHT,
        window_name,
        None,
        None,
    )

    if not render_window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(render_window)

    GL.glClearColor(
        clear_color[0],
        clear_color[1],
        clear_color[2],
        clear_color[3],
    )

    return render_window


def on_loop(render_window, on_frame_tasks=None) -> None:
    """
    Function to be called in every frame of he application.

    This should be the one who renders the program.
    Args:
        render_window: Window to be used in the program.
        on_frame_tasks: List of functions without parameters to be called in the main loop.
                        These should be the ones who renders the objects and call others routines.

    Returns: None

    """
    if on_frame_tasks is None:
        on_frame_tasks = []

    glfw.poll_events()
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    # drawing the model in the screen
    # -------------------------------
    for func in on_frame_tasks:
        func()

    # Once the render is done, buffers are swapped, showing the complete scene.
    glfw.swap_buffers(render_window)


if __name__ == "__main__":
    log.basicConfig(level=log.INFO)

    log.info("Initialization of the application...")
    window = init()

    log.info("Setting up the model...")
    my_model = Model()
    my_model.set_vertices(
        np.array(
            [-0.5, -0.5, 0, 0.5, -0.5, 0, 0.5, 0.5, 0, -0.5, 0.5, 0],
            dtype=np.float32,
        )
    )
    my_model.set_indices(np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32))
    my_model.set_shaders(
        "./shaders/vertex_shader.glsl", "./shaders/fragment_shader.glsl"
    )

    log.info(type(window))

    log.info("Starting main loop of the app...")
    while not glfw.window_should_close(window):
        on_loop([lambda: my_model.draw()])

    glfw.terminate()
