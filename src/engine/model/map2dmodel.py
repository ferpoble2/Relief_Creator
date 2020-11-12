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
from src.engine.data import decimation
from src.engine.settings import WIDTH
from src.engine.settings import HEIGHT
from src.engine.model.tranformations.transformations import ortho

class Map2DModel(Model):
    """
    Class that manage all things related to the 2D representation of the maps.

    Open GL variables:
        glVertexAttributePointer 1: Heights of the vertices.

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

        # indices of the model
        self.__indices = []

        # height values
        self.__height = []
        self.__max_height = None
        self.__min_height = None

        # heigh buffer object
        self.hbo = GL.glGenBuffers(1)

        # projection matriz
        self.__projection = ortho(-180, 180, -90, 90, -1, 1)

    def __print_vertices(self):
        """
        Print the vertices of the model.
        Returns: None
        """
        print(f"Total Vertices: {len(self.__vertices)}")
        for i in range(int(len(self.__vertices) / 3)):
            print(f"P{i}: " + "".join(str(self.__vertices[i * 3:(i + 1) * 3])))

    def __print_indices(self):
        """
        Print the indices of the model.
        Returns: None
        """

        for i in range(int(len(self.__indices) / 3)):
            print(f"I{i}: " + "".join(str(self.__indices[i * 3:(i + 1) * 3])))

    def update_uniforms(self):
        """
        Update the uniforms in the model.

        Set the maximum and minimum height of the vertices.
        Returns: None
        """
        # get the location
        max_height_location = GL.glGetUniformLocation(self.shader_program, "max_height")
        min_height_location = GL.glGetUniformLocation(self.shader_program, "min_height")
        projection_location = GL.glGetUniformLocation(self.shader_program, "projection")

        # set the value
        GL.glUniform1f(max_height_location, float(self.__max_height))
        GL.glUniform1f(min_height_location, float(self.__min_height))
        GL.glUniformMatrix4fv(projection_location, 1, GL.GL_TRUE, self.__projection)

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

    def set_vertices_from_grid(self, x, y, z, quality=1):
        """
        Set the vertices of the model from a grid.

        This method:
         - Store in the class variables the original values of the grid loaded.
         - Set the vertices of the model after applying a decimation algorithm over them to reduce the number
           of vertices to render.
         - Set the height buffer with the height of the vertices.

        Args:
            quality: Quality of the grid to render. 1 for max quality, 2 or more for less quality.
            x: X values of the grid to use.
            y: Y values of the grid.
            z: Z values of the grid.

        Returns: None

        """

        # store the data for future operations.
        self.__x = x
        self.__y = y
        self.__z = z

        # Apply decimation algorithm
        x, y, z = decimation.simple_decimation(x, y, z, int(HEIGHT / quality), int(WIDTH / quality))

        # Set the vertices in the buffer
        for row_index in range(len(z)):
            for col_index in range(len(z[0])):
                self.__vertices.append(x[col_index])
                self.__vertices.append(y[row_index])
                self.__vertices.append(0)

        self.set_vertices(
            np.array(
                self.__vertices,
                dtype=np.float32,
            )
        )

        # Set the indices in the model buffers
        for row_index in range(len(z)):
            for col_index in range(len(z[0])):

                # first triangles
                if col_index < len(z[0]) - 1 and row_index < len(z) - 1:
                    self.__indices.append(row_index * len(z[0]) + col_index)
                    self.__indices.append(row_index * len(z[0]) + col_index + 1)
                    self.__indices.append((row_index + 1) * len(z[0]) + col_index)

                # seconds triangles
                if col_index > 0 and row_index > 0:
                    self.__indices.append(row_index * len(z[0]) + col_index)
                    self.__indices.append((row_index - 1) * len(z[0]) + col_index)
                    self.__indices.append(row_index * len(z[0]) + col_index - 1)

        self.set_indices(np.array(self.__indices, dtype=np.uint32))
        self.set_shaders(
            "../shaders/vertex_shader.glsl", "../shaders/fragment_shader.glsl"
        )

        # set the height buffer for rendering and store height values
        self.__height = np.array(z).reshape(-1)
        self.__max_height = np.nanmax(self.__height)
        self.__min_height = np.nanmin(self.__height)

        self.set_heigh_buffer()


if __name__ == '__main__':
    log.basicConfig(format="%(asctime)s - %(message)s", level=log.DEBUG)

    filename = "../../input/test_inputs/IF_60Ma_AHS_ET.nc"
    X, Y, Z = read_info(filename)

    log.debug("Creating windows.")
    window = init("Relief Creator")

    log.debug("Reading information from file.")
    model = Map2DModel()

    log.debug("Setting vertices from grid")
    model.set_vertices_from_grid(X, Y, Z, 1)
    model.wireframes = False

    log.debug("Starting main loop.")
    while not glfw.window_should_close(window):
        on_loop(window, [lambda: model.draw()])

    glfw.terminate()
