"""
File with the class Plane, class in charge of rendering a plane on the scene.
"""

from src.engine.scene.model.model import Model
from src.utils import get_logger

import numpy as np
import OpenGL.GL as GL

log = get_logger(module="PLANE")


class Plane(Model):
    """
    Class in charge of the modeling and drawing lines in the engine.
    """

    def __init__(self, scene):
        """
        Constructor of the class
        """
        super().__init__(scene)

        self.draw_mode = GL.GL_TRIANGLES

        self.update_uniform_values = True

        self.__vertex_shader_file = './src/engine/shaders/plane_vertex.glsl'
        self.__fragment_shader_file = './src/engine/shaders/plane_fragment.glsl'

        self.__vertices_list = np.array([])
        self.__indices_list = np.array([])

        self.__plane_color = (1, 0, 0, 0.3)

        self.set_shaders(self.__vertex_shader_file, self.__fragment_shader_file)

    def set_plane_color(self, new_color: tuple) -> None:
        """
        Change the color of the plane.

        Args:
            new_color: New color to use in the plane. (R,G,B,A)

        Returns: None
        """
        self.__plane_color = new_color

    def _update_uniforms(self) -> None:
        """
        Update the uniforms values for the model.

        Returns: None
        """

        # update values for the polygon shader
        # ------------------------------------
        projection_location = GL.glGetUniformLocation(self.shader_program, "projection")
        plane_color_location = GL.glGetUniformLocation(self.shader_program, "plane_color")

        # set the color and projection matrix to use
        # ------------------------------------------
        GL.glUniform4f(plane_color_location,
                       self.__plane_color[0],
                       self.__plane_color[1],
                       self.__plane_color[2],
                       self.__plane_color[3])
        GL.glUniformMatrix4fv(projection_location, 1, GL.GL_TRUE, self.scene.get_active_model_projection_matrix())

    def set_triangles(self, vertices: np.ndarray) -> None:
        """
        Set the triangles to be drawn in the plane.

        Args:
            vertices: Vertices to be draw on the model.

        Returns: None
        """
        self.__vertices_list = vertices
        num_vertices = int(len(self.__vertices_list) / 3)
        self.__indices_list = np.array(range(0, num_vertices))

        # reset the buffers
        self.set_vertices(self.__vertices_list.astype(dtype=np.float32))
        self.set_indices(self.__indices_list.astype(dtype=np.uint32))

    def draw(self) -> None:
        """
        Draw the model on the scene.

        Returns: None
        """
        super().draw()
