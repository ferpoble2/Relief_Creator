"""
Class in charge of managing the models of the maps in 2 dimensions.
"""

from src.engine.model.model import Model

import OpenGL.GL as GL
import numpy as np
import ctypes as ctypes

from src.engine.settings import FLOAT_BYTES
from src.engine.data import decimation
from src.engine.settings import WIDTH
from src.engine.settings import HEIGHT
from src.input.CTP import read_file
from src.engine.model.tranformations.transformations import ortho
from src.utils import get_logger

log = get_logger(module='Map2DModel')


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

        # Color file used. (if not color file, then None)
        self.__color_file = None
        self.__colors = []
        self.__height_limit = []

        # grid values
        self.__x = None
        self.__y = None
        self.__z = None

        # vertices values (used in the buffer)
        self.__vertices = []

        # indices of the model (used in the buffer)
        self.__indices = []

        # height values
        self.__height = []
        self.__max_height = None
        self.__min_height = None

        # height buffer object
        self.hbo = GL.glGenBuffers(1)

        # projection matrix
        self.__projection = ortho(-180, 180, -90, 90, -1, 1)

    def __print_vertices(self) -> None:
        """
        Print the vertices of the model.
        Returns: None
        """
        print(f"Total Vertices: {len(self.__vertices)}")
        for i in range(int(len(self.__vertices) / 3)):
            print(f"P{i}: " + "".join(str(self.__vertices[i * 3:(i + 1) * 3])))

    def __print_indices(self) -> None:
        """
        Print the indices of the model.
        Returns: None
        """

        for i in range(int(len(self.__indices) / 3)):
            print(f"I{i}: " + "".join(str(self.__indices[i * 3:(i + 1) * 3])))

    def _update_uniforms(self) -> None:
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

        # set colors if using
        if self.__color_file is not None:
            colors_location = GL.glGetUniformLocation(self.shader_program, "colors")
            height_color_location = GL.glGetUniformLocation(self.shader_program, "height_color")
            length_location = GL.glGetUniformLocation(self.shader_program, "length")

            GL.glUniform3fv(colors_location, len(self.__colors), self.__colors)
            GL.glUniform1fv(height_color_location, len(self.__height_limit), self.__height_limit)
            GL.glUniform1i(length_location, len(self.__colors))

    def __set_height_buffer(self) -> None:
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

    def set_color_file(self, filename: str) -> None:
        """

        Args:
            filename: File to use for the colors.

        Returns: None

        """
        log.debug('Setting colors from file')
        if len(self.__vertices) == 0:
            raise AssertionError('Did you forget to set the vertices? (set_vertices_from_grid)')

        # set the shaders
        self.set_shaders('./engine/shaders/model_2d_colors_vertex.glsl',
                         './engine/shaders/model_2d_colors_fragment.glsl')
        self.__color_file = filename

        file_data = read_file(filename)
        colors = []
        height_limit = []

        for element in file_data:
            colors.append(element['color'])
            height_limit.append(element['height'])

        # send error in case too many colors are passed
        if len(colors) > 500:
            raise BufferError('Shader used does not support more than 500 colors in the file.')

        self.__colors = np.array(colors, dtype=np.float32)
        self.__height_limit = np.array(height_limit, dtype=np.float32)

    def set_vertices_from_grid(self, x, y, z, quality=1) -> None:
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

        # Only select this shader if there is no shader selected.
        if self.shader_program is None:
            self.set_shaders(
                "./engine/shaders/model_2d_vertex.glsl", "./engine/shaders/model_2d_fragment.glsl"
            )

        # set the height buffer for rendering and store height values
        self.__height = np.array(z).reshape(-1)
        self.__max_height = np.nanmax(self.__height)
        self.__min_height = np.nanmin(self.__height)

        self.__set_height_buffer()
