"""
Class in charge of managing the models of the maps in 2 dimentions.
"""

from src.engine.model.model import Model
from src.input.NetCDF import read_info

import OpenGL.GL as GL
import logging as log
import glfw
import numpy as np

from src.engine.render import init
from src.engine.render import on_loop


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

        min_x = np.min(self.__x)
        max_x = np.max(self.__x)

        min_y = np.min(self.__y)
        max_y = np.max(self.__y)

        for row_index in range(len(self.__z)):
            for col_index in range(len(self.__z[0])):
                new_x = interpolate(self.__x[col_index], min_x, max_x)
                new_y = interpolate(self.__y[row_index], min_y, max_y)
                self.__vertices.append(new_x)
                self.__vertices.append(new_y)
                self.__vertices.append(0)

        # Set the vertices in the buffer
        self.set_vertices(
            np.array(
                self.__vertices,
                dtype=np.float32,
            )
        )

        indices = []
        # TODO: Hacer los indices de forma correcta para las triangulaciones.
        for a in range(len(self.__vertices)):
            indices.append(a)

        self.set_indices(np.array(indices, dtype=np.uint32))
        self.set_shaders(
            "../shaders/vertex_shader.glsl", "../shaders/fragment_shader.glsl"
        )


if __name__ == '__main__':
    log.basicConfig(format="%(asctime)s - %(message)s", level=log.DEBUG)

    filename = "../../input/test_inputs/IF_60Ma_AHS_ET.nc"
    X, Y, Z = read_info(filename)

    log.debug("Creating windows.")
    window = init("Relief Creator")

    log.debug("Reading information from file.")
    model = Map2DModel()
    model.set_vertices_from_grid(X, Y, Z)

    log.debug("Starting main loop.")
    while not glfw.window_should_close(window):
        on_loop(window, [lambda: model.draw()])

    glfw.terminate()
