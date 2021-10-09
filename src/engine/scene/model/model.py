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

"""Model class to manage models in the engine."""
import ctypes as ctypes

import OpenGL.GL as GL
import numpy as np
from OpenGL.GL.shaders import compileShader


class Model:
    """
    Class that is in charge of managing the models of the engine.

    Open GL variables:
        glVertexAttributePointer 0: Vertices of the model.
    """

    def __init__(self, scene):
        """Constructor of the model class.

        IMPORTANT: The model is not added to the scene! too add it is necessary to call scene.add_model(model).

        Args:
            scene: Scene object to use to communicate with the engine.
        """
        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        self.ebo = GL.glGenBuffers(1)

        self.shader_program = None

        self.position = np.array([0, 0, 0], dtype=np.float32)
        self.rotation = np.array([0, 0, 0], dtype=np.float32)

        self.indices_size = 0

        self.polygon_mode = GL.GL_FILL
        self.draw_mode = GL.GL_TRIANGLES

        self.update_uniform_values = True

        self.id = ""

        self.scene = scene

        # auxiliary variables
        # -------------------
        self.__vertices_array = np.array([])
        self.__indices_array = np.array([])

    def __str__(self) -> str:
        """Return the string representing the model object.

        Returns:
            str: String representing the object.
        """

        return f"Model with vao={self.vao}."

    def _update_uniforms(self) -> None:
        """
        Method called to updated uniforms in the model.
        Must be implemented in the models.
        Returns: None
        """
        if self.update_uniform_values:
            raise NotImplementedError("Method update_uniform not implemented in the model.")

    def draw(self) -> None:
        """Draw the model on the screen using the current configuration."""

        GL.glPolygonMode(GL.GL_FRONT, self.polygon_mode)
        GL.glPolygonMode(GL.GL_BACK, self.polygon_mode)

        # select the shader to use
        GL.glUseProgram(self.shader_program)

        # update the uniforms information
        self._update_uniforms()

        # Binding the proper buffers
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        # Render the active element buffer with the active shader program
        GL.glDrawElements(
            self.draw_mode, self.indices_size, GL.GL_UNSIGNED_INT, None
        )

        GL.glPolygonMode(GL.GL_FRONT, GL.GL_FILL)
        GL.glPolygonMode(GL.GL_BACK, GL.GL_FILL)

    def get_indices_array(self) -> np.ndarray:
        """
        Get the array of indices currently being used in the model.

        Returns: Numpy array with the elements currently being used in the model.
        """
        return self.__indices_array

    def get_vertices_array(self) -> np.ndarray:
        """
        Get the array of vertices currently being used in the model.

        Returns: Numpy array with the elements currently being used in the model.
        """
        return self.__vertices_array

    def set_indices(self, indices: np.ndarray) -> None:
        """Set the vertex indices of the vertices of the model.

        Args:
            indices: Indices to be used in the draw process.
        """

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(
            GL.GL_ELEMENT_ARRAY_BUFFER,
            len(indices) * self.scene.get_float_bytes(),
            indices.astype(np.uint32),
            GL.GL_STATIC_DRAW,
        )

        self.__indices_array = indices
        self.indices_size = len(indices)

    def set_shaders(self, vertex_shader: str, fragment_shader: str) -> None:
        """Set the shaders to use in the model.

        Set the shaders of the model, compiling them and creating a program.

        Args:
            vertex_shader: Path to the vertex shader location.
            fragment_shader: Path to the fragment shader location.
        """

        vertex_shader = open(vertex_shader, "r").read()
        fragment_shader = open(fragment_shader, "r").read()

        self.shader_program = GL.OpenGL.GL.shaders.compileProgram(
            compileShader(vertex_shader, GL.GL_VERTEX_SHADER),
            compileShader(fragment_shader, GL.GL_FRAGMENT_SHADER),
        )

    def set_vertices(self, vertex: np.ndarray) -> None:
        """Set the vertices buffers inside the model.

        Args:
            vertex: List of vertices of type np.float32.
        """
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            len(vertex) * self.scene.get_float_bytes(),
            vertex.astype(np.float32),
            GL.GL_STATIC_DRAW,
        )

        GL.glVertexAttribPointer(
            0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0)
        )
        GL.glEnableVertexAttribArray(0)

        self.__vertices_array = vertex
