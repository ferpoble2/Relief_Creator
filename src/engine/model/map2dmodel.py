"""
Class in charge of managing the models of the maps in 2 dimentions.
"""

from src.engine.model.model import Model
from src.input.NetCDF import read_info

import OpenGL.GL as GL
import logging as log
import glfw
import numpy as np
import ctypes as ctypes

from src.engine.render import init
from src.engine.render import on_loop
from src.engine.settings import FLOAT_BYTES


def interpolate(value: float, value_min: float, value_max: float, target_min: float = -1,
                target_max: float = 1):
    """

    Args:
        value: Value to interpolate.
        value_min: Minimum value of the values.
        value_max: Maximum value of the values.
        target_min: Minimum value of the interpolation interval.
        target_max: Maximum value of the interpolation interval.

    Returns: Interpolated value.

    """
    return (float(value) - value_min) * (float(target_max) - target_min) / (float(value_max) - value_min) + target_min


class Map2DModel(Model):
    """
    Class that manage all things related to the 2D representation of the maps.
    """

    def __init__(self):
        """
        Constructor of the model class.
        """
        super().__init__()

        # grid values
        self.__x = None
        self.__y = None
        self.__z = None

        # vertices values
        self.__vertices = []

        # height values
        self.__height = []

        # heigh buffer object
        self.hbo = GL.glGenBuffers(1)

    def set_heigh_buffer(self):
        """
        Set the buffer object for the heights to be used in the shaders.

        IMPORTANT:
            Uses the index 1 of the attributes pointers.

        Returns: None

        """
        height = np.array(self.__height, dtype=np.float32)

        # Set the buffer data in the buffer
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.hbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        len(height) * FLOAT_BYTES,
                        height,
                        GL.GL_STATIC_DRAW)

        # Enable the data to the shaders
        GL.glVertexAttribPointer(1, 1, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(1)

        return


    def set_vertices_from_grid(self, x, y, z):
        """
        Set the vertices of the model from a grid.

        Args:
            x: X values of the grid to use.
            y: Y values of the grid.
            z: Z values of the grid.

        Returns: None

        """

        # store the data for future operations.
        self.__x = x
        self.__y = y
        self.__z = z

        # TODO: apply the decimation algoritm here.

        min_x = np.min(x)
        max_x = np.max(x)

        min_y = np.min(y)
        max_y = np.max(y)

        # Set the vertices in the buffer
        for row_index in range(len(z)):
            for col_index in range(len(z[0])):
                new_x = interpolate(x[col_index], min_x, max_x)
                new_y = interpolate(y[row_index], min_y, max_y)
                self.__vertices.append(new_x)
                self.__vertices.append(new_y)
                self.__vertices.append(0)

        self.set_vertices(
            np.array(
                self.__vertices,
                dtype=np.float32,
            )
        )

        # Set the indices in the model buffers
        indices = []
        for row_index in range(len(z)):
            for col_index in range(len(z[0])):

                # first triangles
                if col_index < len(z[0]) - 1 and row_index < len(z) - 1:
                    indices.append(row_index * len(z) + col_index)
                    indices.append(row_index * len(z) + col_index + 1)
                    indices.append((row_index + 1) * len(z) + col_index)

                # seconds triangles
                if col_index > 0 and row_index > 0:
                    indices.append(row_index * len(z) + col_index)
                    indices.append((row_index - 1) * len(z) + col_index)
                    indices.append(row_index * len(z) + col_index - 1)

        self.set_indices(np.array(indices, dtype=np.uint32))
        self.set_shaders(
            "../shaders/vertex_shader.glsl", "../shaders/fragment_shader.glsl"
        )

        # set the height buffer for rendering
        self.__height = np.array(z).reshape(-1)
        self.set_heigh_buffer()


if __name__ == '__main__':
    log.basicConfig(format="%(asctime)s - %(message)s", level=log.DEBUG)

    filename = "../../input/test_inputs/IF_60Ma_AHS_ET.nc"
    X, Y, Z = read_info(filename)

    log.debug("Creating windows.")
    window = init("Relief Creator")

    log.debug("Reading information from file.")
    model = Map2DModel()
    model.set_vertices_from_grid(X[:50], Y[:50], Z[:50, :50])
    model.wireframes = True

    log.debug("Starting main loop.")
    while not glfw.window_should_close(window):
        on_loop(window, [lambda: model.draw()])

    glfw.terminate()
