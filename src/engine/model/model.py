"""Model class to manage models in the engine."""
import OpenGL.GL as GL
import ctypes as ctypes
import numpy as np
from OpenGL.GL.shaders import compileShader
from src.engine.settings import FLOAT_BYTES


class Model:
    """
    Class that is in charge of managing the models of the engine.

    Open GL variables:
        glVertexAttributePointer 0: Vertices of the model.
    """

    def __init__(self):
        """Contructor of the model class."""
        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        self.ebo = GL.glGenBuffers(1)

        self.shader_program = None

        self.position = np.array([0, 0, 0], dtype=np.float32)
        self.rotation = np.array([0, 0, 0], dtype=np.float32)

        self.indices_size = 0

        self.draw_mode = GL.GL_TRIANGLES

        self.wireframes = False

        self.update_uniform_values = True

    def set_shaders(self, vertex_shader, fragment_shader):
        """Set the shaders to use in the model.

        Set the shaders of the model, compiling them and creating a program.

        Args:
            vertex_shader (str): Path to the vertex shader location.
            fragment_shader (str): Path to the fragment shader location.
        """

        vertex_shader = open(vertex_shader, "r").read()
        fragment_shader = open(fragment_shader, "r").read()

        self.shader_program = GL.OpenGL.GL.shaders.compileProgram(
            compileShader(vertex_shader, GL.GL_VERTEX_SHADER),
            compileShader(fragment_shader, GL.GL_FRAGMENT_SHADER),
        )

    def _update_uniforms(self):
        """
        Method called to updated uniforms in the model.
        Must be implemented in the models.
        Returns: None
        """
        if self.update_uniform_values:
            raise NotImplementedError("Method update_uniform not implemented in the model.")

    def draw(self):
        """Draw the model on the screen using the current configuration."""

        if self.wireframes:
            GL.glPolygonMode(GL.GL_FRONT, GL.GL_LINE)
            GL.glPolygonMode(GL.GL_BACK, GL.GL_LINE)

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

    def set_vertices(self, vertex):
        """Set the vertices buffers inside the model.

        Args:
            vertex (numpy.ndarray): List of vertices of type np.float32.
        """

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            len(vertex) * FLOAT_BYTES,
            vertex,
            GL.GL_STATIC_DRAW,
        )

        GL.glVertexAttribPointer(
            0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0)
        )
        GL.glEnableVertexAttribArray(0)

    def set_indices(self, indices):
        """Set the vertex indices of the vertices of the model.

        Args:
            indices (numpy.ndarray): Indices to be used in the draw process.
        """

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(
            GL.GL_ELEMENT_ARRAY_BUFFER,
            len(indices) * FLOAT_BYTES,
            indices,
            GL.GL_STATIC_DRAW,
        )

        self.indices_size = len(indices)

    def __str__(self):
        """Return the string representing the model object.

        Returns:
            str: String representing the object.
        """

        return f"Model with vao={self.vao}."
