"""
File with the class Lines, class in charge of storing all the information related to the models that draw lines on
the scene.
"""

from src.engine.scene.model.model import Model
from src.utils import get_logger

import numpy as np
import OpenGL.GL as GL

log = get_logger(module="LINES")


class Lines(Model):
    """
    Class in charge of the modeling and drawing lines in the engine.
    """

    def __init__(self, scene):
        """
        Constructor of the class
        """
        super().__init__(scene)

        self.draw_mode = GL.GL_LINES

        self.update_uniform_values = True

        self.__vertex_shader_file = './engine/shaders/lines_vertex.glsl'
        self.__fragment_shader_file = './engine/shaders/lines_fragment.glsl'

        self.__point_list = []
        self.__indices_list = []

        self.__line_color = (1, 1, 0, 1)
        self.__border_color = (0, 0, 0, 1)
        self.__use_border = False

        self.set_shaders(self.__vertex_shader_file, self.__fragment_shader_file)

    def _update_uniforms(self) -> None:
        """
        Update the uniforms values for the model.

        Returns: None
        """

        # update values for the polygon shader
        # ------------------------------------
        projection_location = GL.glGetUniformLocation(self.shader_program, "projection")
        polygon_color_location = GL.glGetUniformLocation(self.shader_program, "lines_color")

        # set the color and projection matrix to use
        # ------------------------------------------
        GL.glUniform4f(polygon_color_location,
                       self.__line_color[0],
                       self.__line_color[1],
                       self.__line_color[2],
                       self.__line_color[3])
        GL.glUniformMatrix4fv(projection_location, 1, GL.GL_TRUE, self.scene.get_active_model_projection_matrix())

    def add_line(self, first_point: tuple, second_point: tuple):
        """
        Add a new line to the model.

        Args:
            first_point: (x,y,z) tuple with the coordinates of the point
            second_point: (x,y,z) tuple with the coordinates of the point

        Returns: None
        """

        # first point
        self.__point_list.append(first_point[0])
        self.__point_list.append(first_point[1])
        self.__point_list.append(first_point[2])

        # second point
        self.__point_list.append(second_point[0])
        self.__point_list.append(second_point[1])
        self.__point_list.append(second_point[2])

        self.set_vertices(np.array(self.__point_list, dtype=np.float32))

        # add the index to the model
        self.__indices_list.append(self.get_number_of_points() - 2)
        self.__indices_list.append(self.get_number_of_points() - 1)
        self.set_indices(np.array(self.__indices_list, dtype=np.uint32))

    def get_number_of_points(self) -> int:
        """
        Get the number of points in the model.

        Returns: Number of points in the model.
        """
        return int(len(self.__point_list) / 3)

    def draw(self) -> None:
        """
        Draw the points on the scene

        Returns: None
        """

        # draw if there is at least one line to draw
        if len(self.__point_list) / 3 > 1:
            render_settings = self.scene.get_render_settings()
            line_width = render_settings["LINE_WIDTH"]
            polygon_line_width = render_settings["POLYGON_LINE_WIDTH"]
            active_polygon_line_width = render_settings["ACTIVE_POLYGON_LINE_WIDTH"]

            if self.__use_border:
                # store the old color
                old_color = self.__line_color

                # change the color and width of the line to draw
                self.__line_color = self.__border_color
                GL.glLineWidth(active_polygon_line_width)
                super().draw()

                # return the original color
                self.__line_color = old_color

            GL.glLineWidth(polygon_line_width)
            super().draw()
            GL.glLineWidth(line_width)

    def set_use_borders(self, value: bool) -> None:
        """
        Set if use borders or not

        Args:
            value: Boolean indicating if use borders or not

        Returns: None

        """
        self.__use_border = value

    def remove_last_added_line(self) -> None:
        """
        Remove the last added line.

        Returns: None
        """

        # do something only if there is at least one line
        if len(self.__point_list) > 5:
            # remove the points
            self.__point_list.pop()
            self.__point_list.pop()
            self.__point_list.pop()
            self.__point_list.pop()
            self.__point_list.pop()
            self.__point_list.pop()
            self.set_vertices(np.array(self.__point_list, dtype=np.float32))

            # remove the indices
            self.__indices_list.pop()
            self.__indices_list.pop()
            self.set_indices(np.array(self.__indices_list, dtype=np.uint32))

    def set_line_color(self, color: list) -> None:
        """
        Set the line color to draw.

        Args:
            color: Color in RGBA format.

        Returns: None
        """
        self.__line_color = (color[0], color[1], color[2], color[3])

    def set_border_color(self, color: list) -> None:
        """
        Set the color of the border of the line.

        Args:
            color: new color to use as border.

        Returns: None
        """
        self.__border_color = (color[0], color[1], color[2], color[3])

    def get_line_color(self) -> tuple:
        """
        Get the color of the lines.

        Returns: Color of the line
        """
        return self.__line_color

    def get_border_color(self) -> tuple:
        """
        Get the color of the border.

        Returns: Color of the border
        """

        return self.__border_color
